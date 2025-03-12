import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_amount_to_words, find_nth_occurrence_of, get_list_containing
from fastapi import HTTPException

class ReneeLabel:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.gstPercentage = ""
        self.totalGst = 0

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = get_list_containing(firstPageText, "Renee").split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address":", ".join(vendorInfo[:4]),
            "vendor_mob": vendorInfo[indexOfContainsInList(vendorInfo, "GST")+1],
            "vendor_gst": get_list_containing(vendorInfo, "GST").split(" ")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "GST")+2].split(" ")[0]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number":get_list_containing(get_list_containing(firstPageText, "Invoice No").split("\n"), "invoice n").split(" ")[-1],
            "invoice_date":
                get_list_containing(get_list_containing(firstPageText, "Invoice Date").split("\n"), "date").split(":")[
                    -1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "bill to") + 1:][0][0]
        receiverInfo = receiverInfo.split("\n")
        return {
            "receiver_name": receiverInfo[0],
            "receiver_address": ", ".join(receiverInfo[1:3]),
            "receiver_gst": get_list_containing(receiverInfo, "GST").split(" ")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "bill to") + 1:][0][1]
        billToInfo = billToInfo.split("\n")
        return {
            "billto_name": billToInfo[0],
            "billto_address": ", ".join(billToInfo[2:3]),
            "place_of_supply": get_list_containing(firstPageText, "Place Of Supply").split("\n")[0].split(":")[-1],
            "billto_gst": get_list_containing(billToInfo, "GST").split(" ")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPageText = self.tables[1]
        lastPage = pages[len(pages)]

        gstHeader = get_list_containing(firstPageText, "total taxable amount").split("\n")
        gstType = ""
        if indexOfContainsInList(gstHeader, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(gstHeader, "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(gstHeader, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        total_tax = {
            "IGST": float(get_list_containing(gstHeader, "%").split(" ")[-1].replace(",","")),
            "SGST": 0,
            "CGST": 0, }
        self.gstPercentage = float(get_list_containing(gstHeader, "%").split(" ")[0].replace("IGST", "").strip())
        self.totalGst = total_tax["IGST"] +total_tax["SGST"] +total_tax["CGST"]
        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "description")
        indexOfSr = indexOfContainsInList(firstPageText[indexOfHeader], "Sr")
        indexOfHsn = indexOfContainsInList(firstPageText[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPageText[indexOfHeader], "Qty")
        indexOfRate = indexOfContainsInList(firstPageText[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPageText[indexOfHeader], "Amount")+1
        indexOfPer = indexOfContainsInList(firstPageText[indexOfHeader], "per")
        indexOfIgstRate = indexOfContainsInList(firstPageText[indexOfHeader], "IGST")
        indexOfIgstAmount = indexOfContainsInList(firstPageText[indexOfHeader], "IGST")+1

        for itemIndex, item in enumerate(firstPageText[indexOfHeader+2:]):
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
            aProductResult["HSN/SAC"] = item[indexOfHsn].split("\n")[0]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = item[indexOfPer]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt].split("\n")[0]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = item[indexOfIgstRate]
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = item[indexOfIgstAmount]
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankInfo = get_list_containing(lastPage, "bank ").split("\n")
        return {
            "bank_name": get_list_containing(bankInfo, "Bank Name").split(":")[-1].strip(),
            "account_number": get_list_containing(bankInfo, "A/c").split(":")[-1].strip(),
            "ifs_code": get_list_containing(bankInfo, "IFSC").split(":")[-1].strip()
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        totalsInfo = get_list_containing(lastPage, "Invoice Amount ").split("\n")
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words( self.totalGst)
        returnData["amount_charged_in_words"] = get_list_containing(lastPage,"Total In Words").split("\n")[indexOfContainsInList(get_list_containing(lastPage,"Total In Words").split("\n"), "In Words")+1]
        returnData["total_pcs"] =  get_list_containing(lastPage, "Items in Total ").split("\n")[0]
        returnData["total_amount_after_tax"] = get_list_containing(totalsInfo, "invoice amount").split(" ")[-1]
        returnData["total_b4_tax"] = get_list_containing(totalsInfo, "total").split(" ")[-1]
        returnData["total_tax"] =self.totalGst
        returnData["tax_rate"] = self.gstPercentage
        returnData["total_tax_percentage"] = self.gstPercentage
        return returnData
