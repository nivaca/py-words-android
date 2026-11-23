// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
// This file is part of py-words for Android. See the LICENSE file for details.

// La única pantalla de la app: py-words en un WebView, de una de dos fuentes.
// Por omisión, el teléfono: el programa corre en la app (véase LocalServer) y
// no necesita internet.  En los ajustes se puede pedir en su lugar la página
// web, el sitio py-words.uniandes.edu.co.
// Todo lo demás (la búsqueda, los resultados, los ajustes) lo hace py-words;
// la app le da una ventana, abre fuera los enlaces a otros sitios y recibe
// las palabras que le mandan otras apps.

package io.github.nivaca.pywords

import android.annotation.SuppressLint
import android.app.Activity
import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowInsets
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.ImageButton
import android.widget.PopupMenu
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import android.window.OnBackInvokedCallback
import android.window.OnBackInvokedDispatcher
import java.net.URLEncoder

class MainActivity : Activity() {
    private enum class Source { ONLINE, PHONE }

    private lateinit var web: WebView
    private lateinit var progress: ProgressBar
    private lateinit var loading: View
    private lateinit var error: View
    private lateinit var sourceLabel: TextView

    private val prefs by lazy { getSharedPreferences("settings", Context.MODE_PRIVATE) }

    private var source = Source.PHONE
    private var base: String? = null        // null while py-words starts on the phone
    private var pending: String? = null     // path and query to open once it has
    private var failedUrl: String? = null    // the page that could not be loaded
    private var failed = false
    private var forgetHistory = false       // after a change of source
    private var backCallback: OnBackInvokedCallback? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        web = findViewById(R.id.web)
        progress = findViewById(R.id.progress)
        loading = findViewById(R.id.loading)
        error = findViewById(R.id.error)
        sourceLabel = findViewById(R.id.source)

        // Since Android 15 the window fills the whole screen: keep the page
        // clear of the system bars and of the keyboard.  (Android 10 does not
        // do this, and lacks the calls.)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            findViewById<View>(R.id.root).setOnApplyWindowInsetsListener { v, insets ->
                val bars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.ime())
                v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
                WindowInsets.CONSUMED
            }
        }

        setUpWebView()
        findViewById<Button>(R.id.retry).setOnClickListener { retry() }
        findViewById<Button>(R.id.use_phone).setOnClickListener { switchTo(Source.PHONE) }
        findViewById<ImageButton>(R.id.menu).setOnClickListener { showMenu(it) }

        // Por omisión, el teléfono: funciona sin internet.  Solo quien eligió
        // la fuente en línea la conserva.
        source = if (prefs.getString(PREF_SOURCE, null) == "online") Source.ONLINE else Source.PHONE
        // Tras girar la pantalla, la misma página y el mismo historial; si
        // no, lo que pida otra app, o la portada.
        if (savedInstanceState == null) pending = pathFor(intent)
        begin(savedInstanceState)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        pathFor(intent)?.let { go(it) }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        if (base != null) {
            web.saveState(outState)
            outState.putString(STATE_BASE, base)
        }
    }

    override fun onPause() {
        // Los ajustes de py-words viven en una galleta: que llegue al disco.
        CookieManager.getInstance().flush()
        web.onPause()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        web.onResume()
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    // ---- the two sources ----------------------------------------------------- //

    /** Opens the current source, restoring SAVED if it was the same one. */
    private fun begin(saved: Bundle?) {
        error.visibility = View.GONE
        // Si se cambia de fuente mientras el teléfono aún carga, la capa de
        // carga no debe quedarse encima de la página web.
        loading.visibility = View.GONE
        updateLabel()
        when (source) {
            Source.ONLINE -> ready(ONLINE, saved)
            Source.PHONE -> {
                base = null
                loading.visibility = View.VISIBLE
                LocalServer.start(this) { result ->
                    if (source != Source.PHONE || isDestroyed) return@start
                    loading.visibility = View.GONE
                    result.onSuccess { port -> ready("http://127.0.0.1:$port", saved) }
                        .onFailure { showError(getString(R.string.phone_error), it.message ?: "", phone = false) }
                }
            }
        }
    }

    private fun ready(url: String, saved: Bundle?) {
        base = url
        updateLabel()
        // El estado guardado solo vale para el mismo servidor (el puerto
        // del teléfono cambia cada vez que Android cierra la app).
        val restored = saved != null && saved.getString(STATE_BASE) == url &&
            web.restoreState(saved) != null
        if (!restored) load(url + (pending ?: "/"))
        pending = null
        updateBack()
    }

    private fun switchTo(next: Source) {
        if (next == source && base != null) return
        // La misma página en la otra fuente: una búsqueda sigue siendo la misma.
        pending = currentPath()
        source = next
        prefs.edit().putString(PREF_SOURCE, if (next == Source.PHONE) "phone" else "online").apply()
        web.stopLoading()
        forgetHistory = true
        begin(null)
    }

    /** The path and query of the page shown, if it is a page of py-words. */
    private fun currentPath(): String {
        val uri = web.url?.let { Uri.parse(it) } ?: return "/"
        if (!isOurs(uri) || uri.encodedPath != "/") return "/"
        return "/" + (uri.encodedQuery?.let { "?$it" } ?: "")
    }

    private fun updateLabel() {
        sourceLabel.text = when (source) {
            Source.ONLINE -> getString(R.string.source_online)
            Source.PHONE -> LocalServer.version?.let { getString(R.string.source_phone, it) }
                ?: getString(R.string.source_phone_short)
        }
    }

    // El menú ya no elige la fuente: el teléfono es la de siempre, y la
    // página web queda en los ajustes, para quien la quiera.
    private fun showMenu(anchor: View) {
        val menu = PopupMenu(this, anchor)
        menu.menu.add(0, MENU_RELOAD, 0, R.string.menu_reload)
        if (source == Source.ONLINE) menu.menu.add(0, MENU_BROWSER, 1, R.string.menu_browser)
        menu.menu.add(0, MENU_SETTINGS, 2, R.string.menu_settings)
        menu.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                MENU_RELOAD -> if (base == null) retry() else { error.visibility = View.GONE; web.reload() }
                MENU_BROWSER -> openOutside(Uri.parse(web.url ?: ONLINE))
                MENU_SETTINGS -> showSettings()
            }
            true
        }
        menu.show()
    }

    /** The settings of the app (py-words keeps its own on its page). */
    private fun showSettings() {
        val checked = booleanArrayOf(source == Source.ONLINE)
        AlertDialog.Builder(this)
            .setTitle(R.string.settings)
            .setMultiChoiceItems(arrayOf(getString(R.string.setting_online)), checked) { _, _, on ->
                checked[0] = on
            }
            .setPositiveButton(android.R.string.ok) { _, _ ->
                switchTo(if (checked[0]) Source.ONLINE else Source.PHONE)
            }
            .setNegativeButton(android.R.string.cancel, null)
            .show()
    }

    // ---- words from other apps ----------------------------------------------- //

    /** The path to open for a word or a link from another app, or null. */
    private fun pathFor(intent: Intent?): String? {
        val text = when (intent?.action) {
            Intent.ACTION_PROCESS_TEXT -> intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString()
            Intent.ACTION_SEND -> intent.getStringExtra(Intent.EXTRA_TEXT)
            Intent.ACTION_VIEW -> {
                // A link to the site opens in the source chosen, whichever it is.
                val uri = intent.data ?: return null
                if (uri.scheme != "https" || !uri.host.equals(HOST, ignoreCase = true)) return null
                return "/" + (uri.encodedQuery?.let { "?$it" } ?: "")
            }
            else -> null
        }
        val query = text?.trim()?.takeIf { it.isNotEmpty() && it.length <= MAX_QUERY } ?: return null
        return "/?q=" + URLEncoder.encode(query, "UTF-8")
    }

    /** Opens PATH now, or as soon as py-words has started. */
    private fun go(path: String) {
        val b = base
        if (b == null) pending = path else load(b + path)
    }

    private fun load(url: String) {
        error.visibility = View.GONE
        web.loadUrl(url)
    }

    private fun retry() {
        if (base == null) begin(null) else load(failedUrl ?: (base + "/"))
    }

    private fun showError(title: String, detail: String, phone: Boolean) {
        findViewById<TextView>(R.id.error_title).text = title
        findViewById<TextView>(R.id.error_detail).text = detail
        findViewById<View>(R.id.use_phone).visibility = if (phone) View.VISIBLE else View.GONE
        error.visibility = View.VISIBLE
    }

    // ---- el WebView ---------------------------------------------------------- //

    @SuppressLint("SetJavaScriptEnabled")
    private fun setUpWebView() {
        web.settings.apply {
            javaScriptEnabled = true          // py-words' own scripts (with a CSP nonce)
            domStorageEnabled = true
            builtInZoomControls = true
            displayZoomControls = false
            allowFileAccess = false
            allowContentAccess = false
            userAgentString = "$userAgentString py-words-android/${appVersion()}"
        }
        CookieManager.getInstance().setAcceptCookie(true)

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                // Las páginas de py-words se quedan en la app; los demás
                // enlaces (GitHub, la página del autor, Logeion) van a otra app.
                if (isOurs(request.url)) return false
                openOutside(request.url)
                return true
            }

            override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                failed = false
                progress.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView, url: String) {
                progress.visibility = View.GONE
                if (!failed) error.visibility = View.GONE
                if (forgetHistory) {
                    // Volver no debe saltar a la otra fuente.
                    forgetHistory = false
                    web.clearHistory()
                    updateBack()
                }
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, err: WebResourceError) {
                // Only the page itself counts; a missing image does not.
                if (!request.isForMainFrame) return
                failed = true
                failedUrl = request.url.toString()
                if (source == Source.ONLINE) {
                    showError(getString(R.string.network_error), getString(R.string.network_error_detail), phone = true)
                } else {
                    showError(getString(R.string.phone_error), err.description.toString(), phone = false)
                }
            }

            override fun doUpdateVisitedHistory(view: WebView, url: String, isReload: Boolean) {
                updateBack()
            }
        }

        web.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) {
                progress.isIndeterminate = false
                progress.progress = newProgress
            }
        }

        // py-words no ofrece descargas; si alguna vez lo hace, que las haga
        // el navegador.
        web.setDownloadListener { url, _, _, _, _ -> openOutside(Uri.parse(url)) }
    }

    private fun isOurs(uri: Uri): Boolean {
        val b = base ?: return false
        return "${uri.scheme}://${uri.authority}".equals(b, ignoreCase = true)
    }

    private fun openOutside(uri: Uri) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE))
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(this, R.string.no_browser, Toast.LENGTH_SHORT).show()
        }
    }

    // ---- the back gesture ---------------------------------------------------- //

    // Desde Android 13 el gesto de volver se pide de antemano: la app lo toma
    // solo mientras el WebView tenga adónde volver; si no, la app se cierra
    // con la animación del sistema.
    private fun updateBack() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return
        val wanted = web.canGoBack()
        val dispatcher = onBackInvokedDispatcher
        if (wanted && backCallback == null) {
            val callback = OnBackInvokedCallback { goBack() }
            dispatcher.registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, callback)
            backCallback = callback
        } else if (!wanted && backCallback != null) {
            dispatcher.unregisterOnBackInvokedCallback(backCallback!!)
            backCallback = null
        }
    }

    private fun goBack() {
        error.visibility = View.GONE
        web.goBack()
    }

    // Antes de Android 13; desde entonces lo hace updateBack().
    @SuppressLint("GestureBackNavigation")
    @Deprecated("Replaced by OnBackInvokedCallback from Android 13 on")
    override fun onBackPressed() {
        if (web.canGoBack()) goBack() else @Suppress("DEPRECATION") super.onBackPressed()
    }

    private fun appVersion(): String =
        packageManager.getPackageInfo(packageName, 0).versionName ?: "?"

    companion object {
        const val HOST = "py-words.uniandes.edu.co"
        const val ONLINE = "https://$HOST"
        // Un texto más largo no es una búsqueda sino un párrafo pegado por error.
        const val MAX_QUERY = 500
        private const val PREF_SOURCE = "source"
        private const val STATE_BASE = "base"
        private const val MENU_RELOAD = 1
        private const val MENU_BROWSER = 2
        private const val MENU_SETTINGS = 3
    }
}
