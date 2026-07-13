# Project Inspection

## First pass

Run:

```bash
python3 -B .agents/skills/multipaz/scripts/inspect_multipaz_project.py [project-path]
```

The script should tell you:

- Gradle wrapper version
- Kotlin, AGP, Compose, and Multipaz versions when discoverable
- KMP targets and modules
- source sets
- version catalogs and included builds
- existing Multipaz dependencies
- Android manifests, iOS plist files, and entitlements
- Android NFC declarations
- suspicious iOS NFC-related configuration that does not imply support

## Manual follow-up

- Read `settings.gradle.kts` to verify included modules and composite builds.
- Read the target module `build.gradle.kts` files to see whether the app already exports iOS frameworks, uses Compose, or depends on `multipaz-dcapi`.
- Check whether the app already has holder, verifier, or issuer code paths.

## Classification hints

- Holder app: document store, secure area, provisioning, consent, or presentment source logic.
- Verifier app: request construction, OpenID4VP, DCQL, or device retrieval.
- Issuer/provisioning: OpenID4VCI, attestation, redirect handling, backend RPC.
- Platform work: manifests, activities, entitlements, `iosMain`, or native SwiftUI integration.

## NFC-specific inspection

- Android: verify `android.permission.NFC`, `android.hardware.nfc`, `android.permission.BIND_NFC_SERVICE`, and APDU services.
- iOS: treat any `CoreNFC` import or entitlement as a warning signal only. It does not prove Multipaz iOS NFC presentment support.
