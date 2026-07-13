# Troubleshooting

## Method

1. Inspect the project and dependency layout.
2. Reproduce the failure at the narrowest module or platform boundary.
3. Check whether the code path is shared, Android-only, or iOS-only.
4. Compare against the closest matching Multipaz sample or test.
5. Verify trust, storage, and transport assumptions separately.

## Common failure classes

- wrong or mixed Multipaz versions
- missing Android manifest entries
- Android-only APIs referenced from `commonMain` or `iosMain`
- unsupported iOS NFC assumptions
- missing redirect or URI-scheme configuration for OpenID4VCI or OpenID4VP
- trust-chain or certificate mismatch
- secure-area or storage setup mismatch

## Helpful anchors

- Dependency problems: `python3 -B scripts/check_multipaz_dependencies.py`
- Android manifest and service wiring: `samples/testapp/src/androidMain/AndroidManifest.xml`
- iOS supported presentment paths: `samples/SwiftTestApp/SwiftTestApp/Iso18013ProximityPresentmentScreen.swift`
- Trust and certificate examples: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/ConsentPromptScreen.kt`
