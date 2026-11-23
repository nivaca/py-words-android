# py-words para Android 2.4: descripción

*[Read in English](DESCRIPTION.md)*

## Análisis

py-words para Android es una app de Android para py-words, el diccionario latín-inglés-latín y latín-español-latín con morfología flexiva. Muestra py-words desde una copia del programa que corre dentro de la app, sin internet, o, si se pide en los ajustes de la app, desde el sitio https://py-words.uniandes.edu.co. Fue desarrollada por Nicolás Vaughan en noviembre de 2026 y es software libre, bajo la Licencia Pública General de GNU, versión 3 o posterior; py-words, que la app lleva, tiene la misma licencia, y sus datos, las suyas propias.

La versión 1.0 respondía a un requisito simple: una app que sirviera de entrada al sitio, sin copia del diccionario. De ahí se siguieron los demás, casi todos tomados de Wiktionary Reader, la otra app del autor. Debía ocupar la pantalla entera y respetar el modo oscuro del sistema; mantener dentro las páginas de py-words y abrir fuera los demás enlaces; volver atrás por las páginas visitadas; conservar los ajustes de una vez a otra, y poder consultarse desde cualquier app con la palabra seleccionada. Cuando no hay conexión, tenía que decirlo con claridad y ofrecer un segundo intento.

La 2.0 vino de una pregunta: si la app podía correr py-words desde su repositorio de GitHub en lugar del sitio. La respuesta fue llevar el programa dentro de la app y dejar elegir la fuente. Se pidió que las dos convivieran, con un cambio sencillo entre ellas, y que la página fuera la misma en ambas. En la 2.1, la fuente del teléfono pasó a ser la de omisión, porque funciona en cualquier parte y lleva el py-words más nuevo. Después de la 2.4 se pidió quitar del menú la elección de la página web: el sitio queda como opción de los ajustes, apagada si nadie la enciende.

## Diseño

Hay una pantalla, `MainActivity.kt`, y un objeto, `LocalServer.kt`. La vista tiene arriba una barra fina, con la fuente de py-words y el menú (⋮: Volver a cargar, Ajustes y, con la página web, Abrir en el navegador), y debajo el WebView, con una barra de progreso, una capa de carga («Cargando el diccionario…») y otra para los errores.

La decisión principal fue no hacer nada que py-words ya haga. Su página se genera en el servidor, con formularios corrientes (`GET /?q=…` para buscar, `POST` para los ajustes); guarda los ajustes y las búsquedas anteriores en una galleta, y tiene su propia versión oscura bajo `prefers-color-scheme: dark`. Para la fuente del teléfono se siguió la misma idea: en vez de escribir otra interfaz, la app corre la aplicación WSGI del sitio, `public_app()` de `words_web.py`, en `127.0.0.1`, y el WebView la abre como abriría el sitio. Esa aplicación guarda todo en las galletas de cada visitante y nada en el servidor, de modo que en el teléfono tampoco escribe más que la caché del diccionario.

py-words entra en el proyecto como submódulo de git (`py-words/`), fijado en una etiqueta de su repositorio, hoy `v3.30`. La app guarda en sus preferencias solo la fuente elegida; si nadie eligió, empieza en el teléfono (en la 2.0 empezaba en línea).

La fuente no se elige en el menú sino en Ajustes, un diálogo propio de la app (distinto de los ajustes de py-words, que viven en su página) con una sola casilla: «Usar la página web (py-words.uniandes.edu.co, necesita internet) en lugar del diccionario de este teléfono». Quien había elegido En línea antes la conserva, porque la preferencia es la misma, y la ve marcada.

Fuera de Chaquopy, que trae Python, la app usa solo el framework de Android, sin AndroidX, igual que Wiktionary Reader, de la que hereda los archivos de Gradle, el tema y el manejo de las barras del sistema.

## Implementación

Está escrita en Kotlin (dos archivos, 414 líneas) y Python (un archivo, 45), con 270 líneas de XML entre el manifiesto, los recursos y la vista. Usa el framework de Android, la biblioteca estándar de Kotlin y Chaquopy 17.2, con Python 3.13. El APK release, reducido con R8 y firmado, pesa unos 28 MB, casi todo el intérprete y el diccionario (42 MB hasta la 2.1, cuando llevaba además Python para x86_64). El bloque de información de dependencias que el plugin de Android añade por omisión está desactivado, porque va cifrado con una clave de Google.

### py-words en el teléfono

Una tarea de Gradle copia del submódulo los módulos de Python (sin los de la ventana y la terminal, que necesitan tkinter o curses, ausentes en Android), `data/` y los dos iconos que muestra la página; Chaquopy los compila a *bytecode*. `pywords_android.py` arranca el servidor una vez por proceso, en un hilo propio y en un puerto libre, tras llevar la caché de py-words a la carpeta de caché de Android y dejar fuera del disco la configuración y el historial. `LocalServer.kt` arranca Python y lo llama en segundo plano, porque la primera carga tarda (unos 11 segundos en el emulador, mientras Chaquopy desempaca los 38 MB de datos y py-words hace su caché; unos 6 después). La configuración de seguridad de red permite HTTP sin cifrar solo hacia `127.0.0.1`.

### Las dos fuentes

Al cambiar de fuente, la app abre en la otra la búsqueda que había en pantalla y olvida el historial, para que Atrás no salte de una fuente a otra; antes esconde la capa de carga, que se quedaba sobre la página web si el cambio llegaba mientras el teléfono cargaba. La pantalla de error de la fuente en línea ofrece pasar al teléfono. El estado del WebView solo se recupera para el mismo servidor, porque el puerto del teléfono cambia cada vez que Android cierra la app.

### Los enlaces y otras apps

`shouldOverrideUrlLoading` deja en el WebView los enlaces a la fuente actual y manda los demás a otra app. La galleta se escribe a disco en `onPause`. La app aparece en el menú del texto seleccionado («Buscar en py-words», `PROCESS_TEXT`) y acepta texto compartido (`SEND`); los dos casos se convierten en `/?q=PALABRA`. Un texto de más de 500 caracteres se descarta. Los enlaces al sitio (`VIEW`) se abren en la fuente elegida.

### El modo oscuro y el gesto de volver

Al cambiar a modo oscuro, la actividad se crea de nuevo para tomar el tema oscuro, y el WebView recupera la página y su historial; el servidor del teléfono sigue corriendo. Desde Android 13 el gesto de volver se reclama solo mientras hay adónde volver, y se comprueba también al crearse la actividad.

### Seguir a py-words

py-words no se actualiza dentro de la app: va en el APK, así que cada py-words nuevo pide una versión nueva de la app. `tools/update-py-words.py` la hace entera. Busca la etiqueta más nueva de py-words, mueve a ella el submódulo, sube `versionCode` y `versionName`, escribe la versión nueva de py-words en los README, los registros de cambios y estos dos documentos (lo que haya bajo «Sin publicar» pasa a la entrada de esa versión), y compila el APK firmado; si la compilación falla, deshace sus cambios. Si no, confirma, firma la etiqueta, sube a las dos forjas y crea las versiones, con las notas tomadas del registro de cambios. Si una corrida se detuvo después de confirmar, la siguiente publica lo que falte. `tools/release.py` de py-words lo corre al final de cada versión. Se descartó compilar en GitHub Actions, que habría puesto en los secretos de GitHub la clave del APK y la de OpenPGP, que firma también py-words; y se descartó que la app bajara py-words sola, porque tendría que comprobar firmas al correr y no tendría nada que correr en un primer arranque sin internet.

### El icono

Es el de py-words. Para el icono adaptable se quitó su fondo, que pasó a ser el color de fondo (`#292929`), y el resto se redujo a la zona segura; Inkscape lo exporta como PNG en las cinco densidades.

## Validación

La app no tiene pruebas automáticas; py-words tiene las suyas, y casi todo lo que importa es de py-words. Se comprobó a mano en el emulador de Android (Android 16), con capturas de pantalla tomadas por adb. En la 1.0: la portada; palabras enviadas desde el menú de la selección (*amicorum*, *rosa*, *lupus*); el gesto de volver; la pantalla de error sin red y el botón que, de vuelta la conexión, carga la misma búsqueda; el modo oscuro al abrir la app y al cambiarlo con la app abierta, y los ajustes, que sobrevivieron a cerrar la app. Esas pruebas mostraron dos defectos que se corrigieron (la barra de estado clara en modo oscuro y el gesto de volver tras recrear la actividad).

En la 2.0: el cambio de la fuente en línea al teléfono y de vuelta, con la búsqueda conservada (*amicorum*, *arma virumque cano*); el primer arranque en el teléfono y uno posterior; una búsqueda en el teléfono con el wifi y los datos apagados; el modo oscuro en el teléfono; Atrás después de cambiar de fuente; el botón de la pantalla de error que pasa al teléfono, y el APK release firmado, reducido con R8, con la fuente del teléfono. Luego el APK release de la 2.0 se instaló en un moto g55 5G con Android 16, en modo oscuro, y allí se repitió lo principal: una palabra en línea; el cambio al teléfono, cuyo primer arranque tardó unos 12 segundos; un arranque posterior en modo avión (*arma virumque cano*), de menos de 4 segundos y con el verso entero sin internet; la vuelta a la fuente en línea con la búsqueda conservada (*lupus*), y el giro de la pantalla. Antes, en el escritorio, se midió la carga de `public_app()` con Python 3.13 (1,9 segundos sin caché, 0,4 con ella). El lint de Android no da errores y el compilador de Kotlin no da advertencias. `tools/update-py-words.py` se probó en un clon aparte del repositorio: con `--dry-run`, de la 3.28 a la 3.29; con `--only-if-changed`, que se detuvo porque solo cambiaba `version.py`; con una etiqueta más vieja, que rechaza, y con los cambios mismos en los archivos, con y sin una sección «Sin publicar» en los registros de cambios. Para la 2.2 se hizo la compilación de F-Droid en su propio contenedor (`fdroidserver:buildserver-trixie`), con los mismos pasos que las comprobaciones de su repositorio, y se comprobó que el APK lleva solo las bibliotecas de `arm64-v8a`. Luego se instaló sobre la 2.1 en el teléfono: arrancó y buscó *amicorum* y *arma virumque cano* con Logeion, y *friend* del inglés al latín en el teléfono; esas búsquedas y el menú de las fuentes son las cuatro capturas de la tienda. Con el paso de la página web a los ajustes, la app compila sin advertencias y el lint de Android no da errores; en el emulador se probaron el menú nuevo, el paso a la página web mientras el teléfono cargaba (que mostró el defecto de la capa de carga, ya corregido), la opción conservada al cerrar y abrir la app y la vuelta al teléfono.

## Plataforma

Funciona en Android 10 (API 29) o posterior, en teléfonos y tabletas ARM de 64 bits (arm64-v8a), porque Python 3.13 solo corre en dispositivos de 64 bits y, desde la 2.2, la app lo lleva solo para ARM: en el emulador x86_64 la app se cerraba al arrancar Python, con un error nativo, y el APK de F-Droid no debía ofrecerse así a dispositivos x86_64 como los Chromebook; se compila contra la API 36. Internet hace falta solo para la fuente en línea y para Logeion, una fuente en la que py-words puede buscar. No pide más permiso que el de internet.

## Ambiente

Fue desarrollada en Fedora Linux, con OpenJDK 25, el SDK de Android (plataforma 36, build-tools 36.1), Gradle 9.8 con el Android Gradle Plugin 9.5, que trae Kotlin integrado, y Chaquopy 17.2. El código está en GitHub (https://github.com/nivaca/py-words-android) y en Codeberg (https://codeberg.org/nivaca/py-words-android), donde cada versión lleva una etiqueta `vVERSIÓN` y su APK firmado; el de py-words, en https://github.com/nivaca/py-words.

Para compilarla se clona con `git clone --recurse-submodules` (o se corre `git submodule update --init`), y hacen falta un JDK 17 o posterior, el SDK de Android, cuya ruta va en `local.properties` (`sdk.dir=…`) o en `ANDROID_HOME`, y `python3.13` en el `PATH`. `./gradlew assembleDebug` produce `app/build/outputs/apk/debug/app-debug.apk`, que se instala con `adb install -r`. `./gradlew assembleRelease` produce el APK release, firmado si existe `keystore.properties` (fuera de git) y copiado entonces a `dist/py-words-android-VERSIÓN.apk`; si ese archivo nombra además una clave de gpg (`gpgKey`), el APK lleva al lado su firma OpenPGP (`.apk.asc`). Desde la 2.1, las versiones publicadas se firman así con la clave que firma los paquetes de py-words, cuya clave pública está en `py-words-signing-key.asc`, y sus etiquetas también; las de la 1.0 y la 2.0 recibieron después sus archivos `.asc`. Para llevar un py-words más nuevo, `python3 tools/update-py-words.py` mueve el submódulo, compila, etiqueta y publica (`--dry-run` solo dice qué haría); `tools/release.py` de py-words lo corre al final de cada versión. En el teléfono, Obtainium puede seguir las versiones de GitHub e instalar cada APK nuevo. Para F-Droid, la ficha de la tienda está en `fastlane/metadata/android/` y la receta en `fdroid/io.github.nivaca.pywords.yml`, que compila la etiqueta con el submódulo y borra antes `py-words/TAGS`, un archivo de Emacs que el analizador de F-Droid toma por binario; F-Droid firma con su propia clave. La fuente elegida vive en las preferencias de la app (`settings.xml`); los ajustes de py-words, en sus galletas, y la caché del diccionario, en la carpeta de caché de la app.
