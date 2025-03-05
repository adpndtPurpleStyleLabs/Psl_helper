import os
import pytest
import json

try:
    from VendorsInvoicePdfToExcel.BusinessLogic.VendorInvoiceBl import VendorInvoiceBl
except ImportError as e:
    print(f"❌ Import Error: {e}")
    exit(1)

# FOLDER_NAME = "amit_agarwal/CUST"
FOLDER_NAME = "amit_agarwal/OR"

processor = VendorInvoiceBl()

SAVE_JSON_BASE_DIR = os.path.abspath("/Users/administrator/PycharmProjects/PslHelper/VendorInvoiceTest/test_invoice_json/")  # Ensure absolute path for consistency
BASE_DIR = os.path.abspath("/Users/administrator/PycharmProjects/PslHelper/VendorInvoiceTest/test_invoices/")  # Ensure absolute path for consistency
BASE_DIR = os.path.join(BASE_DIR, FOLDER_NAME)
SAVE_JSON_BASE_DIR =  os.path.join(SAVE_JSON_BASE_DIR, FOLDER_NAME)
if not os.path.isdir(BASE_DIR):
    print(f"❌ Error: The directory '{BASE_DIR}' does not exist.")
    exit(1)

@pytest.mark.parametrize("pdf_file, vendor", [
    (os.path.join(root, file), os.path.basename(root))
    for root, _, files in os.walk(BASE_DIR)
    for file in files if file.endswith(".pdf")
])

def test_process_pdf(pdf_file, vendor):
    result = processor.processPdf(pdf_file, "amit_agarwal")
    JSON_PATH = SAVE_JSON_BASE_DIR+"/"+pdf_file.split("/")[-1].replace(".pdf", ".json")
    for aItemInfo in result["items_info"]:
        if is_null_or_empty(aItemInfo["po_no"], "po_no") and is_null_or_empty(aItemInfo["or_po_no"], "or_po_no") :
            raise ValueError(f"po_no or or_po_no cannot be null or empty.")

        exception_on_null_or_empty(aItemInfo["HSN/SAC"], "HSN/SAC")
        exception_on_null_or_empty(aItemInfo["Qty"], "Qty")
        exception_on_null_or_empty(aItemInfo["Rate"], "Rate")
        exception_on_null_or_empty(aItemInfo["Per"], "Per")
        exception_on_null_or_empty(aItemInfo["mrp"], "mrp")
        exception_on_null_or_empty(aItemInfo["Amount"], "Amount")
        exception_on_null_or_empty(aItemInfo["gst_type"], "gst_type")
        exception_on_null_or_empty(aItemInfo["gst_rate"], "gst_rate")
        exception_on_null_or_empty(aItemInfo["tax_applied"], "tax_applied")
    exception_on_null_or_empty(result["total_tax"], "total_tax")
    exception_on_null_or_empty(result['items_total_info']['tax_amount_in_words'], "tax_amount_in_words")
    exception_on_null_or_empty(result['items_total_info']['amount_charged_in_words'], "amount_charged_in_words")
    exception_on_null_or_empty(result['items_total_info']['total_pcs'], "total_pcs")
    exception_on_null_or_empty(result['items_total_info']['total_amount_after_tax'], "total_amount_after_tax")
    exception_on_null_or_empty(result['items_total_info']['total_b4_tax'], "total_b4_tax")
    exception_on_null_or_empty(result['items_total_info']['total_tax'], "total_tax")
    exception_on_null_or_empty(result['items_total_info']['tax_rate'], "tax_rate")
    exception_on_null_or_empty(result['items_total_info']['total_tax_percentage'], "total_tax_percentage")


    exception_on_null_or_empty(result['vendor_info']['vendor_gst'], "vendor_gst")
    exception_on_null_or_empty(result['invoice_info']['invoice_number'], 'invoice_number')
    exception_on_null_or_empty(result['receiver_info']['receiver_gst'], 'receiver_gst')
    exception_on_null_or_empty(result['receiver_billing_info']['billto_gst'], 'billto_gst')

    if (is_null_or_empty(result['total_tax']['IGST'], "IGST")
            and is_null_or_empty(result['total_tax']['CGST'], "CGST")
            and is_null_or_empty(result['total_tax']['SGST'], "CSST")):
        raise ValueError(f"total_tax IGST and CGST  and SGST cannot be null or empty.")

    validate_previous_json(JSON_PATH, result)
    # save_json(JSON_PATH, result)
    assert result is not None, f"❌ Failed: {pdf_file} returned None"
    print(f"✅ Success: {pdf_file} processed correctly for vendor '{vendor}'.")


def is_null_or_empty(value, field_name):
    return  value is None or (isinstance(value, (str, list, tuple, dict, set)) and len(value) == 0)

def exception_on_null_or_empty(value, field_name):
    isNullOrEmpty =  value is None or (isinstance(value, (str, list, tuple, dict, set)) and len(value) == 0)
    if isNullOrEmpty:
        raise ValueError(f"{field_name} cannot be null or empty.")

def save_json(JSON_PATH, result):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def validate_previous_json(JSON_PATH, result):
    with open(JSON_PATH) as f:
        d = json.load(f)
        if d != result:
            raise ValueError(f"OLD JSON IS NOT SAME AS NEW JSON")