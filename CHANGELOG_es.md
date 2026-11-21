# Cambios

Los cambios de py-words para Android. El código está en
[GitHub](https://github.com/nivaca/py-words-android) y en
[Codeberg](https://codeberg.org/nivaca/py-words-android).

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
