# OpenID4VCI

## Use this when

- adding credential offer handling
- implementing redirect handling and wallet provisioning
- wiring backend assertions, attestations, or local test stubs

## Repository anchors

- Wallet-side sample support: `samples/SwiftTestApp/SwiftTestApp/ProvisioningSupport.swift`
- Compose provisioning UI: `multipaz-compose/src/commonMain/kotlin/org/multipaz/compose/provisioning/ProvisioningBottomSheet.kt`
- Backend implementation example: `multipaz-backend-server/src/main/java/org/multipaz/backend/openid4vci/OpenID4VCIBackendImpl.kt`
- Module: `multipaz-openid4vci`

## Guidance

- Inspect the current Multipaz version and the target project's redirect/deep-link setup before changing code.
- Treat local or embedded backend keys as sample-only.
- Separate backend responsibilities from app code unless the task explicitly targets a local test stub.

## Validation

- Confirm the app accepts the expected offer URI schemes or HTTPS redirects.
- Verify secure-area and storage setup before debugging provisioning failures.
