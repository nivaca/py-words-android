// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
// This file is part of py-words for Android. See the LICENSE file for details.

// py-words en el teléfono: arranca Python (Chaquopy) y, en él, el servidor de
// pywords_android.py, una sola vez por proceso.  Lo hace en un hilo aparte,
// porque cargar el diccionario tarda unos segundos la primera vez.

package io.github.nivaca.pywords

import android.content.Context
import android.os.Handler
import android.os.Looper
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.util.concurrent.Executors

object LocalServer {
    /** The port of the running server, or null while it is not running. */
    @Volatile var port: Int? = null
        private set

    /** The version of py-words inside the app, once Python has started. */
    @Volatile var version: String? = null
        private set

    private val worker = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())

    /** Starts the server if needed; DONE gets the port, or the error. */
    fun start(context: Context, done: (Result<Int>) -> Unit) {
        port?.let { done(Result.success(it)); return }
        val app = context.applicationContext
        worker.execute {
            // Si otra llamada ya lo arrancó mientras esta esperaba, Python
            // devuelve el mismo puerto.
            val result = runCatching {
                if (!Python.isStarted()) Python.start(AndroidPlatform(app))
                val module = Python.getInstance().getModule("pywords_android")
                version = module.callAttr("version").toString()
                module.callAttr("start", app.cacheDir.path).toInt().also { port = it }
            }
            main.post { done(result) }
        }
    }
}
