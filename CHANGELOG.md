# Changelog

All notable changes to py-words for Android. The source is on
[GitHub](https://github.com/nivaca/py-words-android) and
[Codeberg](https://codeberg.org/nivaca/py-words-android).

## 2.8 — 2026-11-26

- py-words 3.32, in place of 3.31 ([its
  changes](https://github.com/nivaca/py-words/blob/main/CHANGELOG.md)).

## 2.7 — 2026-11-24

- py-words 3.31, in place of 3.30 ([its
  changes](https://github.com/nivaca/py-words/blob/main/CHANGELOG.md)).
  The dictionary and its page are the same as in 3.30; only the number
  of the version changed.

## 2.6 — 2026-11-23

- Each release also carries `SHA256SUMS`, with the SHA-256 of the APK,
  and its OpenPGP signature `SHA256SUMS.asc`; 2.5 got them afterwards.
  Before tagging or pushing, `tools/update-py-words.py` checks every
  signature with only the public key, as a user would, and the signature
  of the tag, and stops if one fails.
- `tools/update-py-words.py` also releases changes of the app alone,
  with the same py-words, when the changelogs have an "Unreleased"
  section (2.5 was the first).

## 2.5 — 2026-11-23

- The menu no longer chooses between the web page and the dictionary on
  the phone: it has **Reload**, **Settings** and, with the web page,
  **Open in the browser**. The web page is now an option in
  **Settings** ("Use the web page…"), off unless chosen; the dictionary
  on the phone is always the default.
- A change to the web page while the dictionary on the phone was
  still loading left "Loading the dictionary…" over the page; no more.

## 2.4 — 2026-11-22

- py-words 3.30, in place of 3.29 ([its
  changes](https://github.com/nivaca/py-words/blob/main/CHANGELOG.md)).
  The dictionary and its page are the same as in 3.29; only the number
  of the version changed.

## 2.3 — 2026-11-22

- py-words 3.29, in place of 3.28 ([its
  changes](https://github.com/nivaca/py-words/blob/main/CHANGELOG.md)).
  The dictionary and its page are the same as in 3.28; only the number
  of the version changed.
- `tools/update-py-words.py` puts the newest py-words in the app and
  releases the version of the app that carries it; the release tool of
  py-words runs it at the end of each release of py-words. The notes of
  each release say how to get the new versions by themselves with
  Obtainium.

## 2.2 — 2026-11-21

- The APK is now only for 64-bit ARM devices (`arm64-v8a`), the phones
  and tablets that run Android: it no longer carries Python for x86_64,
  where the app closed when Python started (seen in the emulator). It is
  about 28 MB instead of 42.
- A store listing and a build recipe for F-Droid, in
  `fastlane/metadata/android/` and `fdroid/`.
- The build no longer sets `android.useAndroidX=false`, which the
  Android plugin now warns about.

## 2.1 — 2026-11-21

- The phone is now the default source: the app starts with py-words on
  the phone, unless Online has been chosen in the menu.
- The releases are signed with OpenPGP, with the key that signs the
  packages of py-words (`py-words-signing-key.asc`): the tag, and the APK
  in a `.apk.asc` file made by the build.

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
