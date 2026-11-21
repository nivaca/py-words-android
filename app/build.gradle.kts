// SPDX-License-Identifier: GPL-3.0-or-later
import java.util.Properties

plugins {
    id("com.android.application")
    id("com.chaquo.python")
}

// La clave de firma está fuera de git, en keystore.properties (véase el
// README).  Sin ese archivo la versión release sale sin firmar.
val keystoreFile = rootProject.file("keystore.properties")
val keystore = Properties().apply {
    if (keystoreFile.isFile) keystoreFile.inputStream().use { load(it) }
}

android {
    namespace = "io.github.nivaca.pywords"
    compileSdk = 36

    defaultConfig {
        applicationId = "io.github.nivaca.pywords"
        minSdk = 29
        targetSdk = 36
        versionCode = 2
        versionName = "2.0"

        // Python 3.12 and later run only on 64-bit devices; x86_64 is for
        // the emulator.
        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    signingConfigs {
        if (keystoreFile.isFile) {
            create("release") {
                storeFile = rootProject.file(keystore.getProperty("storeFile"))
                storePassword = keystore.getProperty("storePassword")
                keyAlias = keystore.getProperty("keyAlias")
                keyPassword = keystore.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.findByName("release")
        }
    }

    // Without this block nothing encrypted with a Google key goes in the APK.
    dependenciesInfo {
        includeInApk = false
        includeInBundle = false
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// py-words en el teléfono: el submódulo py-words/ (el repositorio de
// GitHub, en una etiqueta de versión), del que se copian solo los módulos de
// Python, los datos y los dos iconos que muestra la página.  Lo demás
// (pruebas, manuales, empaquetado) no hace falta en la app.
val pyWords = rootProject.file("py-words")
val pyWordsOut = layout.buildDirectory.dir("generated/py-words")
val copyPyWords = tasks.register<Sync>("copyPyWords") {
    from(pyWords) {
        include("*.py", "data/**", "icons/uniandes.svg",
                "icons/linux/icons/hicolor/48x48/apps/py-words.png")
        exclude("words_gui.py", "words_tui.py", "words_edit_gui.py", "gui_*.py", "tui.py")
    }
    into(pyWordsOut)
    doFirst {
        check(File(pyWords, "words_web.py").isFile) {
            "py-words/ is empty: run git submodule update --init"
        }
    }
}

chaquopy {
    defaultConfig {
        version = "3.13"          // py-words needs 3.13 for now
    }
    sourceSets {
        getByName("main") {
            srcDir(pyWordsOut)
        }
    }
}
tasks.matching { it.name.contains("Python", ignoreCase = true) && it.name != "copyPyWords" }
    .configureEach { dependsOn(copyPyWords) }

// Al final de cada versión release firmada, el APK se copia también a
// dist/ como py-words-android-VERSIÓN.apk, en lugar de los anteriores, para
// que dist/ tenga siempre el más nuevo.  Sin firma no se copia nada.
val distApk = tasks.register("distApk") {
    doLast {
        val version = android.defaultConfig.versionName
        val apk = layout.buildDirectory.file("outputs/apk/release/app-release.apk").get().asFile
        if (!apk.isFile) return@doLast
        val dist = rootProject.file("dist")
        dist.mkdirs()
        dist.listFiles { f -> f.name.startsWith("py-words-android-") && f.name.endsWith(".apk") }?.forEach { it.delete() }
        apk.copyTo(File(dist, "py-words-android-$version.apk"), overwrite = true)
        println("dist/py-words-android-$version.apk")
    }
}
tasks.matching { it.name == "assembleRelease" }.configureEach { finalizedBy(distApk) }
