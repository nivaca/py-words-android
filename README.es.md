# py-words para Android

*[Read in English](README.md)* · [Cambios](CHANGELOG_es.md)

py-words para Android es una app pequeña de Android para la versión web de
[py-words](https://github.com/nivaca/py-words), el diccionario latín-inglés-latín y
latín-español-latín con morfología flexiva, que funciona en
<https://py-words.uniandes.edu.co>. La app es solo una interfaz: muestra ese sitio en una
ventana propia, y todas las búsquedas, los resultados y los ajustes vienen del sitio. No
tiene copia del diccionario ni funciona sin internet.

Soy Nicolás Vaughan (<nicolasvaughan@proton.me>) y la escribí en 2026.

## Qué hace

- El sitio, a pantalla completa, en modo claro u oscuro según el sistema (el sitio sigue
  el esquema de colores del dispositivo).
- Las páginas del sitio se abren en la app; los enlaces a cualquier otra cosa (GitHub, la
  página del autor) se abren en el navegador.
- Atrás vuelve a la página anterior del sitio, y cierra la app cuando no la hay.
- Los ajustes del sitio (la lengua de los significados, la búsqueda aproximada, las
  búsquedas anteriores) se guardan en su galleta, así que se conservan de una vez a otra.
- Desde cualquier app: se selecciona una palabra o un verso latino y se elige **Buscar en
  py-words** en el menú de la selección, o se comparte un texto con la app. Los enlaces a
  `py-words.uniandes.edu.co` también pueden abrirse en ella.
- Si no se puede llegar al sitio, un mensaje breve y un botón **Volver a intentarlo**, en
  inglés o en español.

## Requisitos

Android 10 (API 29) o posterior, y conexión a internet.

## Compilación

Hacen falta un JDK (17 o posterior) y el SDK de Android con la plataforma 36. La ruta del
SDK va en `local.properties` (`sdk.dir=/home/yo/Android/Sdk`) o en `ANDROID_HOME`; luego:

```sh
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

El *wrapper* de Gradle descarga por sí mismo la versión correcta de Gradle. El proyecto usa
solo el framework de Android (sin AndroidX ni otras bibliotecas).

## Versiones y firma

`./gradlew assembleRelease` produce el APK release, reducido con R8 (unos 57 KB). Solo se
firma si existe en la raíz del proyecto el archivo `keystore.properties`, con las claves
`storeFile`, `storePassword`, `keyAlias` y `keyPassword`; ni la clave ni ese archivo están
en git. El APK firmado se copia a `dist/py-words-android-VERSIÓN.apk`, en lugar de los
anteriores. Sin ese archivo, el APK release sale sin firmar y no se copia nada.

## Cómo funciona

Todo el código está en `app/src/main/java/io/github/nivaca/pywords/MainActivity.kt`: una
actividad con un WebView. Mantiene dentro las páginas de `py-words.uniandes.edu.co` y manda
fuera los demás enlaces, guarda la galleta cuando la app pasa a segundo plano, muestra una
barra de progreso y la pantalla de error, y convierte una palabra que llega de otra app en
`/?q=PALABRA`. `docs/DESCRIPCIÓN_es.md` la describe.

## Licencia

py-words para Android es software libre, bajo la Licencia Pública General de GNU, versión 3
o posterior (`GPL-3.0-or-later`); véase [LICENSE](LICENSE). py-words tiene la misma
licencia.
