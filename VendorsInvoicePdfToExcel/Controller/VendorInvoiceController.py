from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import uvicorn

from VendorsInvoicePdfToExcel.BusinessLogic.VendorInvoiceBl import VendorInvoiceBl

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        template_path = "../../TemplateVendorInvoices.xlsx"
        venforBl = VendorInvoiceBl()
        extractedInformation = venforBl.processPdf(tmp_pdf_path, vendor_name)
        excel_path = venforBl.fillExcelAndSave(template_path, extractedInformation)


        os.remove(tmp_pdf_path)
        return FileResponse(excel_path, filename=f"{os.path.basename(tmp_pdf_path)}.xlsx")

    except Exception as e:
        raise e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)