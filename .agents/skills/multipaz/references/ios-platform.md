# iOS Platform

## Current NFC status

Multipaz NFC credential presentation is currently not supported on iOS.

## Required implications

- Do not generate Multipaz NFC presentation code for iOS.
- Adding `CoreNFC` or an NFC entitlement does not create Multipaz NFC presentation support.
- Do not copy Android NFC APIs or Android service logic into `iosMain` or shared code.
- Do not claim that a common cross-platform NFC implementation works for both Android and iOS.

## Verified repository anchors

- iOS QR-based proximity presentment: `samples/SwiftTestApp/SwiftTestApp/Iso18013ProximityPresentmentScreen.swift`
- iOS Identity Document integration: `samples/SwiftTestApp/IdentityDocumentProviderExtension/DocumentProviderExtension.swift`
- Swift provisioning support: `samples/SwiftTestApp/SwiftTestApp/ProvisioningSupport.swift`
- KMP `iosMain` sources in the sample app: `samples/testapp/src/iosMain`

## Supported-alternative workflow

When the user asks for iOS presentment, verify the requested version and prefer one of:

- QR-based presentment
- BLE-backed proximity where the selected version and app actually support it
- browser or URI/deep-link initiated flows
- W3C Digital Credentials / Identity Document integration

## Validation focus

- Verify the supported iOS mechanism actually used by the project.
- Inspect plist, associated domains, and extension entitlements only for supported iOS features.
