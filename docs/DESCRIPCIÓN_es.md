# py-words para Android 1.0: descripción

*[Read in English](DESCRIPTION.md)*

## Análisis

py-words para Android es una app pequeña de Android para la versión web de py-words, el diccionario latín-inglés-latín y latín-español-latín con morfología flexiva, que funciona en https://py-words.uniandes.edu.co. Es solo una interfaz: muestra el sitio en una ventana propia, y las búsquedas, los resultados y los ajustes son todos del sitio. Fue desarrollada por Nicolás Vaughan en noviembre de 2026 y es software libre, bajo la Licencia Pública General de GNU, versión 3 o posterior; el diccionario y sus datos pertenecen a py-words, con sus propias licencias.

El requisito fue ese: una app que sirva de entrada al sitio, sin copia del diccionario. De ahí se siguieron los demás, casi todos tomados de Wiktionary Reader, la otra app del autor. Debía ocupar la pantalla entera y respetar el modo oscuro del sistema; mantener dentro las páginas del sitio y abrir fuera los demás enlaces; volver atrás por las páginas visitadas; conservar los ajustes del sitio de una vez a otra, y poder consultarse desde cualquier app con la palabra seleccionada. Cuando no hay conexión, tenía que decirlo con claridad y ofrecer un segundo intento.

## Diseño

Hay una sola pantalla y una sola clase, `MainActivity.kt`. Su vista es un `FrameLayout` con el WebView, una barra de progreso fina encima y una capa para el error de red, oculta mientras el sitio responde.

La decisión principal fue no hacer nada que el sitio ya haga. El sitio genera sus páginas en el servidor, con formularios corrientes (`GET /?q=…` para buscar, `POST` para los ajustes); guarda los ajustes y las búsquedas anteriores en una galleta que dura un año, y tiene su propia versión oscura bajo `prefers-color-scheme: dark`. Bastaba con un WebView bien configurado. No hay datos propios ni preferencias de la app: lo único que se guarda es la galleta del sitio, en el almacén de galletas del WebView.

La app usa solo el framework de Android, sin AndroidX, igual que Wiktionary Reader, de la que hereda los archivos de Gradle, el tema y el manejo de las barras del sistema.

## Implementación

Está escrita en Kotlin, en un archivo de 242 líneas, con 161 líneas de XML entre el manifiesto, los recursos y la vista. No usa más que el framework de Android y la biblioteca estándar de Kotlin. El APK de depuración pesa 2,6 MB; el release, reducido con R8 y firmado, 57 KB. El bloque de información de dependencias que el plugin de Android añade por omisión está desactivado, porque va cifrado con una clave de Google.

### Los enlaces

`shouldOverrideUrlLoading` deja en el WebView todo enlace `https` a `py-words.uniandes.edu.co` y manda los demás a otra app con `ACTION_VIEW`. Las descargas, que el sitio hoy no ofrece, irían al navegador. La galleta se escribe a disco en `onPause`, para que un ajuste cambiado no se pierda si Android cierra la app.

### Desde otras apps

La app aparece en el menú del texto seleccionado («Buscar en py-words», `PROCESS_TEXT`) y acepta texto compartido (`SEND`); los dos casos se convierten en `/?q=PALABRA`, la misma dirección de los ejemplos de la portada. Un texto de más de 500 caracteres se descarta. También se ofrece para abrir los enlaces del sitio (`VIEW`), sin verificar el dominio, así que Android pregunta al usuario.

### El modo oscuro y el gesto de volver

Al cambiar el sistema a modo oscuro con la app abierta, la actividad se crea de nuevo para tomar el tema oscuro (si no, los iconos de la barra de estado seguían claros); el WebView guarda su estado y lo recupera, con la página y su historial. Desde Android 13 el gesto de volver se reclama de antemano: la app lo hace solo mientras el WebView tiene adónde volver, y lo comprueba también al crearse, porque el historial recuperado no avisa. Antes de Android 13 lo hace `onBackPressed`.

### El icono

Es el de py-words. Para el icono adaptable se quitó su fondo, que pasó a ser el color de fondo (`#292929`), y el resto se redujo a la zona segura; Inkscape lo exporta como PNG en las cinco densidades.

## Validación

No hay pruebas automáticas: la app es un marco alrededor de un sitio, y casi todo lo que importa es del sitio. Se comprobó a mano en el emulador de Android (Android 16), con capturas de pantalla tomadas por adb: la portada; palabras enviadas desde el menú de la selección (*amicorum*, *rosa*, *lupus*); el gesto de volver, hasta la portada y fuera de la app; la pantalla de error con el wifi y los datos apagados, y el botón que, de vuelta la conexión, carga la misma búsqueda; el modo oscuro al abrir la app y al cambiarlo con la app abierta, y los ajustes del sitio, que sobrevivieron a cerrar la app. Esas pruebas mostraron los dos defectos que se corrigieron (la barra de estado clara en modo oscuro y el gesto de volver tras recrear la actividad). El lint de Android no da errores y el compilador de Kotlin no da advertencias.

## Plataforma

Funciona en Android 10 (API 29) o posterior, en cualquier teléfono o tableta; se compila contra la API 36. Necesita internet siempre, porque todo lo hace el sitio. No pide más permiso que el de internet.

## Ambiente

Fue desarrollada en Fedora Linux, con OpenJDK 25, el SDK de Android (plataforma 36, build-tools 36.1) y Gradle 9.8 con el Android Gradle Plugin 9.5, que trae Kotlin integrado. El sitio, py-words, tiene su código en https://github.com/nivaca/py-words.

Para compilarla hacen falta un JDK 17 o posterior y el SDK de Android, cuya ruta va en `local.properties` (`sdk.dir=…`) o en `ANDROID_HOME`. `./gradlew assembleDebug` produce `app/build/outputs/apk/debug/app-debug.apk`, que se instala con `adb install -r`. `./gradlew assembleRelease` produce el APK release, reducido con R8, firmado si existe `keystore.properties` (fuera de git) y copiado entonces a `dist/py-words-android-VERSIÓN.apk`. La app no tiene ajustes propios; los del sitio viven en su galleta, dentro de los datos de la app, y se borran al borrar esos datos desde los ajustes de Android.
