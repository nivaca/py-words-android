#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pone en la app la versión más nueva de py-words y publica la versión
de la app que la lleva, en GitHub (con gh) y en Codeberg (con tea).

    python3 tools/update-py-words.py [--tag vX.YY] [--only-if-changed]
                                     [--dry-run] [--yes]

En orden:

1. comprueba que el repositorio esté en main, sin nada por confirmar, que
   gh, tea y gpg estén instalados y que keystore.properties nombre la clave
   de firma del APK y la de gpg (gpgKey);
2. trae las etiquetas de py-words y elige la más nueva (o la de --tag).  Si
   el submódulo ya está en ella y los registros de cambios tienen una
   sección «Unreleased» / «Sin publicar», publica una versión de la app con
   esos cambios y el mismo py-words (los pasos 4 a 7, sin mover el
   submódulo); si no la tienen, no hay nada que hacer, salvo publicar una
   versión de la app que haya quedado a medias (véase abajo);
3. con --only-if-changed, se detiene si de una etiqueta a otra no cambió
   nada de lo que la app lleva (los módulos de Python, data/, los dos
   iconos), fuera del número de versión;
4. mueve el submódulo a la etiqueta, sube versionCode y versionName (2.2 →
   2.3), y pone la versión nueva de py-words en los README, en los
   registros de cambios y en los documentos de docs/;
5. compila el APK firmado (./gradlew assembleRelease, que lo copia a dist/
   con su firma de OpenPGP; gpg pide la frase de paso).  Si la compilación
   falla, deshace los cambios del paso 4;
6. confirma los cambios («vVERSIÓN: py-words X.YY»), escribe
   dist/SHA256SUMS (el SHA-256 del APK) con su firma, y comprueba las firmas
   del APK y de SHA256SUMS como lo haría quien los descargue: en un
   GNUPGHOME temporal que solo tiene la clave pública que se publica.  Si
   una no se comprueba, se detiene.  Luego pone la etiqueta firmada
   vVERSIÓN, la comprueba con git tag --verify en otro GNUPGHOME temporal
   con solo esa clave, y sube main y la etiqueta a origin (que sube a
   GitHub y a Codeberg);
7. crea la versión en cada forja, con el APK, SHA256SUMS, sus firmas y la
   clave pública.  A una versión ya publicada le añade los archivos que le
   falten en cualquiera de las dos forjas (así recibió la 2.5 su
   SHA256SUMS), siempre que los que ya tiene en GitHub sean los mismos que
   hay en dist/.

Antes del paso 4 muestra lo que va a hacer y pregunta; con --yes no
pregunta, y con --dry-run solo lo muestra.  Si algo falla después del
paso 6, correr el script de nuevo publica lo que falte: el submódulo ya
está en la etiqueta, y HEAD es la confirmación de la versión.

tools/release.py de py-words corre este script al final de cada versión de
py-words, así que la app la sigue sin que haya que acordarse.
"""

import argparse
import datetime
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMODULE = 'py-words'
GRADLE = os.path.join('app', 'build.gradle.kts')
SIGNING_KEY = 'py-words-signing-key.asc'
BRANCH = 'main'
SUMS = os.path.join('dist', 'SHA256SUMS')
TEA_LOGIN = 'codeberg'

DESCRIPTION = ('Put the newest py-words in the app, and release the version '
               'of the app that carries it on GitHub and Codeberg.')

# Lo que la compilación copia del submódulo (véase copyPyWords en
# app/build.gradle.kts): solo esto cuenta como cambio para --only-if-changed.
BUNDLED_ICONS = ('icons/uniandes.svg',
                 'icons/linux/icons/hicolor/48x48/apps/py-words.png')
NOT_BUNDLED = re.compile(r'^(words_gui|words_tui|words_edit_gui|gui_.*|tui)'
                         r'\.py$')

CHANGELOG_URL = 'https://github.com/nivaca/py-words/blob/main/'


def run(*command, check=True, capture=True, cwd=ROOT) -> str:
    out = subprocess.run(command, cwd=cwd, text=True,
                         capture_output=capture)
    if check and out.returncode != 0:
        detail = (out.stderr or out.stdout or '').strip() if capture else ''
        sys.exit(f'update-py-words: {shlex.join(command)} failed'
                 + (f': {detail}' if detail else ''))
    return (out.stdout or '').strip() if capture else ''


def ok(*command) -> bool:
    """True if COMMAND succeeds (its output is thrown away)."""
    return subprocess.run(command, cwd=ROOT, capture_output=True
                          ).returncode == 0


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def write(path: str, text: str):
    with open(os.path.join(ROOT, path), 'w', encoding='utf-8') as f:
        f.write(text)


def substitute(path: str, pattern: str, replacement, count=1):
    """Replace PATTERN in PATH; stop if it is not there, since then the
    text changed and this script must change with it."""
    text, n = re.subn(pattern, replacement, read(path), count=count,
                      flags=re.MULTILINE)
    if n == 0:
        sys.exit(f'update-py-words: {path}: did not find /{pattern}/')
    write(path, text)


def keystore() -> dict:
    path = os.path.join(ROOT, 'keystore.properties')
    if not os.path.isfile(path):
        sys.exit('update-py-words: there is no keystore.properties, so the '
                 'APK would not be signed (see the README)')
    props = {}
    for line in read('keystore.properties').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.split('=', 1)
            props[k.strip()] = v.strip()
    for k in ('storeFile', 'storePassword', 'keyAlias', 'keyPassword',
              'gpgKey'):
        if not props.get(k):
            sys.exit(f'update-py-words: keystore.properties has no {k}')
    return props


def apksigner() -> str:
    """apksigner of the newest build-tools of the SDK (local.properties or
    ANDROID_HOME, as Gradle finds it)."""
    sdk = os.environ.get('ANDROID_HOME', '')
    path = os.path.join(ROOT, 'local.properties')
    if os.path.isfile(path):
        m = re.search(r'^sdk\.dir=(.+)$', read('local.properties'),
                      re.MULTILINE)
        sdk = m[1].strip() if m else sdk
    tools = os.path.join(sdk, 'build-tools')
    versions = sorted((v for v in os.listdir(tools) if re.fullmatch(
        r'[\d.]+', v)), key=lambda v: tuple(map(int, v.split('.')))
    ) if sdk and os.path.isdir(tools) else []
    for v in reversed(versions):
        found = os.path.join(tools, v, 'apksigner')
        if os.path.isfile(found):
            return found
    sys.exit('update-py-words: no apksigner in the build-tools of the SDK')


def tag_version(tag: str) -> tuple:
    return tuple(int(n) for n in tag[1:].split('.'))


def app_version() -> tuple[int, str]:
    text = read(GRADLE)
    code = re.search(r'versionCode = (\d+)', text)
    name = re.search(r'versionName = "([\d.]+)"', text)
    if not code or not name:
        sys.exit(f'update-py-words: no versionCode or versionName in {GRADLE}')
    return int(code[1]), name[1]


def next_name(name: str) -> str:
    # 2.2 → 2.3; 2.9 → 2.10, como py-words (3.9 → 3.10)
    major, minor = name.split('.')[:2]
    return f'{major}.{int(minor) + 1}'


class Update:

    def __init__(self, args):
        self.args = args
        self.keys = {}

    # Comprobaciones -----------------------------------------------------

    def check(self):
        for tool in ('git', 'gh', 'tea', 'gpg'):
            if not shutil.which(tool):
                sys.exit(f'update-py-words: {tool} is not installed')
        self.keys = keystore()
        if not ok('gpg', '--batch', '--list-secret-keys',
                  self.keys['gpgKey']):
            sys.exit(f'update-py-words: the gpg key {self.keys["gpgKey"]} is '
                     "not in this machine's keyring")
        branch = run('git', 'rev-parse', '--abbrev-ref', 'HEAD')
        if branch != BRANCH:
            sys.exit(f'update-py-words: on branch {branch}, not {BRANCH}')
        if not os.path.isfile(os.path.join(ROOT, SUBMODULE, 'version.py')):
            sys.exit('update-py-words: py-words/ is empty: run git '
                     'submodule update --init')
        if run('git', 'status', '--porcelain'):
            message = 'there are changes not committed (see git status)'
            if not self.args.dry_run:
                sys.exit(f'update-py-words: {message}')
            print(f'update-py-words: (dry run) {message}', file=sys.stderr)

    def tags(self) -> tuple[str, str]:
        """(the tag of the submodule now, the tag to move it to)."""
        sub = os.path.join(ROOT, SUBMODULE)
        run('git', 'fetch', '--quiet', '--tags', 'origin', cwd=sub)
        current = run('git', 'describe', '--tags', '--exact-match', 'HEAD',
                      cwd=sub, check=False)
        if not re.fullmatch(r'v\d+\.\d+', current):
            sys.exit('update-py-words: the submodule is not at a tag of '
                     f'py-words ({current or "no tag"})')
        if self.args.tag:
            target = self.args.tag
            if not ok('git', '-C', SUBMODULE, 'rev-parse', '--verify',
                      '--quiet', f'refs/tags/{target}'):
                sys.exit(f'update-py-words: py-words has no tag {target}')
        else:
            tags = [t for t in run('git', 'tag', cwd=sub).split()
                    if re.fullmatch(r'v\d+\.\d+', t)]
            target = max(tags, key=tag_version)
        if tag_version(target) < tag_version(current):
            sys.exit(f'update-py-words: {target} is older than {current}, '
                     'where the submodule is')
        return current, target

    def bundled_changes(self, current: str, target: str) -> list[str]:
        """The files that the app carries and that changed, besides
        version.py."""
        names = run('git', 'diff', '--name-only', current, target,
                    cwd=os.path.join(ROOT, SUBMODULE)).split('\n')
        return [n for n in names if n and n != 'version.py' and (
            n.startswith('data/') or n in BUNDLED_ICONS or
            ('/' not in n and n.endswith('.py') and not NOT_BUNDLED.match(n)))]

    # Paso 4: los cambios en los archivos --------------------------------

    def bump(self, code: int, name: str):
        """The new version in the build file and in the title of the
        Spanish description."""
        substitute(GRADLE, r'versionCode = \d+', f'versionCode = {code}')
        substitute(GRADLE, r'versionName = "[\d.]+"',
                   f'versionName = "{name}"')
        substitute('docs/DESCRIPCIÓN_es.md',
                   r'^# py-words para Android [\d.]+: descripción',
                   f'# py-words para Android {name}: descripción')

    def edit(self, current: str, target: str, code: int, name: str,
             same: bool):
        old, new = current[1:], target[1:]
        run('git', 'checkout', '--quiet', target,
            cwd=os.path.join(ROOT, SUBMODULE))
        self.bump(code, name)
        substitute('README.md', r'\(now py-words [\d.]+\)',
                   f'(now py-words {new})')
        substitute('README.es.md', r'\(ahora py-words [\d.]+\)',
                   f'(ahora py-words {new})')
        substitute('docs/DESCRIPTION.md', r'(today|now) `v[\d.]+`',
                   rf'\1 `{target}`')
        substitute('docs/DESCRIPCIÓN_es.md', r'hoy `v[\d.]+`',
                   f'hoy `{target}`')
        today = datetime.date.today().isoformat()
        en = (f'- py-words {new}, in place of {old} ([its changes]'
              f'({CHANGELOG_URL}CHANGELOG.md)).')
        es = (f'- py-words {new}, en lugar de la {old} ([sus cambios]'
              f'({CHANGELOG_URL}CHANGELOG_es.md)).')
        if same:
            en += (f' The dictionary and its page are the same as in {old}; '
                   'only the number of the version changed.')
            es += (f' El diccionario y su página son los mismos de la {old}; '
                   'solo cambió el número de la versión.')
        for path, item, pending in (('CHANGELOG.md', en, 'Unreleased'),
                                    ('CHANGELOG_es.md', es, 'Sin publicar')):
            text = read(path)
            heading = f'## {name} — {today}'
            if re.search(rf'^## {pending}$', text, re.MULTILINE):
                # Lo escrito a mano bajo «Unreleased» pasa a ser de esta
                # versión, con py-words al principio de su lista.
                text = re.sub(rf'^## {pending}\n\n', lambda m: f'{heading}'
                              f'\n\n{wrap(item)}\n', text, count=1,
                              flags=re.MULTILINE)
                write(path, text)
            else:
                # La entrada nueva va antes de la primera versión de la lista.
                substitute(path, r'^## ', lambda m, item=item:
                           f'{heading}\n\n{wrap(item)}\n\n## ')
        run('git', 'add', SUBMODULE, GRADLE, 'README.md', 'README.es.md',
            'CHANGELOG.md', 'CHANGELOG_es.md', 'docs/DESCRIPTION.md',
            'docs/DESCRIPCIÓN_es.md')

    def edit_app(self, code: int, name: str):
        """A version of the app alone: the sections «Unreleased» and «Sin
        publicar» become its entries."""
        self.bump(code, name)
        heading = f'## {name} — {datetime.date.today().isoformat()}'
        for path, pending in (('CHANGELOG.md', 'Unreleased'),
                              ('CHANGELOG_es.md', 'Sin publicar')):
            substitute(path, rf'^## {pending}$', heading)
        run('git', 'add', GRADLE, 'CHANGELOG.md', 'CHANGELOG_es.md',
            'docs/DESCRIPCIÓN_es.md')

    def undo(self, current: str):
        run('git', 'reset', '--quiet', 'HEAD', check=False)
        run('git', 'checkout', '--quiet', '--', '.', check=False)
        run('git', 'checkout', '--quiet', current,
            cwd=os.path.join(ROOT, SUBMODULE), check=False)

    # Pasos 5 a 7 --------------------------------------------------------

    def build(self):
        gradlew = os.path.join(ROOT, 'gradlew')
        return subprocess.run([gradlew, 'assembleRelease'],
                              cwd=ROOT).returncode == 0

    def files(self, name: str) -> list[str]:
        apk = os.path.join('dist', f'py-words-android-{name}.apk')
        return [apk, apk + '.asc', SUMS, SUMS + '.asc', SIGNING_KEY]

    def sign_sums(self, name: str):
        """dist/SHA256SUMS of the APK and its signature; then every signature
        is checked with only the published public key."""
        apk = self.files(name)[0]
        for f in (apk, apk + '.asc'):
            if not os.path.isfile(os.path.join(ROOT, f)):
                sys.exit(f'update-py-words: there is no {f}')
        sums = f'{sha256(apk)}  {os.path.basename(apk)}\n'
        # Si una corrida anterior ya los hizo (y quizá los subió), se
        # conservan: otra firma del mismo texto sería otro archivo.
        if not (os.path.isfile(os.path.join(ROOT, SUMS + '.asc'))
                and os.path.isfile(os.path.join(ROOT, SUMS))
                and read(SUMS) == sums):
            write(SUMS, sums)
            run('gpg', '--batch', '--yes', '--local-user',
                self.keys['gpgKey'], '--armor', '--detach-sign', '--output',
                SUMS + '.asc', SUMS, capture=False)
        failed = []
        with tempfile.TemporaryDirectory(prefix='update-py-words-') as home:
            os.chmod(home, 0o700)
            env = {'GNUPGHOME': home, 'PATH': '/usr/bin:/bin'}
            subprocess.run(['gpg', '--batch', '--quiet', '--import',
                            SIGNING_KEY], cwd=ROOT, env=env, check=True,
                           capture_output=True)
            for f in (apk, SUMS):
                done = subprocess.run(['gpg', '--batch', '--verify',
                                       f + '.asc', f], cwd=ROOT, env=env,
                                      capture_output=True, text=True)
                if done.returncode != 0:
                    failed.append(f)
            # Un GNUPGHOME nuevo puede arrancar gpg-agent o keyboxd: se
            # detienen antes de borrar la carpeta.
            subprocess.run(['gpgconf', '--kill', 'all'], env=env,
                           capture_output=True)
        if failed:
            sys.exit('update-py-words: these do not verify with '
                     f'{SIGNING_KEY}: {", ".join(failed)}')
        print(f'Signed and verified with {SIGNING_KEY}: '
              f'{os.path.basename(apk)}, {os.path.basename(SUMS)}')

    def verify_tag(self, tag: str):
        """Stop unless the signature of TAG verifies with only the
        published public key, as a user would check it."""
        with tempfile.TemporaryDirectory(prefix='update-py-words-') as home:
            os.chmod(home, 0o700)
            env = {'GNUPGHOME': home, 'PATH': '/usr/bin:/bin'}
            subprocess.run(['gpg', '--batch', '--quiet', '--import',
                            SIGNING_KEY], cwd=ROOT, env=env, check=True,
                           capture_output=True)
            done = subprocess.run(['git', 'tag', '--verify', tag], cwd=ROOT,
                                  env=env, capture_output=True, text=True)
            subprocess.run(['gpgconf', '--kill', 'all'], env=env,
                           capture_output=True)
        if done.returncode != 0:
            sys.exit(f'update-py-words: the signature of the tag {tag} does '
                     f'not verify with {SIGNING_KEY}')
        print(f'Verified with {SIGNING_KEY}: the tag {tag}')

    def notes(self, name: str, new: str, apk: str) -> str:
        with open(os.path.join(ROOT, apk), 'rb') as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        cert = re.search(r'certificate SHA-256 digest: ([0-9a-f]{64})', run(
            apksigner(), 'verify', '--print-certs', apk))
        if not cert:
            sys.exit(f'update-py-words: apksigner shows no certificate in {apk}')
        cert = cert[1]
        fpr = re.sub(r'(.{4})', r'\1 ', self.keys['gpgKey'].replace(' ', ''))
        fpr = fpr[:24] + ' ' + fpr[24:].rstrip()
        # Lo nuevo es la entrada de esta versión en CHANGELOG.md, con cada
        # punto de la lista en una sola línea.
        entry = re.search(rf'^## {re.escape(name)} — .*?\n\n(.*?)(?=^## |\Z)',
                          read('CHANGELOG.md'), re.MULTILINE | re.DOTALL)
        what = re.sub(r'\n  +', ' ', entry[1].strip()) if entry else (
            f'- py-words {new}.')
        return f'''\
py-words for Android shows [py-words](https://github.com/nivaca/py-words), \
the Latin-English-Latin and Latin-Spanish-Latin dictionary with inflectional \
morphology, from a copy of py-words {new} that runs inside the app, without \
the Internet, or, if one chooses it in the settings of the app, from the site \
<https://py-words.uniandes.edu.co>.

What is new in {name}:

{what}

It needs a 64-bit ARM device with Android 10 or newer.

**Install:** download `py-words-android-{name}.apk` and open it on the phone \
(Android will ask to allow installs from that source). It is signed with the \
same key as the earlier versions, so it installs over them. To get each new \
version by itself, add this repository to Obtainium.

**Verify:**

```
SHA-256 of the APK:            {sha}
SHA-256 of the signing cert:   {cert}
OpenPGP key:                   {fpr}
```

The OpenPGP signatures are checked with:

```
gpg --import {SIGNING_KEY}
gpg --verify py-words-android-{name}.apk.asc py-words-android-{name}.apk
gpg --verify SHA256SUMS.asc SHA256SUMS
sha256sum -c SHA256SUMS
```

The tag `v{name}` is signed with the same key.

Free software, under the GNU General Public License, version 3 or later. It \
also carries Python (Python Software Foundation License) through Chaquopy \
(MIT License).
'''

    def publish(self, name: str, new: str):
        tag = f'v{name}'
        files = self.files(name)
        self.sign_sums(name)
        for f in files:
            if not os.path.isfile(os.path.join(ROOT, f)):
                sys.exit(f'update-py-words: there is no {f}')
        if not ok('git', 'rev-parse', '--verify', '--quiet',
                  f'refs/tags/{tag}'):
            run('git', 'tag', '--sign', '--local-user', self.keys['gpgKey'],
                '--message', f'py-words for Android {name}', tag,
                capture=False)
        self.verify_tag(tag)
        run('git', 'push', 'origin', BRANCH, capture=False)
        run('git', 'push', 'origin', f'refs/tags/{tag}', capture=False)
        title = f'py-words for Android {name}'
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False,
                                         encoding='utf-8') as f:
            f.write(self.notes(name, new, files[0]))
            notes = f.name
        try:
            if ok('gh', 'release', 'view', tag):
                self.add_missing_github(tag, files)
            else:
                run('gh', 'release', 'create', tag, *files, '--title', title,
                    '--notes-file', notes, '--verify-tag', capture=False)
            repo = 'nivaca/py-words-android'
            listed = run('tea', 'releases', 'ls', '--repo', repo, '--login',
                         TEA_LOGIN, '--output', 'simple')
            if re.search(rf'^{re.escape(tag)}\b', listed, re.MULTILINE):
                self.add_missing_codeberg(tag, repo, files)
            else:
                assets = [a for f in files for a in ('--asset', f)]
                run('tea', 'releases', 'create', '--repo', repo, '--login',
                    TEA_LOGIN, '--tag', tag, '--title', title, '--note-file',
                    notes, *assets, capture=False)
        finally:
            os.unlink(notes)
        print(f'\nReleased py-words for Android {name}, with py-words {new}.')

    def add_missing_github(self, tag: str, files: list[str]):
        """Uploads to a release already made the files it lacks, if the ones
        it has are those in dist/."""
        have = dict(line.split(' ', 1) for line in run(
            'gh', 'release', 'view', tag, '--json', 'assets', '--jq',
            '.assets[] | "\\(.name) \\(.digest)"').splitlines() if line)
        for f in files:
            digest = have.get(os.path.basename(f))
            if digest and digest != f'sha256:{sha256(f)}':
                sys.exit(f'update-py-words: GitHub {tag} has another '
                         f'{os.path.basename(f)} than {f}: nothing added')
        missing = [f for f in files if os.path.basename(f) not in have]
        if not missing:
            print(f'GitHub: {tag} is already released')
            return
        run('gh', 'release', 'upload', tag, *missing, capture=False)
        print(f'GitHub: added to {tag}: '
              + ', '.join(os.path.basename(f) for f in missing))

    def codeberg_assets(self, tag: str) -> set | None:
        """The names of the files of the release TAG on Codeberg, or None
        if there is no such release."""
        repo = 'nivaca/py-words-android'
        listed = run('tea', 'releases', 'ls', '--repo', repo, '--login',
                     TEA_LOGIN, '--output', 'simple')
        if not re.search(rf'^{re.escape(tag)}\b', listed, re.MULTILINE):
            return None
        return set(re.findall(r'\S+', run(
            'tea', 'releases', 'assets', 'ls', '--repo', repo, '--login',
            TEA_LOGIN, '--output', 'simple', tag)))

    def add_missing_codeberg(self, tag: str, repo: str, files: list[str]):
        names = self.codeberg_assets(tag) or set()
        missing = [f for f in files if os.path.basename(f) not in names]
        if not missing:
            print(f'Codeberg: {tag} is already released')
            return
        run('tea', 'releases', 'assets', 'create', '--repo', repo, '--login',
            TEA_LOGIN, tag, *missing, capture=False)
        print(f'Codeberg: added to {tag}: '
              + ', '.join(os.path.basename(f) for f in missing))

    # Todo ---------------------------------------------------------------

    def ask(self, text: str):
        print(text)
        if self.args.dry_run:
            sys.exit(0)
        if not self.args.yes:
            answer = input('Go on? [y/N] ').strip().lower()
            if answer not in ('y', 'yes', 's', 'sí', 'si'):
                sys.exit('Nothing done.')

    def resume(self, current: str):
        """The submodule is already at the newest tag: publish the version
        of the app if a run before stopped half-way."""
        code, name = app_version()
        subject = run('git', 'log', '-1', '--format=%s')
        # «vX.Y: py-words A.B», o «vX.Y: py-words A.B; …» si solo cambió la app.
        # (o una versión ya etiquetada, a la que pueden faltarle archivos)
        if not re.fullmatch(rf'v{re.escape(name)}: py-words '
                            rf'{re.escape(current[1:])}(;.*)?', subject) \
                and not ok('git', 'rev-parse', '--verify', '--quiet',
                           f'refs/tags/v{name}'):
            print(f'The app already carries py-words {current[1:]}.')
            return
        if ok('gh', 'release', 'view', f'v{name}'):
            have = run('gh', 'release', 'view', f'v{name}', '--json',
                       'assets', '--jq', '.assets[].name').split()
            # También Codeberg: una subida pudo fallar allí sola.
            codeberg = self.codeberg_assets(f'v{name}')
            if codeberg is not None and all(
                    os.path.basename(f) in have and
                    os.path.basename(f) in codeberg
                    for f in self.files(name)):
                print(f'The app already carries py-words {current[1:]}, and '
                      f'v{name} is released.')
                return
            if not os.path.isfile(os.path.join(ROOT, self.files(name)[0])):
                sys.exit(f'update-py-words: v{name} lacks files, and there is '
                         f'no {self.files(name)[0]} to make them from')
            self.ask(f'v{name} is released, but not on both forges with all '
                     'its files (SHA256SUMS, perhaps): make what is missing, '
                     'sign it and add it.')
            self.publish(name, current[1:])
            return
        self.ask(f'v{name} (py-words {current[1:]}) is committed but not '
                 'released: tag it, push it and release it.')
        # El APK pudo no llegar a dist/ si la vez anterior falló al compilar.
        if not os.path.isfile(os.path.join(ROOT, self.files(name)[0])):
            if not self.build():
                sys.exit('update-py-words: the build failed')
        self.publish(name, current[1:])

    def __call__(self):
        self.check()
        current, target = self.tags()
        if current == target:
            if re.search(r'^## Unreleased$', read('CHANGELOG.md'),
                         re.MULTILINE):
                self.release_app(current)
            else:
                self.resume(current)
            return
        changed = self.bundled_changes(current, target)
        same = not changed
        if same and self.args.only_if_changed:
            print(f'From {current} to {target}, nothing that the app carries '
                  'changed but the number of the version: nothing done.')
            return
        code, name = app_version()
        code, name = code + 1, next_name(name)
        self.ask(
            f'py-words {current[1:]} → {target[1:]}; the app {name} '
            f'(versionCode {code}).\n'
            + (f'Files of the app that change: {len(changed)}.\n' if changed
               else 'Of what the app carries, only version.py changes.\n')
            + 'Build the signed APK, commit, tag, push to origin, and '
            'release on GitHub and Codeberg.')
        self.edit(current, target, code, name, same)
        if not self.build():
            self.undo(current)
            sys.exit('update-py-words: the build failed; the changes are '
                     'undone')
        run('git', 'commit', '--quiet', '--message',
            f'v{name}: py-words {target[1:]}')
        self.publish(name, target[1:])

    def release_app(self, current: str):
        """py-words is the same; what changed is the app (the sections
        «Unreleased» of the changelogs)."""
        if not re.search(r'^## Sin publicar$', read('CHANGELOG_es.md'),
                         re.MULTILINE):
            sys.exit('update-py-words: CHANGELOG.md has an "Unreleased" '
                     'section, but CHANGELOG_es.md has no "Sin publicar"')
        code, name = app_version()
        code, name = code + 1, next_name(name)
        self.ask(
            f'py-words stays at {current[1:]}; the app {name} (versionCode '
            f'{code}) releases the "Unreleased" changes of the changelogs.\n'
            'Build the signed APK, commit, tag, push to origin, and '
            'release on GitHub and Codeberg.')
        self.edit_app(code, name)
        if not self.build():
            self.undo(current)
            sys.exit('update-py-words: the build failed; the changes are '
                     'undone')
        run('git', 'commit', '--quiet', '--message',
            f'v{name}: py-words {current[1:]}; changes of the app')
        self.publish(name, current[1:])


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def wrap(item: str, width=72) -> str:
    """A list item wrapped as in the changelogs, with its lines indented."""
    lines, line = [], ''
    for word in item.split(' '):
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = '  ' + word
        else:
            line = f'{line} {word}' if line else word
    return '\n'.join(lines + [line])


def main(argv=None):
    parser = argparse.ArgumentParser(prog='tools/update-py-words.py',
                                     description=DESCRIPTION)
    parser.add_argument('--tag', metavar='vX.YY',
                        help='the tag of py-words to carry (default: the '
                             'newest)')
    parser.add_argument('--only-if-changed', action='store_true',
                        help='do nothing if, of what the app carries, only '
                             'the number of the version changed')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='only say what would be done')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='do not ask before doing it')
    Update(parser.parse_args(argv))()


if __name__ == '__main__':
    main()
