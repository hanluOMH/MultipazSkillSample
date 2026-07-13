# DCQL

## Use this when

- creating verifier requests
- converting canned requests into DCQL
- debugging request mismatch issues

## Repository anchors

- DCQL examples in the test app: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/ConsentPromptScreen.kt`
- Request construction screen: `samples/testapp/src/commonMain/kotlin/org/multipaz/testapp/ui/DcRequestScreen.kt`
- Android matcher implementation: `multipaz-dcapi/src/androidMain/matcher`

## Guidance

- Treat DCQL as a query language layered into verifier or presentment protocols.
- Verify the requested credential format and doc type metadata before generating a query.
- Keep examples version-matched to the current request model.
