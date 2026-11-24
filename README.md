# py-words for Android

*[Leer en español](README.es.md)* · [Changelog](CHANGELOG.md)

py-words for Android is an Android app for
[py-words](https://github.com/nivaca/py-words), the Latin-English-Latin and
Latin-Spanish-Latin dictionary with inflectional morphology. It shows py-words itself,
which runs inside the app, without the Internet: the app carries a copy of the program and
its data (now py-words 3.30) and a Python 3.13 to run it.

In the settings of the app you can choose the web page instead, the site
<https://py-words.uniandes.edu.co>, which needs the Internet. Both show the same page, with
the same searches, results and settings; the app is only a window for it.

I am Nicolas Vaughan (<nicolasvaughan@proton.me>), and I wrote it in 2026.

## Installing

The signed APK of each version is in the releases, on
[GitHub](https://github.com/nivaca/py-words-android/releases) and
[Codeberg](https://codeberg.org/nivaca/py-words-android/releases).

[![Get it on Obtainium](docs/img/badge_obtainium.png)](https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/%7B%22id%22%3A%22io.github.nivaca.pywords%22%2C%22url%22%3A%22https%3A%2F%2Fgithub.com%2Fnivaca%2Fpy-words-android%22%2C%22author%22%3A%22nivaca%22%2C%22name%22%3A%22py-words%22%7D)

With [Obtainium](https://github.com/ImranR98/Obtainium) the phone installs the newest release
and then each new one over the old. The badge adds the app to Obtainium in one touch, if
Obtainium is installed (the link passes through Obtainium's own redirect page, which has
analytics); without it, add the app in Obtainium by hand, with the address
`https://github.com/nivaca/py-words-android`.

It is also in my own F-Droid repository, with the same signed APKs, so each one updates the
other: in F-Droid (or Droid-ify, Neo Store), add the repository
`https://nivaca.codeberg.page/fdroid/repo`, whose key has the fingerprint
`E930B855E234BD2DE4F083D454DA0195549005D91A89309F9A3E5510D71E2E46`;
the page <https://nivaca.codeberg.page/fdroid/> adds it in one touch.

## What it does

- py-words full screen, under a thin bar that says where it comes from, in light or dark
  mode as the system says.
- The menu (⋮): **Reload**, **Settings** and, with the web page, **Open in the browser**.
  In **Settings**, "Use the web page" changes the source; the search on the screen is
  kept.
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
tag to `origin` (GitHub and Codeberg), and makes the release on each forge with the APK,
`SHA256SUMS`, their `.asc` and the public key. Before it tags or pushes anything, it checks
the signatures of the APK and of `SHA256SUMS` as a user would, in a temporary `GNUPGHOME`
with only the public key, and the signature of the tag; if one fails, nothing is published.
The notes come from the changelog, where anything written under `## Unreleased` joins the
new entry. When py-words has no newer tag but the changelogs have an `## Unreleased`
section, it releases those changes of the app alone, with the same py-words. A release
already made that lacks a file (as 2.5 lacked `SHA256SUMS`) gets it, if the files it has
are those in `dist/`. It asks before changing anything; `--dry-run` only
says what it would do, and `--only-if-changed` does nothing when, of what the app carries,
only the number of the version changed. It needs `gh`, `tea`, `gpg`, a clean `main` and the
signing keys of `keystore.properties`. If it stops after the commit, running it again
publishes what is missing.

`tools/release.py` of py-words runs it at the end of each release of py-words, so the app
follows py-words without anybody remembering it.

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

Since 2.5 each release also has `SHA256SUMS`, with the SHA-256 of the APK, and its signature:

```sh
gpg --verify SHA256SUMS.asc SHA256SUMS
sha256sum -c SHA256SUMS
```

## F-Droid

The description, the icon, four screenshots and the notes of each version for F-Droid are in
`fastlane/metadata/android/` (in English and Spanish), where F-Droid looks for them. The
build recipe for the F-Droid repository is `fdroid/io.github.nivaca.pywords.yml`: it builds
the tag `vVERSION` from the folder `app`, with the submodule, and finds new versions by
their tags. It deletes `py-words/TAGS` (an Emacs tags file) before building, because
F-Droid's scanner takes it for a binary. F-Droid signs the apps with its own key, so its
APK and the one in the releases here cannot update each other.

The notes of each version are written by the release script, from the changelogs
(`tools/store_notes.py`). The app is also in my own F-Droid repository (see "Installing"),
which offers the signed APKs of the releases themselves, so that it, the releases and
Obtainium do update one another; the release script publishes each new version there. Its
source is [nivaca/fdroid](https://codeberg.org/nivaca/fdroid) on Codeberg.

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
