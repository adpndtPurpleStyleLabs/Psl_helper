# import pdfplumber
# import openpyxl
# import shutil
# from openpyxl.styles import Font
# import os
# import tempfile
#
# def extractTextFromPdf(file_path):
#     page_text_dict = {}
#     with pdfplumber.open(file_path) as pdf:
#         for page_num, page in enumerate(pdf.pages, start=1):
#             page_text = page.extract_text()
#             if page_text:
#                 page_text_dict[page_num] = page_text
#
#     return page_text_dict
#
# def extract_tables_from_pdf(pdf_path):
#     tables_data = {}
#
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_number in range(len(pdf.pages)):
#             page = pdf.pages[page_number]
#             table = page.extract_table()
#             if table:
#                 cleaned_table = [[cell for cell in row if cell is not None] for row in table]
#                 tables_data[page_number + 1] = cleaned_table
#
#     return tables_data
#
# def fillExcelAndSave(template_path, vendorInformation):
#     tempPath = "/Users/administrator/PycharmProjects/PslHelper/zz.xlsx"
#     shutil.copy(template_path, tempPath)
#     workbook = openpyxl.load_workbook(tempPath)
#     sheet = workbook.active
#
#     # vendor_info
#     sheet["B2"] = vendorInformation["vendor_info"]["vendor_name"]
#     sheet["B3"] = vendorInformation["vendor_info"]["vendor_address"]
#     sheet["B4"] = vendorInformation["vendor_info"]["vendor_mob"]
#     sheet["B5"] = vendorInformation["vendor_info"]["vendor_gst"]
#     sheet["B6"] = vendorInformation["vendor_info"]["vendor_email"]
#     sheet["B7"] = vendorInformation["invoice_info"]["invoice_number"]
#     sheet["B8"] = vendorInformation["invoice_info"]["invoice_date"]
#
#     #our Info
#     sheet["K2"] = vendorInformation["receiver_info"]["receiver_name"]
#     sheet["K3"] = vendorInformation["receiver_info"]["receiver_address"]
#     sheet["K4"] = vendorInformation["receiver_info"]["receiver_gst"]
#     sheet["K5"] = vendorInformation["receiver_billing_info"]["place_of_supply"]
#     sheet["K6"] = vendorInformation["receiver_billing_info"]["billto_address"]
#     sheet["K7"] = vendorInformation["receiver_billing_info"]["billto_gst"]
#     sheet["K8"] = vendorInformation["receiver_billing_info"]["billto_name"]
#
#     startIndexOfProduct = 15
#     for aProductInfo in vendorInformation["items_info"]:
#         sheet["A"+str(startIndexOfProduct)] = aProductInfo["index"]
#         sheet["B"+str(startIndexOfProduct)] = aProductInfo["vendor_code"]
#         sheet["C"+str(startIndexOfProduct)] = aProductInfo["po_no"]
#         sheet["D"+str(startIndexOfProduct)] = aProductInfo["or_po_no"]
#         sheet["E"+str(startIndexOfProduct)] = aProductInfo['debit_note_no']
#         sheet["F"+str(startIndexOfProduct)] = aProductInfo["HSN/SAC"]
#         sheet["G"+str(startIndexOfProduct)] = aProductInfo["Qty"]
#         sheet["H"+str(startIndexOfProduct)] = aProductInfo["mrp"]
#         sheet["I"+str(startIndexOfProduct)] = aProductInfo["Rate"]
#         if aProductInfo["gst_type"] == "CGST":
#             sheet["J" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
#             sheet["K" + str(startIndexOfProduct)] =  aProductInfo["tax_applied"]
#
#         elif aProductInfo["gst_type"] == "SGST":
#             sheet["L" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
#             sheet["M" + str(startIndexOfProduct)] = aProductInfo["tax_applied"]
#         elif aProductInfo["gst_type"] == "IGST":
#             sheet["N" + str(startIndexOfProduct)] =  aProductInfo["gst_rate"]
#             sheet["O" + str(startIndexOfProduct)] = aProductInfo["tax_applied"]
#         sheet["P"+str(startIndexOfProduct)] = aProductInfo["po_cost"]
#         startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Total"
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["G" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_pcs']
#     cell = sheet["G" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["I" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_b4_tax']
#     cell = sheet["I" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["P" + str(startIndexOfProduct)] = float(vendorInformation['items_total_info']['total_amount_after_tax'].replace('Rs.', '').replace(',', '').strip())
#     cell = sheet["P" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["K" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["CGST"] == 0 else vendorInformation["total_tax"]["CGST"]
#     cell = sheet["K" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["M" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["SGST"] == 0 else vendorInformation["total_tax"]["SGST"]
#     cell = sheet["M" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["O" + str(startIndexOfProduct)] = "" if vendorInformation["total_tax"]["IGST"] == 0 else vendorInformation["total_tax"]["IGST"]
#     cell = sheet["O" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#
#     startIndexOfProduct += 1
#     startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Total Amount "
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_b4_tax']
#     startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Tax Amount"
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_tax']
#     startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Amount after tax"
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['total_amount_after_tax']
#     startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Amount In Words"
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['amount_charged_in_words']
#     startIndexOfProduct += 1
#
#     sheet["A" + str(startIndexOfProduct)] = "Tax Amount In Words"
#     cell = sheet["A" + str(startIndexOfProduct)]
#     cell.font = Font(bold=True)
#     sheet["B" + str(startIndexOfProduct)] = vendorInformation['items_total_info']['tax_amount_in_words']
#     startIndexOfProduct += 1
#
#     workbook.save(tempPath)
#
# # if __name__ == '__main__':
# #     templatePath = "/Users/administrator/PycharmProjects/PslHelper/TemplateVendorInvoices.xlsx"
# #     pdfPath = "../Sales_1805_24-25.pdf"
# #     tables_data = extract_tables_from_pdf(pdfPath)
# #     text_data = extractTextFromPdf(pdfPath)
# #     implementation_factor = ImplementationFactory()
# #     # implementation = implementation_factor.getImplementation("amitagarwal", tables_data, text_data)
# #     implementation = implementation_factor.getImplementation("seemagujral", tables_data, text_data)
# #     vendor_info = implementation.getVendorInfo()
# #     invoice_info = implementation.getInvoiceInfo()
# #     receiver_info = implementation.getReceiverInfo()
# #     receiver_billing_info = implementation.getBillingInfo()
# #     items_info, total_tax = implementation.getItemInfo()
# #     vendor_bank_info = implementation.getVendorBankInfo()
# #     items_total_info = implementation.getItemTotalInfo()
# #
# #     finalInfo ={
# #        "vendor_info" : vendor_info,
# #        "invoice_info" : invoice_info,
# #        "receiver_info" : receiver_info,
# #        "receiver_billing_info" : receiver_billing_info,
# #        "items_info" : items_info,
# #        "vendor_bank_info" : vendor_bank_info,
# #        "items_total_info" : items_total_info,
# #        "total_tax": total_tax
# #     }
# #
# #     fillExcelAndSave(templatePath, finalInfo)
#
#