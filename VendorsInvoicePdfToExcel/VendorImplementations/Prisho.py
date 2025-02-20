import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_amount_to_words, find_nth_occurrence_of, get_list_containing
from fastapi import HTTPException

class Prisho:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.gstPercentage = ""


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Anjuna")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:5]),
            "vendor_mob": "N/A",
            "vendor_gst": get_list_containing(vendorInfo, "GST").split(":")[-1].strip(),
            "vendor_email": get_list_containing(vendorInfo, "mail").split(":")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice No")]
        return {
            "invoice_number":invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(" ")[-1].split("\n")[-1],
            "invoice_date":self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "dated")+1].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "ship to")][0]
        receiverInfo = receiverInfo.split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ", ".join(receiverInfo[2:4]),
            "receiver_gst": get_list_containing(receiverInfo, "GST").split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "bill to")][0]
        billToInfo = billToInfo.split("\n")

        return {
            "billto_name":billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:4]),
            "place_of_supply":get_list_containing(billToInfo, "State"),
            "billto_gst":get_list_containing(billToInfo, "GST").split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPageText = self.tables[1]
        lastPage = pages[len(pages)]

        gstHeader = pages[1][indexOfContainsInList(pages[1], "Amount Charg")+1]
        gstType = ""
        if indexOfContainsInList(gstHeader, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(gstHeader, "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(gstHeader, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        total_tax = {
            "IGST": float(pages[1][indexOfContainsInList(pages[1], "ax Amount (in wo")-1][-2].replace(",", "")),
            "SGST": 0,
            "CGST": 0, }
        self.gstPercentage = float(pages[1][indexOfContainsInList(pages[1], "ax Amount (in wo")-2][indexOfContainsInList(gstHeader, "IGST")].replace("%", ""))

        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "description")
        indexOfSr = indexOfContainsInList(firstPageText[indexOfHeader], "Sl")
        indexOfHsn = indexOfContainsInList(firstPageText[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPageText[indexOfHeader], "Quantity")
        indexOfRate = indexOfContainsInList(firstPageText[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPageText[indexOfHeader], "Amount")
        indexOfPer = indexOfContainsInList(firstPageText[indexOfHeader], "per")

        for itemIndex, item in enumerate(firstPageText[indexOfHeader+1:]):
            if indexOfContainsInList(item, "Total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult= {}

            poNoInfo = get_list_containing(item[1].split("\n"), "PO").split(" ")[-1]
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            if poNoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = poNoInfo
            else:
                aProductResult["po_no"] = poNoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = item[indexOfPer]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt].split("\n")[0]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = self.gstPercentage
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankInfo = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
        return {
            "bank_name": get_list_containing(bankInfo, "Bank Name").split(":")[-1].strip(),
            "account_number": bankInfo[find_nth_occurrence_of(bankInfo, "A/c No",2)],
            "ifs_code": get_list_containing(bankInfo, "IFS Cod").split(":")[-1].strip()
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = get_list_containing(lastPage, "Tax Amount (in word").split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = get_list_containing(lastPage, "Amount Chargeable (in wor").split("\n")[-1]
        returnData["total_pcs"] =  lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in ")-1][1]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in ")-1][-1]
        returnData["tax_rate"] = self.gstPercentage
        returnData["total_tax_percentage"] = self.gstPercentage
        return returnData
