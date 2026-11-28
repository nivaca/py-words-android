How py-words for Android was made
=================================

*[Leer en español](DESCRIPCIÓN_es.md)*

py-words for Android is an Android app for py-words, the Latin-English-Latin and
Latin-Spanish-Latin dictionary with inflectional morphology. It shows py-words from a copy
of the program that runs inside the app, without the Internet, or, if one asks for it in
the settings, from the site <https://py-words.uniandes.edu.co>. Nicolas Vaughan made it in November 2026. It came from the
Wiktionary Reader app, made the same month, which gave it its build files and its manner of
working. Version 1.0 only showed the site; version 2.0 added the copy on the phone, and
2.1 made it the default source; 2.2 is only for ARM devices and has a listing for F-Droid.
From 2.3 on, each release of py-words brings a new version of the app, made by a script;
after 2.4 the choice of the site left the menu for the settings. Here I explain how it was
made, in nine stages.

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
one. py-words enters the project as a git submodule, `py-words/`, fixed at a tag of its repository (now `v3.34`),
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

6. Only ARM, and F-Droid
------------------------

For F-Droid, which builds each app from its source on its own servers,
the app got a store listing in `fastlane/metadata/android/` (English and
Spanish) and a recipe in `fdroid/`.  Before sending it, I ran F-Droid's
own build of 2.1 in its build container.  Two things came out of that.
F-Droid's scanner stopped at `py-words/TAGS`, an Emacs tags file of the
submodule, which it takes for a binary because of its form feeds; the
recipe deletes it before building.  And Chaquopy found in that container
the `python3.13` it needs to compile py-words to bytecode, so the build
went through.

While taking screenshots for the store, the app closed every time it
started Python on the emulator (x86_64, Android 16), with a native error
("pthread_mutex_lock called on a destroyed mutex"); on the phone, an
ARM device, it works.  The emulator had run 2.0 well, so the cause is
not clear.  But the APK that F-Droid makes would be offered to x86_64
devices too, Chromebooks above all, so version 2.2 carries Python only
for `arm64-v8a`, the processor of nearly every Android phone and tablet.
The APK went down from about 42 MB to 28, and the release APK no
longer runs on the x86_64 emulator.  The build also stopped setting
`android.useAndroidX=false`, which the Android plugin now warns about.

7. Following py-words
---------------------

py-words 3.29 came out the day after 2.2, and the phone still had 3.28. The app cannot
update the copy it carries, since the copy is inside the APK: a new py-words means a new
version of the app. Doing that by hand each time (move the submodule, raise the version,
write the changelogs, build, sign, tag, release on two forges) is easy to forget, so I wrote
`tools/update-py-words.py` to do all of it, and made the release tool of py-words run it at
its end, with the tag just released.

The script finds the newest tag of py-words, moves the submodule to it, raises
`versionCode` and `versionName`, and writes the new version of py-words in the READMEs, the
changelogs and these two documents; what I wrote under "Unreleased" in a changelog goes
into the same entry. Then it builds the signed APK. If the build fails, it undoes its
changes, so the repository stays as it was. Otherwise it commits, signs the tag, pushes to
both forges and makes the releases, whose notes come from the changelog. A run that stopped
after the commit can be repeated, and it publishes what is missing.

I considered building in GitHub Actions instead, so that nothing would depend on my
computer. But that would put the signing key of the APK, and the OpenPGP key that also
signs py-words, in the secrets of GitHub, and a leak of them would let anybody publish
updates that phones accept. The keys stay on the computer where py-words is released,
which already holds them. A third way, an app that downloads py-words by itself, would need
no new versions at all; it would also need to check signatures at run time, and a first
start without the Internet would have nothing to run.

With 2.5 the script learnt two more things. The change of the menu was a change of the app
alone, with the same py-words, and the script only knew how to release a new py-words; now,
when py-words has no newer tag but the changelogs have an "Unreleased" section, it releases
those changes by themselves. And each release now carries `SHA256SUMS`, with the SHA-256
of the APK, and its OpenPGP signature, as my other projects do. Before it tags or pushes
anything, the script checks the signatures of the APK and of `SHA256SUMS` in a temporary
`GNUPGHOME` that holds only the published public key, the way someone who downloads them
would, and the signature of the tag; one that does not verify stops it. 2.5 was released
before that part, so the script also learnt to add the missing files to a release already
made, but only when the files it has are the same as those in `dist/`.

3.29 changed nothing that the app carries except the number of the version. The script
says so in the changelog, and `--only-if-changed` skips such releases. On the phone,
Obtainium watches the releases on GitHub and installs each new APK over the old one, since
all are signed with the same key.

8. The site, in the settings
-----------------------------

Until 2.4 the menu at the top offered the two sources side by side, Online and On this
phone, as if they were equal. They were not, after 2.1: the phone works anywhere and has
the newer py-words, and the site is only useful to someone who wants it in particular. So
I took the choice out of the menu, which now has Reload, Settings and, with the site, Open
in the browser. Settings is a small dialog of the app, separate from the settings of
py-words in its page, with one option, "Use the web page (py-words.uniandes.edu.co, needs
the Internet) instead of the dictionary on this phone", off unless one turns it on.
Changing it does what the menu did: the same search opens in the other source, and the
history is forgotten.

Whoever had chosen Online before keeps it, since the preference is the same one; the
option in Settings shows it ticked, and unticking it brings back the phone. The bar at the
top still says where the page comes from, and the error screen of the site still offers the
copy on the phone.

Trying it showed an old fault, which the menu had too: a change to the site while the
phone was still loading left "Loading the dictionary…" over the page. Now each change of
source hides that layer first.

9. Where to get it
------------------

Up to here the only way to get the app was a release: download the APK, or let Obtainium
follow the releases. The READMEs got an "Installing" section with a badge that adds the
app to Obtainium in one touch; the link passes through Obtainium's own redirect page,
which has analytics, so the README says so and gives the address to add by hand.

Then a repository of my own for F-Droid, `fdroid-repo`, a project next to the two apps and
published on Codeberg Pages (<https://nivaca.codeberg.page/fdroid/repo>). It offers the
same signed APKs as the releases, so the repository, the releases and Obtainium update one
another; its script checks each APK against the release and its signatures before adding
it. F-Droid's main repository builds from source and signs with its own key, and it does
not suit an APK that carries a prebuilt Python.

Two things joined the release script. It writes the notes of each version for the stores,
`fastlane/metadata/android/*/changelogs/VERSIONCODE.txt`, from the entry in the changelogs
(`tools/store_notes.py`: plain text, one line per item, within F-Droid's 500 characters);
until then they had stopped at 2.2, and F-Droid showed no "What's new". The notes of 2.3
to 2.6 were written the same way, afterwards. And at the end of a release it runs the
repository's `tools/update.py --publish`, so that F-Droid users get the new version too;
if that fails, it only warns, since the release is already made.

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
For 2.2, I ran F-Droid's build in its own container
(`fdroidserver:buildserver-trixie`), with the same steps as the checks
of F-Droid's repository, and checked that the APK carries only the
libraries for `arm64-v8a`.  Then I installed 2.2 on the phone over 2.1:
it started, looked up *amicorum* and *arma virumque cano* with Logeion,
and *friend* from English to Latin on the phone; those searches and the
menu of sources are the four screenshots of the store.

I tried `tools/update-py-words.py` in a clone of the repository, outside the real one:
with `--dry-run`, for 3.28 to 3.29, with `--only-if-changed` (which stopped, since only
`version.py` changed), and with an older tag (which it refuses); and the edits themselves,
whose diff I read, with and without an "Unreleased" section in the changelogs. For
`SHA256SUMS`, a dry run said that 2.5 lacked it; the real run made it, signed it, checked
the signatures with the public key alone and added the two files to both releases. Then I
downloaded them from GitHub and from Codeberg: on both, `sha256sum -c SHA256SUMS` passes,
and `gpg --verify` with only the published key finds a good signature.

For the move of the site to the settings, the app compiles without warnings and Android lint
reports no errors. On the emulator I opened the menu (Reload and Settings, and Open in the
browser only with the site), turned the site on while the phone was loading, which showed
the fault above and, after the fix, the page of the site; closed and opened the app, which
came back on the site with the option ticked; and turned it off, which brought back the
phone. The emulator is x86_64, where Python does not start, so the phone itself was not
tried there.

The project has 20 files under `app/` besides the build output: two Kotlin files of 434
lines, one Python file of 45, 272 lines of XML in the manifest, the resources and the
layout, and five PNG images of the icon. The build file of the app has 129 lines, and
`tools/update-py-words.py`, 631.
