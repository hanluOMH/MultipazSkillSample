# Android Platform

## Current NFC status

Multipaz NFC credential presentation is supported on Android in the current repository when the app includes the required services, manifest entries, and device capabilities.

## Verified repository anchors

- Manifest declarations: `samples/testapp/src/androidMain/AndroidManifest.xml`
- Combined APDU service: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppCombinedNfcService.kt`
- NDEF engagement service: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppMdocNdefService.kt`
- NFC v2 engagement service: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppMdocNfcV2Service.kt`
- Digital Credentials API activity: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppCredentialManagerPresentmentActivity.kt`
- URI-scheme presentment activity: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppUriSchemePresentmentActivity.kt`

## Verified requirements to inspect

- `android.permission.NFC`
- `android.hardware.nfc`
- `android.permission.BIND_NFC_SERVICE` on the APDU services
- activity and service registration in the Android manifest
- NFC adapter and lifecycle handling in app code
- physical-device availability for runtime testing

## Source-set rules

- Keep Android NFC code in `androidMain` or Android application modules.
- Do not move APDU services, `PresentmentActivity`, or Android manifest wiring into `commonMain`.

## Validation

- Compile Android sources after edits.
- Check manifest declarations.
- Note that runtime NFC behavior usually needs physical hardware.
