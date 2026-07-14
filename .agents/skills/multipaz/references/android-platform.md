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

## Android holder and issuance requirements

- Call `org.multipaz.context.initializeApplication(applicationContext)` from Android app startup before shared wallet initialization touches `Platform.storage`, `Platform.nonBackedUpStorage`, or secure areas.
- Add `android.permission.INTERNET` for any real issuer, verifier, or metadata fetch.
- For OpenID4VCI custom scheme offers, add an intent filter for the credential-offer scheme and dispatch both `onCreate` and `onNewIntent` data.
- For OAuth authorization-code offers, add a redirect scheme or app link that exactly matches the client metadata sent to the issuer. Use `singleTop` or equivalent routing when needed so the redirect reaches the existing activity.
- Keep Android browser launching and redirect capture in Android code. Shared code may expose an `expect` authorization function, but the `actual` implementation should own `Intent.ACTION_VIEW` and redirect completion.

## Verified requirements to inspect

- `android.permission.NFC`
- `android.hardware.nfc`
- `android.permission.BIND_NFC_SERVICE` on the APDU services
- activity and service registration in the Android manifest
- NFC adapter and lifecycle handling in app code
- OpenID4VCI offer and OAuth redirect intent filters when issuance is in scope
- physical-device availability for runtime testing

## Source-set rules

- Keep Android NFC code in `androidMain` or Android application modules.
- Do not move APDU services, `PresentmentActivity`, or Android manifest wiring into `commonMain`.
- Keep Android app context initialization, browser intents, and Android URI dispatch in Android-specific source sets or the Android app module.

## Validation

- Compile Android sources after edits.
- Check manifest declarations.
- For issuance, run a device smoke test with a real offer when possible: offer received, browser opened, redirect returned, document stored.
- Note that runtime NFC behavior usually needs physical hardware.
