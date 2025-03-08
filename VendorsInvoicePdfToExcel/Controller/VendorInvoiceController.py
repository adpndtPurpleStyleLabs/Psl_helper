from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
import os
import tempfile
import uvicorn
import requests
import json

from VendorsInvoicePdfToExcel.BusinessLogic.VendorInvoiceBl import VendorInvoiceBl

WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAAJs0u1JQ/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=C-NZB4YfjhxmApsm2css9_m57mEzN6Auu_eZMWcWqjM"
GCHAT_LOG = os.environ.get("GCHAT_LOG", "true")

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.post("/pdf-to-excel/")
async def pdf_to_excel(
    file: UploadFile = File(...),
    vendor_name: str = Form(...),
    file_path: str = Form(None)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(await file.read())
            tmp_pdf_path = tmp_pdf.name

        template_path = "/Users/administrator/PycharmProjects/PslHelper/VendorsInvoicePdfToExcel/TemplateVendorInvoices.xlsx"
        # template_path = "/app/VendorsInvoicePdfToExcel/TemplateVendorInvoices.xlsx"
        venforBl = VendorInvoiceBl()
        extractedInformation = venforBl.processPdf(tmp_pdf_path, vendor_name)
        excel_path = venforBl.fillExcelAndSave(template_path, extractedInformation,vendor_name)


        os.remove(tmp_pdf_path)
        return FileResponse(excel_path, filename=f"{os.path.basename(tmp_pdf_path)}.xlsx")

    except Exception as e:
        raise e

@app.post("/parse-pdf/")
async def parse_pdf(
    file: UploadFile = File(...),
    vendor_name: str = Form(...),
    po_type: str = Form(...),
    file_path: str = Form(None)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(await file.read())
            tmp_pdf_path = tmp_pdf.name

        venforBl = VendorInvoiceBl()
        extractedInformation = venforBl.processPdf(tmp_pdf_path, vendor_name)
        os.remove(tmp_pdf_path)
        send_log_to_g_chat(vendor_name, file.filename, "PASSED")
        return extractedInformation

    except Exception as e:
        error = {
            "isSuccess": False,
            "msg": str(e) + " ,Invalid or Wrong invoice pdf format for designer " + vendor_name
        }
        try:
            error["msg"] = e.detail + " ,Invalid or Wrong invoice pdf format for designer " + vendor_name

        except:
            print(str(e))
        send_log_to_g_chat(vendor_name + str(error) , file.filename, "FAILED")
        return error

def send_log_to_g_chat(vendor_name, pdf_name, status):
    if GCHAT_LOG != "true":
        return
    try:
        headers = {"Content-Type": "application/json"}
        emoji = "✅" if status.upper() == "PASSED" else "❌"
        message = f"{emoji} **Status:** {status}\n📁 **Vendor:** {vendor_name}\n📄 **PDF:** {pdf_name}"
        data = json.dumps({"text": message})
        response = requests.post(WEBHOOK_URL, headers=headers, data=data)
        if response.status_code == 200:
            print("✅ Log sent successfully!")
        else:
            print(f"❌ Error sending log: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)