How py-words for Android was made
=================================

*[Leer en español](DESCRIPCIÓN_es.md)*

py-words for Android is an Android app for py-words, the Latin-English-Latin and
Latin-Spanish-Latin dictionary with inflectional morphology. It shows py-words either from
the site <https://py-words.uniandes.edu.co> or from a copy of the program that runs inside
the app, without the Internet. Nicolas Vaughan made it in November 2026. It came from the
Wiktionary Reader app, made the same month, which gave it its build files and its manner of
working. Version 1.0 only showed the site; version 2.0 added the copy on the phone, and
2.1, the current one, made it the default source. Here I explain how it was made, in five
stages.

py-words for Android is free software, under the GNU General Public License, version 3 or
later. It uses the Android framework, the Kotlin standard library (under the Apache License
2.0) and Chaquopy (under the MIT License), which brings Python (under the Python Software
Foundation License). The app carries py-words, under the same GPL, whose data has its own
licenses, shown under "About" in its page.

Nicolas Vaughan is Associate Professor of Literature at the School of Arts and Humanities
of the Universidad de los Andes, Bogotá, Colombia.

1. A first version
------------------

The request was simple: an Android app that is only a frontend to the site. Before writing
anything I looked at what the site sends. It is a page made on the server, with ordinary
forms (`GET /?q=…` for a search, `POST` for the settings), a cookie that keeps the settings
and the earlier searches for a year, and a Content-Security-Policy that lets only its own
scripts run. Its stylesheet already has a dark version under
`prefers-color-scheme: dark`. Nothing there asked for more than a WebView.

So the app is one activity, `MainActivity.kt`, with a WebView over the whole screen, a thin
progress bar on top, and a screen for when the site cannot be reached. I took the Gradle
files, the theme and the handling of the system bars from Wiktionary Reader: the same
versions of Gradle and of the Android plugin, Android 10 as the minimum, and no AndroidX.
The window pads itself by the system bars and the keyboard, because since Android 15 it
fills the whole screen.

The WebView keeps in the app every `https` link to `py-words.uniandes.edu.co`; any other
link (the author's page, the commit on GitHub) goes to the browser. The cookie is written to
disk when the app goes to the background, so a setting changed on the site is not lost if
Android closes the app.

2. Words from other apps
------------------------

As in Wiktionary Reader, the app appears in the menu of selected text ("Look up in
py-words") and accepts shared text. Both turn into a search, `/?q=WORD`, which is the same
address as the examples on the home page. A text of more than 500 characters is ignored,
since it is not a search but a paragraph pasted by mistake. The app also offers to open
links to the site, without claiming them: it does not verify the domain, so Android asks
the user.

3. The icon
-----------

The icon is the one of py-words (`icons/py-words.svg`). For the adaptive icon of Android I
took out its dark background, which becomes the background colour (`#292929`), and reduced
the rest to fit the safe zone, the circle that every launcher keeps. Inkscape exports it as
PNG at the five densities. A first look at the result showed that the text, "py-" and
"Words", and the open book stay readable even in the smallest size.

4. Back, and dark mode
----------------------

The first tests on the emulator showed two problems. When the system changed to dark mode
with the app open, the page changed but the icons of the status bar did not, because the
activity was declared to handle that change itself and kept its light theme. I removed
`uiMode` from the changes it handles, so Android creates the activity again, and the
WebView saves its state (the page and its history) and restores it.

That raised the second problem. Since Android 13, the back gesture must be claimed in
advance; the app claims it only while the WebView has a page to go back to, and the claim
was made only when the history changed. After the activity is created again, the restored
history did not trigger that, so I made the app check it once at the start too. Before
Android 13, `onBackPressed` does the same work.

5. py-words on the phone
------------------------

Version 1.0 was useless without the Internet, and the question came soon: could the app
run py-words from its GitHub repository instead of the site? Not by fetching code at run
time, but by carrying it. py-words needs nothing outside the standard library of Python,
and its web page is a WSGI application, `public_app()` in `words_web.py`, the one the site
itself runs, which keeps each visitor's settings in cookies and writes nothing on the
server. So the plan was to run that same application inside the app, on `127.0.0.1`, and
point the WebView at it.

Python on Android comes from Chaquopy, a Gradle plugin that puts CPython in the APK. Its
version 17.2 supports the Android plugin 9.5 of the project and Python 3.13, which py-words
needs for now; Python 3.12 and later run only on 64-bit devices, so the app now asks for
one. py-words enters the project as a git submodule, `py-words/`, fixed at the tag `v3.28`,
and a Gradle task copies from it only what the server needs: the Python modules (not the
window or the terminal, which need tkinter or curses, absent on Android), `data/` and the
two icons that the page shows. Chaquopy compiles them to bytecode with the `python3.13` of
the build machine.

A short module of the app, `pywords_android.py`, starts the server once per process, in a
thread of its own, at a free port, after pointing the cache of py-words to the cache folder
of Android and leaving the configuration and the history out of the disk. `LocalServer.kt`
starts Python and calls it in the background, because loading the dictionary takes time:
on the desktop, 1.9 seconds the first time, while the pickle cache of py-words is made,
and 0.4 afterwards. On the emulator it was about 11 seconds the first time (Chaquopy also
unpacks the 38 MB of data) and 6 afterwards; meanwhile the app shows "Loading the
dictionary…". The WebView needs permission to speak plain HTTP to `127.0.0.1`, and only
there, which a network security configuration gives.

The screen gained a thin bar at the top, with the source of py-words (and, on the phone,
its version) and a menu to change it. Changing the source keeps the search on the screen,
and forgets the history, so that Back does not jump from one source to the other. When the
site cannot be reached, the error screen offers the copy on the phone. The source chosen
is kept in the preferences of the app. In 2.0 a new install started online; after trying
it on a phone, I made the phone the default in 2.1, since it works anywhere and is the
newer py-words, and only those who choose Online keep it. From 2.1 on, the releases are also signed with
OpenPGP, with the key that signs the packages of py-words: the tag, and the APK in an
`.asc` file that the build makes when `keystore.properties` names the key; the 1.0 and 2.0
releases got their `.asc` files afterwards. The state of the
WebView is restored only for the same server, since the port changes each time Android
closes the app.

The price is size: the APK went from 57 KB to about 42 MB, nearly all of it the Python
runtime and the dictionary.

Testing
-------

There are no automatic tests of the app; py-words has its own, and almost all the
behaviour that matters belongs to it. I checked the app by hand on the Android emulator
(Android 16), with screenshots taken through adb. For 1.0: the home page; a word sent from
the selection menu (*amicorum*, *rosa*, *lupus*); the back gesture to the home page and out
of the app; the error screen with Wi-Fi and mobile data off, and the button that loads the
same search when the connection returns; dark mode, both when starting and when changing
with the app open; and the settings of the site, which survived closing the app. For 2.0:
the change from online to the phone and back, with the search kept (*amicorum*, *arma
virumque cano*); the first start on the phone and a later one; a search on the phone with
Wi-Fi and mobile data off; dark mode on the phone; Back after a change of source; the
button of the error screen that changes to the phone; and the signed release APK, shrunk
with R8, on the phone source. Then I installed the release APK of 2.0 on a moto g55 5G with
Android 16, in dark mode, and repeated the main steps there: a word online; the change to
the phone, whose first start took about 12 seconds; a later start with airplane mode on
(*arma virumque cano*), which took under 4 seconds and gave the whole line without the
Internet; the change back online with the search kept (*lupus*), and the turn of the
screen to landscape. Android lint reports no errors, and the Kotlin compiler no warnings.

The project has 20 files under `app/` besides the build output: two Kotlin files of 414
lines, one Python file of 45, 270 lines of XML in the manifest, the resources and the
layout, and five PNG images of the icon. The build file of the app has 114 lines.
