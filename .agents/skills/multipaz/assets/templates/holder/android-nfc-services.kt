// Reference: references/android-platform.md
// Sample anchor: samples/testapp/src/androidMain/kotlin/org/multipaz/testapp/TestAppCombinedNfcService.kt
// Multipaz NFC credential presentation is currently Android-only.

import kotlinx.io.bytestring.ByteString
import org.multipaz.compose.mdoc.CombinedNfcService
import org.multipaz.compose.mdoc.NfcApduService
import org.multipaz.nfc.Nfc

class YourCombinedNfcService : CombinedNfcService() {
    override fun buildServices(): Map<ByteString, NfcApduService> {
        return mapOf(
            Nfc.NDEF_APPLICATION_ID to YourMdocNdefService(this, ::sendResponseApdu),
            Nfc.MDOC_NFC_ENGAGEMENT_V2_AID to YourMdocNfcV2Service(this, ::sendResponseApdu),
            Nfc.ISO_MDOC_NFC_DATA_TRANSFER_APPLICATION_ID to YourMdocNfcDataTransferService(this, ::sendResponseApdu)
        )
    }
}
