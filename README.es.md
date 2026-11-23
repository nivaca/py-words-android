# py-words para Android

*[Read in English](README.md)* · [Cambios](CHANGELOG_es.md)

py-words para Android es una app de Android para
[py-words](https://github.com/nivaca/py-words), el diccionario latín-inglés-latín y
latín-español-latín con morfología flexiva. Muestra py-words mismo, que
corre dentro de la app, sin internet: la app lleva una copia del programa y de sus datos
(ahora py-words 3.30) y un Python 3.13 para correrlo.

En los ajustes de la app se puede elegir en su lugar la página web, el sitio
<https://py-words.uniandes.edu.co>, que necesita internet. Las dos muestran la misma página,
con las mismas búsquedas, resultados y ajustes; la app es solo una ventana para ella.

Soy Nicolás Vaughan (<nicolasvaughan@proton.me>) y la escribí en 2026.

## Qué hace

- py-words a pantalla completa, bajo una barra fina que dice de dónde viene, en modo claro
  u oscuro según el sistema.
- El menú (⋮): **Volver a cargar**, **Ajustes** y, con la página web, **Abrir en el
  navegador**. En **Ajustes**, «Usar la página web» cambia de fuente; se conserva la
  búsqueda que hay en pantalla.
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

Android 10 (API 29) o posterior, en un dispositivo ARM de 64 bits (`arm64-v8a`), como casi
todos los teléfonos y tabletas con Android: Python 3.13 solo corre en dispositivos de 64
bits, y desde la 2.2 la app lo lleva solo para ARM. Internet, solo para la fuente en línea.

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

## Seguir a py-words

La app lleva una copia fija de py-words, así que cada py-words nuevo pide una versión nueva
de la app. `tools/update-py-words.py` la hace y la publica:

```sh
python3 tools/update-py-words.py [--tag vX.YY] [--only-if-changed] [--dry-run] [--yes]
```

Mueve el submódulo a la etiqueta más nueva de py-words (o a la de `--tag`), sube
`versionCode` y `versionName` (de 2.2 a 2.3), escribe la versión nueva de py-words en los
README, los registros de cambios y `docs/`, y compila el APK firmado; si la compilación
falla, deshace esos cambios. Luego confirma (`vVERSIÓN: py-words X.YY`), firma la etiqueta,
sube `main` y la etiqueta a `origin` (GitHub y Codeberg) y crea la versión en cada forja, con
el APK, `SHA256SUMS`, sus `.asc` y la clave pública. Antes de etiquetar o subir nada,
comprueba las firmas del APK y de `SHA256SUMS` como lo haría un usuario, en un `GNUPGHOME`
temporal que solo tiene la clave pública, y la firma de la etiqueta; si una falla, no publica
nada. Las notas salen del registro de cambios, donde lo que esté bajo `## Sin publicar` pasa
a la entrada nueva. Si py-words no tiene una etiqueta más nueva pero los registros de cambios
tienen una sección `## Sin publicar`, publica solos esos cambios de la app, con el mismo
py-words. A una versión ya publicada a la que le falte un archivo (como a la 2.5 le faltaba
`SHA256SUMS`) se lo añade, si los que tiene son los de `dist/`. Pregunta antes de cambiar nada;
`--dry-run` solo dice qué haría, y `--only-if-changed` no hace nada si, de lo que la app
lleva, solo cambió el número de la versión. Necesita `gh`, `tea`, `gpg`, `main` sin cambios
por confirmar y las claves de `keystore.properties`. Si se detiene después de confirmar,
correrlo de nuevo publica lo que falte.

`tools/release.py` de py-words lo corre al final de cada versión de py-words, así que la app
sigue a py-words sin que nadie tenga que acordarse. En el teléfono,
[Obtainium](https://github.com/ImranR98/Obtainium) puede seguir las versiones de este
repositorio e instalar cada APK nuevo sobre el anterior.

## Versiones y firma

`./gradlew assembleRelease` produce el APK release, reducido con R8 (unos 28 MB, casi todo
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

Desde la 2.5 cada versión lleva también `SHA256SUMS`, con el SHA-256 del APK, y su firma:

```sh
gpg --verify SHA256SUMS.asc SHA256SUMS
sha256sum -c SHA256SUMS
```

## F-Droid

La descripción, el icono, cuatro capturas y las notas de cada versión para F-Droid están en
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
