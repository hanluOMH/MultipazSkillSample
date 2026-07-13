# Credential Issuance

## Use this when

- creating or importing credentials into a wallet
- adding provisioning UI
- wiring secure storage and document store setup

## Repository anchors

- Compose provisioning UI: `multipaz-compose/src/commonMain/kotlin/org/multipaz/compose/provisioning/ProvisioningBottomSheet.kt`
- Swift OpenID4VCI provisioning support: `samples/SwiftTestApp/SwiftTestApp/ProvisioningSupport.swift`
- Test app document creation and secure-area selection: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/DocumentStoreScreen.kt`

## Normal sequence

1. Create or obtain storage.
2. Build or obtain a `SecureArea` and `SecureAreaRepository`.
3. Build a `DocumentStore`.
4. Configure document types and wallet domains.
5. Add the provisioning or issuance workflow.
6. Validate secure storage and trust handling.

## Security requirements

- Sample-only local backends or embedded keys must be clearly marked as non-production. `ProvisioningSupport.swift` embeds keys and explicitly explains that this is not real-world safe.
- Never move sample private keys into production code.
