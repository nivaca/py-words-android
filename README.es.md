# py-words para Android

*[Read in English](README.md)* · [Cambios](CHANGELOG_es.md)

py-words para Android es una app de Android para
[py-words](https://github.com/nivaca/py-words), el diccionario latín-inglés-latín y
latín-español-latín con morfología flexiva. Muestra py-words desde una de dos fuentes, y un
menú arriba cambia de una a otra:

- **En línea**: el sitio <https://py-words.uniandes.edu.co>, que necesita internet.
- **En este teléfono**: py-words mismo, que corre dentro de la app, sin internet. La app
  lleva una copia del programa y de sus datos (ahora py-words 3.28) y un Python 3.13 para
  correrlo.

Las dos muestran la misma página, con las mismas búsquedas, resultados y ajustes; la app es
solo una ventana para ella. La app empieza en el teléfono, salvo que se haya elegido En línea.

Soy Nicolás Vaughan (<nicolasvaughan@proton.me>) y la escribí en 2026.

## Qué hace

- py-words a pantalla completa, bajo una barra fina que dice de dónde viene, en modo claro
  u oscuro según el sistema.
- El menú (⋮): **En línea** o **En este teléfono**, **Volver a cargar** y, en línea,
  **Abrir en el navegador**. Al cambiar de fuente se conserva la búsqueda que hay en
  pantalla.
- En el teléfono, el diccionario carga en unos segundos la primera vez (se desempaca y se
  hace su caché), y más rápido después. Solo Logeion, una fuente en la que py-words puede
  buscar, sigue necesitando internet.
- Las páginas de py-words se abren en la app; los enlaces a cualquier otra cosa, en el
  navegador.
- Atrás vuelve a la página anterior, y cierra la app cuando no la hay.
- Los ajustes de py-words (la lengua de los significados, la búsqueda aproximada, las
  búsquedas anteriores) se guardan en su galleta, así que se conservan de una vez a otra.
  Cada fuente tiene los suyos.
- Desde cualquier app: se selecciona una palabra o un verso latino y se elige **Buscar en
  py-words** en el menú de la selección, o se comparte un texto con la app. Los enlaces a
  `py-words.uniandes.edu.co` también pueden abrirse en ella, en la fuente elegida.
- Si no se puede llegar al sitio, un mensaje breve con **Volver a intentarlo** y **Usarlo
  en este teléfono**. Interfaz en inglés y en español.

## Requisitos

Android 10 (API 29) o posterior, en un dispositivo de 64 bits (Python 3.13 solo corre en
ellos). Internet, solo para la fuente en línea.

## Compilación

py-words es un submódulo de git, en `py-words/`, fijado en una etiqueta de su repositorio.
Se clona con él:

```sh
git clone --recurse-submodules https://github.com/nivaca/py-words-android.git
```

(o se corre `git submodule update --init` en un clon hecho sin él). Hacen falta un JDK (17 o
posterior), el SDK de Android con la plataforma 36, y Python 3.13 en el `PATH` como
`python3.13`, con el que la compilación pasa py-words a *bytecode*. La ruta del SDK va en
`local.properties` (`sdk.dir=/home/yo/Android/Sdk`) o en `ANDROID_HOME`; luego:

```sh
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

El *wrapper* de Gradle descarga la versión correcta de Gradle, y el plugin de Chaquopy, el
Python para Android. Fuera de Chaquopy, el proyecto usa solo el framework de Android (sin
AndroidX ni otras bibliotecas).

Para poner en la app un py-words más nuevo, se mueve el submódulo a su etiqueta y se compila
de nuevo:

```sh
cd py-words && git fetch --tags && git checkout v3.29 && cd ..
git add py-words
```

## Versiones y firma

`./gradlew assembleRelease` produce el APK release, reducido con R8 (unos 42 MB, casi todo
Python y el diccionario). Solo se firma si existe en la raíz del proyecto el archivo
`keystore.properties`, con las claves `storeFile`, `storePassword`, `keyAlias` y
`keyPassword`; ni la clave ni ese archivo están en git. El APK firmado se copia a
`dist/py-words-android-VERSIÓN.apk`, en lugar de los anteriores. Sin ese archivo, el APK
release sale sin firmar y no se copia nada.

Si `keystore.properties` tiene además `gpgKey`, la huella de una clave de gpg, la
compilación firma también el APK con ella, en `dist/py-words-android-VERSIÓN.apk.asc`. Las
versiones publicadas se firman con la clave que firma los paquetes de py-words, cuya clave
pública es [py-words-signing-key.asc](py-words-signing-key.asc) (huella
`8187 0643 CA22 1AF9 0C30  554E BE68 32CD 3599 4948`); sus etiquetas también van firmadas
con ella. Para comprobar una descarga:

```sh
gpg --import py-words-signing-key.asc
gpg --verify py-words-android-VERSIÓN.apk.asc py-words-android-VERSIÓN.apk
```

## F-Droid

La descripción, el icono y las notas de cada versión para F-Droid están en
`fastlane/metadata/android/` (en inglés y en español), donde F-Droid los busca. La receta de
compilación para el repositorio de F-Droid es `fdroid/io.github.nivaca.pywords.yml`: compila
la etiqueta `vVERSIÓN` desde la carpeta `app`, con el submódulo, y encuentra las versiones
nuevas por sus etiquetas. Antes de compilar borra `py-words/TAGS` (un archivo de etiquetas
de Emacs), porque el analizador de F-Droid lo toma por un binario. F-Droid firma las apps con
su propia clave, así que su APK y el de las versiones publicadas aquí no se actualizan entre sí.

## Cómo funciona

`MainActivity.kt` es la única pantalla: un WebView, la barra con el menú y las pantallas de
carga y de error. En línea, abre `https://py-words.uniandes.edu.co`. En el teléfono,
`LocalServer.kt` arranca Python con [Chaquopy](https://chaquo.com/chaquopy/), y en él
`app/src/main/python/pywords_android.py` corre `public_app()` de `words_web.py` (la misma
aplicación del sitio) en `127.0.0.1`, en un puerto libre; el WebView abre esa dirección. La
compilación copia del submódulo solo lo que hace falta: los módulos de Python, `data/` y dos
iconos. `docs/DESCRIPCIÓN_es.md` la describe.

## Licencia

py-words para Android es software libre, bajo la Licencia Pública General de GNU, versión 3
o posterior (`GPL-3.0-or-later`); véase [LICENSE](LICENSE). py-words, que la app lleva, tiene
la misma licencia; sus datos tienen las licencias que da su propia documentación. Chaquopy
está bajo la licencia MIT, y Python bajo la licencia de la Python Software Foundation.
