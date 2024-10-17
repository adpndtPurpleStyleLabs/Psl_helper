from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import pandas as pd
import os
import tempfile
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify specific origins like ['http://localhost:8000'] if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allows all headers (or specific headers you expect)
)


@app.post("/pdf-to-excel/")  # POST method is defined here
async def pdf_to_excel(
    file: UploadFile = File(...),
    vendor_name: str = Form(...),
    file_path: str = Form(None)
):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(await file.read())
            tmp_pdf_path = tmp_pdf.name


        all_tables = getTablesFromPdf(tmp_pdf_path)
        new_tables = []
        if vendor_name == "amit":
            new_tables = processForAmit(all_tables)
        else:
            return {"error": str(vendor_name + " is not a valid vendor")}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_excel:
            excel_path = tmp_excel.name

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df = pd.DataFrame(new_tables)
            df.to_excel(writer, sheet_name=f'Sheet1', index=False)

        os.remove(tmp_pdf_path)

        return FileResponse(excel_path, filename=f"{vendor_name}_tables.xlsx")

    except Exception as e:
        return {"error": str(e)}


def getTablesFromPdf(tmp_pdf_path):
    all_tables = []
    with pdfplumber.open(tmp_pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    all_tables.append(table)
    return all_tables

def processForAmit(all_tables):
    new_tables =[]
    isFirstProcessed = False
    for table in all_tables:
        if table[0][0] == '07':
            continue
        if isFirstProcessed:
            table.pop(0)
            table.pop(0)
            new_tables = new_tables + table
        else:
            isFirstProcessed = True
            new_tables = new_tables + table
    return new_tables


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
