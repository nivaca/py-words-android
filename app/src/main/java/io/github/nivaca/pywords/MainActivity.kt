// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
// This file is part of py-words for Android. See the LICENSE file for details.

// La única pantalla de la app: el sitio de py-words en un WebView.  Todo lo
// demás (la búsqueda, los resultados, los ajustes) lo hace el sitio; la app
// solo le da una ventana, abre fuera los enlaces a otros sitios y recibe las
// palabras que le mandan otras apps.

package io.github.nivaca.pywords

import android.annotation.SuppressLint
import android.app.Activity
import android.content.ActivityNotFoundException
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
import android.widget.ProgressBar
import android.widget.Toast
import android.window.OnBackInvokedCallback
import android.window.OnBackInvokedDispatcher
import java.net.URLEncoder

class MainActivity : Activity() {
    private lateinit var web: WebView
    private lateinit var progress: ProgressBar
    private lateinit var error: View

    private var failedUrl: String? = null   // la página que no se pudo cargar
    private var failed = false
    private var backCallback: OnBackInvokedCallback? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        web = findViewById(R.id.web)
        progress = findViewById(R.id.progress)
        error = findViewById(R.id.error)

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

        // Tras girar la pantalla o volver de segundo plano, la misma página
        // y el mismo historial; si no, lo que pida otra app, o la portada.
        if (savedInstanceState == null || web.restoreState(savedInstanceState) == null) {
            if (!handleIntent(intent)) web.loadUrl(HOME)
        }
        updateBack()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onPause() {
        // Los ajustes del sitio viven en una galleta: que llegue al disco.
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

    /** A word or a link from another app; false if there is none. */
    private fun handleIntent(intent: Intent?): Boolean {
        when (intent?.action) {
            Intent.ACTION_PROCESS_TEXT ->
                return lookUp(intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)?.toString())
            Intent.ACTION_SEND ->
                return lookUp(intent.getStringExtra(Intent.EXTRA_TEXT))
            Intent.ACTION_VIEW -> {
                val uri = intent.data ?: return false
                if (!isOurs(uri)) return false
                load(uri.toString())
                return true
            }
        }
        return false
    }

    /** Busca en el sitio el texto que llegó de otra app. */
    private fun lookUp(text: String?): Boolean {
        val query = text?.trim()?.takeIf { it.isNotEmpty() && it.length <= MAX_QUERY } ?: return false
        load(HOME + "?q=" + URLEncoder.encode(query, "UTF-8"))
        return true
    }

    private fun load(url: String) {
        error.visibility = View.GONE
        web.loadUrl(url)
    }

    private fun retry() {
        load(failedUrl ?: HOME)
    }

    // ---- el WebView ---------------------------------------------------------- //

    @SuppressLint("SetJavaScriptEnabled")
    private fun setUpWebView() {
        web.settings.apply {
            javaScriptEnabled = true          // the site's own scripts (with a CSP nonce)
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
                // Las páginas del sitio se quedan en la app; los demás enlaces
                // (GitHub, la página del autor, el correo) van a otra app.
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
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, err: WebResourceError) {
                // Only the page itself counts; a missing image does not.
                if (!request.isForMainFrame) return
                failed = true
                failedUrl = request.url.toString()
                error.visibility = View.VISIBLE
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

        // El sitio no ofrece descargas; si alguna vez lo hace, que las haga
        // el navegador.
        web.setDownloadListener { url, _, _, _, _ -> openOutside(Uri.parse(url)) }
    }

    private fun isOurs(uri: Uri): Boolean =
        uri.scheme == "https" && uri.host.equals(HOST, ignoreCase = true)

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
        const val HOME = "https://$HOST/"
        // Un texto más largo no es una búsqueda sino un párrafo pegado por error.
        const val MAX_QUERY = 500
    }
}
