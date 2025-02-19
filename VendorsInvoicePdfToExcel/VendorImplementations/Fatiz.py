import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from fastapi import HTTPException
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class Fatiz:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Fatiz")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Fatiz")], "Fatiz")]
        return {
            "vendor_name": vendorInfo.split("\n")[0],
            "vendor_address": ", ".join(vendorInfo.split("\n")[0:3]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo.split("\n")[indexOfContainsInList(vendorInfo.split("\n"), "GST")].split(" ")[-1],
            "vendor_email": vendorInfo.split("\n")[-2]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice Number")][0].split("\n")
        return {
            "invoice_number": invoiceInfo[0].split(":")[-1],
            "invoice_date": invoiceInfo[2].split(":")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship")+1][0].split("\n")

        return {
            "receiver_name": receiverInfo[0],
            "receiver_address": receiverInfo[1],
            "receiver_gst":receiverInfo[indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Ship")+1][0].split("\n"), "GST")].split(" ")[-1]
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =  firstPageText[indexOfContainsInList(firstPageText, "Ship")+1][0].split("\n")
        return {
            "billto_name": billToInfo[0],
            "billto_address": billToInfo[1],
            "place_of_supply": billToInfo[3],
            "billto_gst": billToInfo[indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Ship")+1][0].split("\n"), "GST")].split(" ")[-1]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        indexOfHeader = indexOfContainsInList(self.tables[1], "#")

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "#")], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "#")], "IGST")  != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "#")], "SGST")  != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        total_tax = {"IGST":
                         lastPage[indexOfContainsInList(lastPage, "Sub Total")][-1].split("\n")[indexOfContainsInList(
                             lastPage[indexOfContainsInList(lastPage, "Sub Total")][-1].split("\n"), "GST")].split(" ")[
                             -1]
            , "SGST": 0,
                     "CGST": 0, }

        products = []
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "#")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
        indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

        for itemIndex, item in enumerate(firstPage[indexOfHeader + 2:]):
            if indexOfContainsInList(item, "Total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult = {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = item[indexOfItemname].split("\n")[-1].replace("PO", "")
            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = item[indexOfQty]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt+1]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = item[indexOfContainsInList(item, "%")].replace("%", "")
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        return {
            "bank_name": "",
            "account_number": "",
            "ifs_code": "",
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        totalTax = re.sub(r'[^a-zA-Z0-9.]+', '',
                          lastPage[indexOfContainsInList(lastPage, "Sub Total")][-1].split("\n")[indexOfContainsInList(
                              lastPage[indexOfContainsInList(lastPage, "Sub Total")][-1].split("\n"), "GST")].split(
                              " ")[
                              -1])
        totalAmount = re.sub(r'[^a-zA-Z0-9.]+', '', lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n")[
            indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n"), "GST") + 1].split(
            " ")[-1])
        returnData["tax_amount_in_words"] = convert_amount_to_words(
            lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n")[
                indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n"), "GST")].split(
                " ")[-1].replace(",", ""))
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n")[2]
        returnData["total_pcs"] = ""
        returnData["total_amount_after_tax"] = totalAmount
        returnData["total_b4_tax"] = float(totalAmount) - float(totalTax)
        returnData["total_tax"] = totalTax
        returnData["tax_rate"] = re.sub(r'[^a-zA-Z0-9.]+', "",
                                        lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n")[
                                            indexOfContainsInList(
                                                lastPage[indexOfContainsInList(lastPage, "In Wo")][0].split("\n"),
                                                "GST")].split(" ")[1])
        returnData["total_tax_percentage"] = returnData["tax_rate"]
        return returnData