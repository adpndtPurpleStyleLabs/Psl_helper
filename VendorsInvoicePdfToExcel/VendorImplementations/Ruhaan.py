import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from fastapi import HTTPException

class Ruhaan:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        if self.text_data[len(self.tables)].find("e-Way") is not -1:
            self.text_data.pop(len(self.tables))
            self.tables.pop(len(self.tables))

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Ruha")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:4]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "Email")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Dated")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(" ")[-2].split("\n")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship") : indexOfContainsInList(receiverInfo, "Bill")]
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": receiverInfo[2],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill") :]
        return {
            "billto_name": billToInfo[1],
            "billto_address": billToInfo[2],
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "Place")].split(":")[-1].strip(),
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        total_tax = { "IGST": lastPage[indexOfContainsInList(lastPage, "Taxable")+1][1].split("\n")[-1],  "SGST": 0, "CGST": 0,}

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")


        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(self.tables[1], "Sl")
            indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
            indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
            indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
            indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

            for itemIndex, item in enumerate(aPage[indexOfHeader+1:]):
                if indexOfContainsInList(item, "Output") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                aProductResult= {}
                aProductResult["po_no"] = ""
                orPoInfo = aPage[indexOfHeader+itemIndex+2][1]
                if indexOfContainsInList(aPage[indexOfHeader+itemIndex+2], "OR") is not -1:
                    aProductResult["po_no"] = orPoInfo[orPoInfo.find("OR"):].replace(")", "").strip()

                aProductResult["index"] =  item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = item[indexOfRate]
                aProductResult["Per"] = item[indexOfPer]
                aProductResult["mrp"] = item[indexOfRate]
                aProductResult["Amount"] = item[indexOfAmt]
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] =lastPage[indexOfContainsInList(lastPage, "Taxable")+1][0].split("\n")[-1].replace("%", "").strip()
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
        lastPage  =self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[-1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = re.sub(r'[^a-zA-Z0-9.]+', '',lastPage[indexOfContainsInList(lastPage, "Total")][-1])
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Taxable")], "Taxable")].split("\n")[-1]
        returnData["total_tax"] =lastPage[indexOfContainsInList(lastPage, "Taxable")][-1].split("\n")[-1]
        returnData["tax_rate"] = lastPage[indexOfContainsInList(lastPage, "Taxable")+1][0].split("\n")[-1].replace("%", "").strip()
        returnData["total_tax_percentage"] =lastPage[indexOfContainsInList(lastPage, "Taxable")+1][0].split("\n")[-1].replace("%", "").strip()
        return returnData