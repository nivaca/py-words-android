How py-words for Android was made
=================================

*[Leer en español](DESCRIPCIÓN_es.md)*

py-words for Android is a small Android app for the web version of py-words, the
Latin-English-Latin and Latin-Spanish-Latin dictionary with inflectional morphology, which
runs at <https://py-words.uniandes.edu.co>. Nicolas Vaughan made it in November 2026. It
came from the Wiktionary Reader app, made the same month, which gave it its build files and
its manner of working; but where Wiktionary Reader builds its own pages, this one only shows
the site, so it is much smaller. The current version is 1.0. Here I explain how it was made,
in four stages.

py-words for Android is free software, under the GNU General Public License, version 3 or
later. It uses only the Android framework and the Kotlin standard library (under the Apache
License 2.0), with no other libraries. The dictionary and its data belong to py-words, with
their own licenses, which the site shows under "About".

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

Testing
-------

There are no automatic tests; the app is a frame around a site, and almost all the
behaviour that matters belongs to the site. I checked it by hand on the Android emulator
(Android 16), with screenshots taken through adb: the home page; a word sent from the
selection menu (*amicorum*, *rosa*, *lupus*); the back gesture to the home page and out of
the app; the error screen with Wi-Fi and mobile data off, and the button that loads the
same search when the connection returns; dark mode, both when starting and when changing
with the app open; and the settings of the site, which survived closing the app. Android
lint reports no errors, and the Kotlin compiler no warnings. The release APK, shrunk with
R8 and signed, is 57 KB.

The project has 16 files under `app/` besides the build output: one Kotlin file of 242
lines, 161 lines of XML in the manifest, the resources and the layout, and five PNG
images of the icon.
