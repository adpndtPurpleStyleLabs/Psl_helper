import pdfplumber
import openpyxl
import shutil
from fastapi import HTTPException
from openpyxl.styles import Font
from VendorsInvoicePdfToExcel.ImplementationFactory import ImplementationFactory
import datetime
import tabula
import io
import re

class VendorInvoiceBl:
    def extractTextFromPdf(self, file_path):
        page_text_dict = {}
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    page_text_dict[page_num] = page_text

        return page_text_dict

    def extract_tables_from_pdf(self, pdf_path):
        tables_data = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_number in range(len(pdf.pages)):
                page = pdf.pages[page_number]
                table = page.extract_table()
                if table:
                    cleaned_table = [[cell for cell in row if cell is not None] for row in table]
                    tables_data[page_number + 1] = cleaned_table

        return tables_data

    def extract_tables_from_pdf_using_tabula(self, pdfPath):
        tables_by_page = {}
        with pdfplumber.open(pdfPath) as pdf:
            for page_number in range(len(pdf.pages)):
                tables = tabula.read_pdf(pdfPath, pages=page_number, multiple_tables=True)
                csv_list = []
                for i, table in enumerate(tables):
                    csv_buffer = io.StringIO()
                    table.to_csv(csv_buffer, index=False, sep='$')
                    csv_data = csv_buffer.getvalue()  # Get CSV data as a string
                    csv_list.append(csv_data)  # Add CSV string to list for this page

                tables_by_page[page_number+1] = csv_list

        return tables_by_page

    def fillExcelAndSave(self, template_path, vendorInformation,vendor_name):
        tempPath = f"/app/VendorsInvoicePdfToExcel/{vendor_name}"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".xlsx"
        # tempPath = f"/Users/administrator/PycharmProjects/PslHelper/{vendor_name}"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".xlsx"
        shutil.copy(template_path, tempPath)
        workbook = openpyxl.load_workbook(tempPath)
        sheet = workbook.active

        # vendor_info
        sheet["B2"] = vendorInformation["vendor_info"]["vendor_name"]
        sheet["B3"] = vendorInformation["vendor_info"]["vendor_address"]
        sheet["B4"] = vendorInformation["vendor_info"]["vendor_mob"]
        sheet["B5"] = vendorInformation["vendor_info"]["vendor_gst"]
        sheet["B6"] = vendorInformation["vendor_info"]["vendor_email"]
        sheet["B7"] = vendorInformation["invoice_info"]["invoice_number"]
        sheet["B8"] = vendorInformation["invoice_info"]["invoice_date"]

        #our Info
        sheet["K2"] = vendorInformation["receiver_info"]["receiver_name"]
        sheet["K3"] = vendorInformation["receiver_info"]["receiver_address"]
        sheet["K4"] = vendorInformation["receiver_info"]["receiver_gst"]
        sheet["K5"] = vendorInformation["receiver_billing_info"]["place_of_supply"]
        sheet["K6"] = vendorInformation["receiver_billing_info"]["billto_name"]
        sheet["K7"] = vendorInformation["receiver_billing_info"]["billto_address"]
        sheet["K8"] = vendorInformation["receiver_billing_info"]["billto_gst"]

        startIndexOfProduct = 15
        for aProductInfo in vendorInformation["items_info"]:
            sheet["A"+str(startIndexOfProduct)] = aProductInfo["index"]
            sheet["B"+str(startIndexOfProduct)] = aProductInfo["vendor_code"]
            sheet["C"+str(startIndexOfProduct)] = aProductInfo["po_no"]
            sheet["D"+str(startIndexOfProduct)] = aProductInfo["or_po_no"]
            sheet["E"+str(startIndexOfProduct)] = aProductInfo['debit_note_no']
            sheet["F"+str(startIndexOfProduct)] = aProductInfo["HSN/SAC"]
            sheet["G"+str(startIndexOfProduct)] = aProductInfo["Qty"]
            sheet["H"+str(startIndexOfProduct)] = aProductInfo["mrp"]
            sheet["I"+str(startIndexOfProduct)] = aProductInfo["Rate"]

            if aProductInfo["gst_type"].strip().__contains__("CGST"):
                sheet["J" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
                sheet["K" + str(startIndexOfProduct)] =  aProductInfo["tax_applied"]
            if aProductInfo["gst_type"].strip().__contains__("SGST"):
                sheet["L" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
                sheet["M" + str(startIndexOfProduct)] = aProductInfo["tax_applied"]
            if aProductInfo["gst_type"].strip() == "IGST":
                sheet["N" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
                sheet["O" + str(startIndexOfProduct)] = aProductInfo["tax_applied"]
            sheet["P"+str(startIndexOfProduct)] = aProductInfo["po_cost"]
            startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Total"
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["G" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_pcs']
        cell = sheet["G" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["I" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_b4_tax']
        cell = sheet["I" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["P" + str(startIndexOfProduct)] = float(vendorInformation['items_total_info']['total_amount_after_tax'].replace('Rs.', '').replace(',', '').strip())
        cell = sheet["P" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["K" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["CGST"] == 0 else vendorInformation["total_tax"]["CGST"]
        cell = sheet["K" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["M" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["SGST"] == 0 else vendorInformation["total_tax"]["SGST"]
        cell = sheet["M" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["O" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["IGST"] == 0 else vendorInformation["total_tax"]["IGST"]
        cell = sheet["O" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)

        startIndexOfProduct += 1
        startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Total Amount "
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_b4_tax']
        startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Tax Amount"
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_tax']
        startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Amount after tax"
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_amount_after_tax']
        startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Amount In Words"
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['amount_charged_in_words']
        startIndexOfProduct += 1

        sheet["A" + str(startIndexOfProduct)] = "Tax Amount In Words"
        cell = sheet["A" + str(startIndexOfProduct)]
        cell.font = Font(bold=True)
        sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['tax_amount_in_words']
        startIndexOfProduct += 1

        workbook.save(tempPath)
        return tempPath

    def processPdf(self, pdfPath, vendor):
            tables_data = self.extract_tables_from_pdf(pdfPath)
            text_data =  self.extractTextFromPdf(pdfPath)
            tables_data_from_tabula = self.extract_tables_from_pdf_using_tabula(pdfPath)
            if len(text_data) == 0:
                raise HTTPException(status_code=400,detail="Input pdf might be an image, cannot parse it.")

            implementation_factor =  ImplementationFactory()
            implementation = implementation_factor.getImplementation(vendor, tables_data, text_data, tables_data_from_tabula)
            vendor_info = implementation.getVendorInfo()
            invoice_info = implementation.getInvoiceInfo()
            receiver_info = implementation.getReceiverInfo()
            receiver_billing_info = implementation.getBillingInfo()
            items_info, total_tax = implementation.getItemInfo()
            vendor_bank_info = implementation.getVendorBankInfo()
            items_total_info = implementation.getItemTotalInfo()

            extractedInformation = {
               "vendor_info" : vendor_info,
               "invoice_info" : invoice_info,
               "receiver_info" : receiver_info,
               "receiver_billing_info" : receiver_billing_info,
               "items_info" : items_info,
               "vendor_bank_info" : vendor_bank_info,
               "items_total_info" : items_total_info,
               "total_tax": total_tax
            }
            return extractedInformation