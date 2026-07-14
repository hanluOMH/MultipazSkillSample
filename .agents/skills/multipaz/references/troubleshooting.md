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
- OpenID4VCI offer appears in the app but tapping issue does nothing: inspect device logs first, then check Android Multipaz context initialization, internet permission, Ktor engine, OAuth challenge handling, redirect intent filter, and issuer trust in that order.
- `NullPointerException` in `ContextUtil.getApplicationContext`: Android app did not call `initializeApplication(applicationContext)` before using Multipaz `Platform` storage or secure-area helpers.
- `Permission denied (missing INTERNET permission?)`: Android manifest is missing `android.permission.INTERNET`.
- `CA not registered: trusted_client_attestations...`: the issuer does not trust the wallet attestation key. Use a registered wallet backend, trusted sample keys for Multipaz demo issuers, or configure a local issuer to trust the test key.
- `Failed to find HTTP client engine implementation`: Ktor core is present but no platform engine is on the runtime classpath. Add the Android, Darwin, CIO, or other appropriate Ktor client engine in the correct source set and prefer explicit engine construction.
- `signedAt cannot have fractional seconds`: mdoc/MSO timestamps were created from `Clock.System.now()` without truncating to whole seconds. Normalize issue and validity times before encoding.
- `NoSuchProviderException: no such provider: AndroidKeyStore` in host tests: the host JVM cannot use Android Keystore. Inject `SoftwareSecureArea` for host tests or run a connected Android device test.
- Android log lines like `hiddenapi: Accessing hidden method ... allowed` are warnings when marked `allowed`; do not treat them as the root cause unless paired with a real exception.
- trust-chain or certificate mismatch
- secure-area or storage setup mismatch

## Helpful anchors

- Dependency problems: `python3 -B scripts/check_multipaz_dependencies.py`
- Android manifest and service wiring: `samples/testapp/src/androidMain/AndroidManifest.xml`
- iOS supported presentment paths: `samples/SwiftTestApp/SwiftTestApp/Iso18013ProximityPresentmentScreen.swift`
- Trust and certificate examples: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/ConsentPromptScreen.kt`
