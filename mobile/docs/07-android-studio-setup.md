# 07. Android Studio Setup & Native Project Guide

## 1. Directory Location
The native Android project is structured in:
`mobile/android/`

This directory is ready to be opened directly in **Android Studio**.

---

## 2. Prerequisites
1. **Android Studio:** Latest Hedgehog, Iguana, or Koala release.
2. **Android SDK:**
   - Android SDK Platform 34 (API Level 34)
   - Android SDK Build-Tools 34.0.0
   - Android SDK Command-line Tools
3. **Java Development Kit (JDK):** JDK 17 (recommended: Android Studio's bundled JBR 17).
4. **Environment Variables:**
   - `ANDROID_HOME` pointing to `C:\Users\<username>\AppData\Local\Android\Sdk`
   - `%ANDROID_HOME%\platform-tools` added to your system `PATH`.

---

## 3. Opening the Project in Android Studio
1. Launch **Android Studio**.
2. Select **Open an Existing Project**.
3. Browse to and select `C:\ess\ess_sample_2\mobile\android`.
4. Allow Android Studio to sync the Gradle project.
5. If prompted, confirm using Gradle 8+ with Android Gradle Plugin 8.3+.

---

## 4. Network Configuration for Local Development
- Inside the Android emulator, your workstation is reachable at `http://10.0.2.2:8000/api`.
- The Android project includes `android:usesCleartextTraffic="true"` in `AndroidManifest.xml` to allow cleartext HTTP communication with local development servers.
- When running on a physical Android device connected via USB or Wi-Fi, ensure your phone and computer are on the same Wi-Fi network and update the API base URL in the app settings or `src/config/index.ts` to your PC's LAN IP (e.g. `http://192.168.1.50:8000/api`).
- Alternatively, run `adb reverse tcp:8000 tcp:8000` via terminal to map the device's port 8000 directly to your PC's port 8000!

---

## 5. Running the Application

### 5.1 Starting Metro Bundler
In the `mobile` directory:
```bash
npm start
```

### 5.2 Launching on Android Emulator or Device
From Android Studio:
- Click the green **Run 'app'** button (Shift + F10) targeting your connected device or AVD.

Or from CLI:
```bash
npx react-native run-android
```

---

## 6. Building Debug and Release APKs

### 6.1 Debug APK
To assemble a debug APK from command line:
```bash
cd mobile/android
./gradlew assembleDebug
```
The output APK will be placed at:
`mobile/android/app/build/outputs/apk/debug/app-debug.apk`

### 6.2 Release APK
To assemble a release APK:
```bash
cd mobile/android
./gradlew assembleRelease
```
The signed APK will be generated at:
`mobile/android/app/build/outputs/apk/release/app-release.apk`
