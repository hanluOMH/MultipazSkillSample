# Proximity Presentation

## Separation of concerns

- Engagement method: QR or NFC tap
- Transport: BLE, NFC data transfer, or other negotiated transport
- Session establishment: creation of the presentment session and handover
- Credential retrieval and presentation: document selection, consent, trust checks, and response generation

Do not collapse these into one concept.

## Current repository evidence

- Android QR and consent flow logic: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/ConsentPromptScreen.kt`
- Android NFC service wiring: `samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppCombinedNfcService.kt`
- Android NDEF and NFC v2 services: `TestAppMdocNdefService.kt`, `TestAppMdocNfcV2Service.kt`
- iOS QR presentment sample: `samples/SwiftTestApp/SwiftTestApp/Iso18013ProximityPresentmentScreen.swift`

## Platform support

| Capability | Android | iOS |
| --- | --- | --- |
| Multipaz NFC credential presentation | Supported | Not currently supported |
| QR-based proximity presentment | Verify in selected app/version | Verify in selected app/version |
| BLE-based proximity transport | Verify in selected app/version | Verify in selected app/version |

## Required rules

- NFC presentation is currently Android-only.
- Do not generate iOS NFC presentation code.
- BLE and QR support must be verified separately for the selected version and app architecture.
- NFC and BLE are not interchangeable.
- Protocol and session logic may be shared, but transport and engagement code stays platform specific.

## Implementation sequence

1. Choose the protocol and request model.
2. Choose the engagement mechanism.
3. Verify transport support in the current module set.
4. Keep shared document and consent logic in common code.
5. Keep Android NFC services, manifest, and lifecycle integration in Android code.
6. Keep iOS to supported alternatives such as QR, BLE-backed flows, browser, or Identity Document services.
