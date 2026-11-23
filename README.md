# py-words for Android

*[Leer en español](README.es.md)* · [Changelog](CHANGELOG.md)

py-words for Android is an Android app for
[py-words](https://github.com/nivaca/py-words), the Latin-English-Latin and
Latin-Spanish-Latin dictionary with inflectional morphology. It can show py-words from one
of two sources, and a menu at the top changes from one to the other:

- **Online**: the site <https://py-words.uniandes.edu.co>, which needs the Internet.
- **On this phone**: py-words itself, which runs inside the app, without the Internet. The
  app carries a copy of the program and its data (now py-words 3.30) and a Python 3.13 to
  run it.

Both show the same page, with the same searches, results and settings; the app is only a
window for it. The app starts on the phone, unless you have chosen Online.

I am Nicolas Vaughan (<nicolasvaughan@proton.me>), and I wrote it in 2026.

## What it does

- py-words full screen, under a thin bar that says where it comes from, in light or dark
  mode as the system says.
- The menu (⋮): **Online** or **On this phone**, **Reload**, and, online, **Open in the
  browser**. Changing the source keeps the search on the screen.
- On this phone, the dictionary loads in a few seconds the first time (it is unpacked and
  its cache is made), and faster afterwards. Only Logeion, a source that py-words can
  search, still needs the Internet.
- Pages of py-words open in the app; links to anything else open in the browser.
- Back returns to the previous page, and closes the app when there is none.
- The settings of py-words (the language of the meanings, fuzzy search, the earlier
  searches) are kept in its cookie, so they stay from one use to the next. Each source has
  its own.
- From any app: select a Latin word or line and choose **Look up in py-words** in the
  menu of the selection, or share a text with the app. Links to
  `py-words.uniandes.edu.co` can open in it too, in the source chosen.
- When the site cannot be reached, a short message with **Try again** and **Use it on
  this phone**. English and Spanish interface.

## Requirements

Android 10 (API 29) or newer, on a 64-bit ARM device (`arm64-v8a`), as nearly all Android
phones and tablets are: Python 3.13 runs only on 64-bit devices, and since 2.2 the app
carries it only for ARM. The Internet only for the online source.

## Building

py-words is a git submodule, in `py-words/`, fixed at a tag of its repository. Clone with
it:

```sh
git clone --recurse-submodules https://github.com/nivaca/py-words-android.git
```

(or run `git submodule update --init` in a clone made without it). You need a JDK (17 or
newer), the Android SDK with platform 36, and Python 3.13 on the `PATH` as `python3.13`,
which the build uses to compile py-words to bytecode. Write the path of the SDK in
`local.properties` (`sdk.dir=/home/me/Android/Sdk`), or set `ANDROID_HOME`, and then:

```sh
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

The Gradle wrapper downloads the right Gradle, and the Chaquopy plugin downloads the
Python for Android. Besides Chaquopy, the project uses only the Android framework (no
AndroidX, no other libraries).

## Following py-words

The app carries a fixed copy of py-words, so each new py-words needs a new version of the
app. `tools/update-py-words.py` makes it and releases it:

```sh
python3 tools/update-py-words.py [--tag vX.YY] [--only-if-changed] [--dry-run] [--yes]
```

It moves the submodule to the newest tag of py-words (or to `--tag`), raises `versionCode`
and `versionName` (2.2 to 2.3), writes the new version of py-words in the READMEs, the
changelogs and `docs/`, and builds the signed APK; if the build fails, it undoes those
changes. Then it commits (`vVERSION: py-words X.YY`), signs the tag, pushes `main` and the
tag to `origin` (GitHub and Codeberg), and makes the release on each forge with the APK, its
`.asc` and the public key. The notes come from the changelog, where anything written under
`## Unreleased` joins the new entry. It asks before changing anything; `--dry-run` only
says what it would do, and `--only-if-changed` does nothing when, of what the app carries,
only the number of the version changed. It needs `gh`, `tea`, `gpg`, a clean `main` and the
signing keys of `keystore.properties`. If it stops after the commit, running it again
publishes what is missing.

`tools/release.py` of py-words runs it at the end of each release of py-words, so the app
follows py-words without anybody remembering it. On the phone,
[Obtainium](https://github.com/ImranR98/Obtainium) can watch the releases of this
repository and install each new APK over the old one.

## Releases and signing

`./gradlew assembleRelease` makes the release APK, shrunk with R8 (about 28 MB, nearly all
of it Python and the dictionary). It is signed only if the file `keystore.properties`
exists in the root of the project, with the keys `storeFile`, `storePassword`, `keyAlias`
and `keyPassword`; the key and that file are not in git. A signed APK is copied to
`dist/py-words-android-VERSION.apk`, replacing the older ones there. Without the file, the
release APK comes out unsigned and nothing is copied.

If `keystore.properties` also has `gpgKey`, the fingerprint of a gpg key, the build signs
the APK with it as well, in `dist/py-words-android-VERSION.apk.asc`. The releases are
signed with the key that signs the packages of py-words, whose public key is
[py-words-signing-key.asc](py-words-signing-key.asc) (fingerprint
`8187 0643 CA22 1AF9 0C30  554E BE68 32CD 3599 4948`); their tags are signed with it too.
To check a download:

```sh
gpg --import py-words-signing-key.asc
gpg --verify py-words-android-VERSION.apk.asc py-words-android-VERSION.apk
```

## F-Droid

The description, the icon, four screenshots and the notes of each version for F-Droid are in
`fastlane/metadata/android/` (in English and Spanish), where F-Droid looks for them. The
build recipe for the F-Droid repository is `fdroid/io.github.nivaca.pywords.yml`: it builds
the tag `vVERSION` from the folder `app`, with the submodule, and finds new versions by
their tags. It deletes `py-words/TAGS` (an Emacs tags file) before building, because
F-Droid's scanner takes it for a binary. F-Droid signs the apps with its own key, so its
APK and the one in the releases here cannot update each other.

## How it works

`MainActivity.kt` is the only screen: a WebView, the bar with the menu, and the screens for
loading and for errors. Online, it opens `https://py-words.uniandes.edu.co`. On this phone,
`LocalServer.kt` starts Python with [Chaquopy](https://chaquo.com/chaquopy/), and in it
`app/src/main/python/pywords_android.py` runs `public_app()` from py-words' `words_web.py`
(the same application as the site) on `127.0.0.1`, at a free port; the WebView opens that.
The build copies from the submodule only what this needs: the Python modules, `data/` and
two icons. `docs/DESCRIPTION.md` tells how it was made.

## License

py-words for Android is free software, under the GNU General Public License, version 3 or
later (`GPL-3.0-or-later`); see [LICENSE](LICENSE). py-words, which the app carries, has the
same license; its data has the licenses listed in its own documentation. Chaquopy is under
the MIT License, and Python under the Python Software Foundation License.
