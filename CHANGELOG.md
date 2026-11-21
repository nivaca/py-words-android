# Changelog

All notable changes to py-words for Android. The source is on
[GitHub](https://github.com/nivaca/py-words-android) and
[Codeberg](https://codeberg.org/nivaca/py-words-android).

## 2.0 — 2026-11-21

- py-words can now run on the phone, without the Internet: the app carries
  py-words 3.28 (from its GitHub repository, as a git submodule) and a
  Python 3.13 to run it (Chaquopy), and shows the same page as the site.
- A thin bar at the top says where py-words comes from; its menu changes
  between Online and On this phone, keeping the search on the screen, and
  has Reload and Open in the browser.
- When the site cannot be reached, the error screen offers the copy on the
  phone.
- Links to the site open in the source chosen.
- The APK is now about 42 MB, and needs a 64-bit device.

## 1.0 — 2026-11-21

- First version: the web version of py-words
  (<https://py-words.uniandes.edu.co>) full screen in a WebView, in light
  or dark mode as the system says.
- Pages of the site open in the app; other links open in the browser.
- Back returns to the previous page of the site.
- The settings of the site, kept in its cookie, stay from one use to the
  next.
- Lookup from other apps: selected text (*Look up in py-words*), shared
  text and links to the site.
- A screen with *Try again* when the site cannot be reached; English and
  Spanish interface.
