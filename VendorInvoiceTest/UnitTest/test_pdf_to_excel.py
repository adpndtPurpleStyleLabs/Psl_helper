import os
import pytest

try:
    from VendorsInvoicePdfToExcel.BusinessLogic.VendorInvoiceBl import VendorInvoiceBl
except ImportError as e:
    print(f"❌ Import Error: {e}")
    exit(1)

processor = VendorInvoiceBl()

BASE_DIR = os.path.abspath("/Users/administrator/PycharmProjects/PslHelper/VendorInvoiceTest/test_invoices/seema_gujral")  # Ensure absolute path for consistency

if not os.path.isdir(BASE_DIR):
    print(f"❌ Error: The directory '{BASE_DIR}' does not exist.")
    exit(1)

@pytest.mark.parametrize("pdf_file, vendor", [
    (os.path.join(root, file), os.path.basename(root))
    for root, _, files in os.walk(BASE_DIR)
    for file in files if file.endswith(".pdf")
])
def test_process_pdf(pdf_file, vendor):
    result = processor.processPdf(pdf_file, vendor)

    assert result is not None, f"❌ Failed: {pdf_file} returned None"
    print(f"✅ Success: {pdf_file} processed correctly for vendor '{vendor}'.")
