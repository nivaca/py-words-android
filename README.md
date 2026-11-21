# py-words for Android

*[Leer en español](README.es.md)* · [Changelog](CHANGELOG.md)

py-words for Android is a small Android app for the web version of
[py-words](https://github.com/nivaca/py-words), the Latin-English-Latin and
Latin-Spanish-Latin dictionary with inflectional morphology, which runs at
<https://py-words.uniandes.edu.co>. The app is only a frontend: it shows that site in a
window of its own, and every search, result and setting comes from the site. It has no
copy of the dictionary and does not work without the Internet.

I am Nicolas Vaughan (<nicolasvaughan@proton.me>), and I wrote it in 2026.

## What it does

- The site, full screen, in light or dark mode as the system says (the site follows
  the colour scheme of the device).
- Pages of the site open in the app; links to anything else (GitHub, the author's page)
  open in the browser.
- Back returns to the previous page of the site, and closes the app when there is none.
- The settings of the site (the language of the meanings, fuzzy search, the earlier
  searches) are kept in its cookie, so they stay from one use to the next.
- From any app: select a Latin word or line and choose **Look up in py-words** in the
  menu of the selection, or share a text with the app. Links to
  `py-words.uniandes.edu.co` can open in it too.
- When the site cannot be reached, a short message and a **Try again** button, in
  English or Spanish.

## Requirements

Android 10 (API 29) or newer, and an Internet connection.

## Building

You need a JDK (17 or newer) and the Android SDK with platform 36. Write the path of the
SDK in `local.properties` (`sdk.dir=/home/me/Android/Sdk`), or set `ANDROID_HOME`, and then:

```sh
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

The Gradle wrapper downloads the right Gradle by itself. The project uses only the
Android framework (no AndroidX, no other libraries).

## Releases and signing

`./gradlew assembleRelease` makes the release APK, shrunk with R8 (about 57 KB). It is
signed only if the file `keystore.properties` exists in the root of the project, with the
keys `storeFile`, `storePassword`, `keyAlias` and `keyPassword`; the key and that file are
not in git. A signed APK is copied to `dist/py-words-android-VERSION.apk`, replacing the
older ones there. Without the file, the release APK comes out unsigned and nothing is
copied.

## How it works

All the code is in `app/src/main/java/io/github/nivaca/pywords/MainActivity.kt`: one
activity with a WebView. It keeps the pages of `py-words.uniandes.edu.co` inside and sends
other links out, saves the cookie when the app goes to the background, shows a progress
bar and the error screen, and turns a word from another app into `/?q=WORD`.
`docs/DESCRIPTION.md` tells how it was made.

## License

py-words for Android is free software, under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`); see [LICENSE](LICENSE). py-words itself has the same license.
