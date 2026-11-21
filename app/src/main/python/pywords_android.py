# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Nicolas Vaughan <nicolasvaughan@proton.me>
# This file is part of py-words for Android. See the LICENSE file for details.
"""El servidor de py-words dentro de la app: la misma aplicación del sitio
público (public_app() de words_web.py), en 127.0.0.1 y en un puerto libre,
para que el WebView la abra sin internet.

Los ajustes y las búsquedas de cada visitante van en las galletas, como en
el sitio, así que aquí no se guarda nada salvo la caché del diccionario.
"""

import os
import threading

_server = None
_lock = threading.Lock()


def start(cache_dir: str) -> int:
    """Starts the server once per process (loading the dictionary, which
    takes a moment) and returns its port."""
    global _server
    with _lock:
        if _server is not None:
            return _server.server_port
        home = os.environ['HOME']           # (los archivos de la app)
        #  La caché del diccionario, en la carpeta de caché de Android, que
        #  el sistema puede vaciar: entonces se rehace.  Ni configuración ni
        #  historial en disco.
        os.environ['XDG_CACHE_HOME'] = cache_dir
        os.environ['PY_WORDS_CONFIG'] = os.path.join(home, 'config')
        os.environ['PY_WORDS_HISTORY'] = ''

        from words_web import public_app, serve
        app = public_app(hosts={'127.0.0.1'})
        _server = serve(app, '127.0.0.1', 0)
        threading.Thread(target=_server.serve_forever, name='py-words',
                         daemon=True).start()
        return _server.server_port


def version() -> str:
    """La versión de py-words que va en la app."""
    from version import VERSION
    return VERSION
