# Cambios

Los cambios de py-words para Android. El código está en
[GitHub](https://github.com/nivaca/py-words-android) y en
[Codeberg](https://codeberg.org/nivaca/py-words-android).

## 2.6 — 2026-11-23

- Cada versión lleva también `SHA256SUMS`, con el SHA-256 del APK, y su
  firma OpenPGP `SHA256SUMS.asc`; la 2.5 los recibió después. Antes de
  etiquetar o subir nada, `tools/update-py-words.py` comprueba todas las
  firmas solo con la clave pública, como lo haría un usuario, y la de la
  etiqueta, y se detiene si alguna falla.
- `tools/update-py-words.py` publica también cambios de la app solos,
  con el mismo py-words, cuando los registros de cambios tienen una
  sección «Sin publicar» (la 2.5 fue la primera).

## 2.5 — 2026-11-23

- El menú ya no elige entre la página web y el diccionario del teléfono:
  tiene **Volver a cargar**, **Ajustes** y, con la página web, **Abrir
  en el navegador**. La página web es ahora una opción de **Ajustes**
  («Usar la página web…»), apagada si no se elige; el diccionario del
  teléfono es siempre el de omisión.
- Si se cambiaba a la página web mientras el diccionario del teléfono
  aún cargaba, «Cargando el diccionario…» se quedaba sobre la página;
  ya no.

## 2.4 — 2026-11-22

- py-words 3.30, en lugar de la 3.29 ([sus
  cambios](https://github.com/nivaca/py-words/blob/main/CHANGELOG_es.md)).
  El diccionario y su página son los mismos de la 3.29; solo cambió el
  número de la versión.

## 2.3 — 2026-11-22

- py-words 3.29, en lugar de la 3.28 ([sus
  cambios](https://github.com/nivaca/py-words/blob/main/CHANGELOG_es.md)).
  El diccionario y su página son los mismos de la 3.28; solo cambió el
  número de la versión.
- `tools/update-py-words.py` pone en la app el py-words más nuevo y
  publica la versión de la app que lo lleva; la herramienta de versiones
  de py-words lo corre al final de cada versión de py-words. Las notas de
  cada versión dicen cómo recibir las nuevas solas con Obtainium.

## 2.2 — 2026-11-21

- El APK es ahora solo para dispositivos ARM de 64 bits (`arm64-v8a`),
  los teléfonos y tabletas que usan Android: ya no lleva Python para
  x86_64, donde la app se cerraba al arrancar Python (visto en el
  emulador). Pesa unos 28 MB en lugar de 42.
- Una ficha y una receta de compilación para F-Droid, en
  `fastlane/metadata/android/` y `fdroid/`.
- La compilación ya no fija `android.useAndroidX=false`, de lo que el
  plugin de Android ahora advierte.

## 2.1 — 2026-11-21

- El teléfono es ahora la fuente por omisión: la app empieza con py-words
  en el teléfono, salvo que se haya elegido En línea en el menú.
- Las versiones publicadas van firmadas con OpenPGP, con la clave que
  firma los paquetes de py-words (`py-words-signing-key.asc`): la etiqueta,
  y el APK en un archivo `.apk.asc` que hace la compilación.

## 2.0 — 2026-11-21

- py-words puede correr ahora en el teléfono, sin internet: la app lleva
  py-words 3.28 (de su repositorio de GitHub, como submódulo de git) y un
  Python 3.13 para correrlo (Chaquopy), y muestra la misma página del
  sitio.
- Una barra fina arriba dice de dónde viene py-words; su menú cambia entre
  En línea y En este teléfono, conservando la búsqueda en pantalla, y
  tiene Volver a cargar y Abrir en el navegador.
- Si no se llega al sitio, la pantalla de error ofrece la copia del
  teléfono.
- Los enlaces al sitio se abren en la fuente elegida.
- El APK pesa ahora unos 42 MB, y necesita un dispositivo de 64 bits.

## 1.0 — 2026-11-21

- Primera versión: la versión web de py-words
  (<https://py-words.uniandes.edu.co>) a pantalla completa en un WebView,
  en modo claro u oscuro según el sistema.
- Las páginas del sitio se abren en la app; los demás enlaces, en el
  navegador.
- Atrás vuelve a la página anterior del sitio.
- Los ajustes del sitio, guardados en su galleta, se conservan de una vez
  a otra.
- Búsqueda desde otras apps: el texto seleccionado (*Buscar en py-words*),
  el texto compartido y los enlaces al sitio.
- Una pantalla con *Volver a intentarlo* cuando no se llega al sitio;
  interfaz en inglés y en español.
