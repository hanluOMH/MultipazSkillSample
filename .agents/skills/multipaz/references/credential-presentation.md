# Credential Presentation

## Use this when

- implementing wallet presentment
- building consent and presentment-source logic
- adding QR, BLE, browser, or Digital Credentials entry points

## Current supported sample paths

- Shared consent and request handling: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/ConsentPromptScreen.kt`
- Android URI-scheme presentment: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppUriSchemePresentmentActivity.kt`
- Android Digital Credentials presentment: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppCredentialManagerPresentmentActivity.kt`
- iOS QR-based proximity presentment: `samples/SwiftTestApp/SwiftTestApp/Iso18013ProximityPresentmentScreen.swift`
- iOS Identity Document provider flow: `samples/SwiftTestApp/IdentityDocumentProviderExtension/DocumentProviderExtension.swift`

## Keep these distinctions clear

- OpenID4VP is a protocol, not a transport.
- DCQL is a query language, not a transport.
- QR and BLE are engagement or transport mechanisms depending on the flow.
- NFC credential presentation is currently Android-only in Multipaz.

## Validation

- Verify that the selected presentment mechanism exists in the current Multipaz version and sample set.
- For Android NFC, validate compile-time integration and note that runtime behavior usually needs physical hardware.
