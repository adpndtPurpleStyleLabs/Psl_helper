from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing

import re
from fastapi import HTTPException

class MrunaliniRao:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Mrun")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:5]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Dated")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(" ")[-1].split("\n")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ",".join(receiverInfo[2:6]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:6]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]
        lastPageAsText = self.text_data[len(self.text_data)].split("\n")

        total_tax = { "IGST": float(self.text_data[len(pages)].split("\n")[indexOfContainsInList(self.text_data[len(pages)].split("\n"), "Tax Amount (in")-1].split(" ")[-1].replace(",","")),  "SGST": 0, "CGST": 0,}

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")


        products = []

        for index in range(1, len(pages) + 1):
            page = pages[index]

            indexOfHeader = indexOfContainsInList(self.tables[1], "description")
            indexOfSr = indexOfContainsInList(page[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(page[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(page[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(page[indexOfHeader], "Quantity")
            indexOfRate = indexOfContainsInList(page[indexOfHeader], "Rate")
            indexOfUnit = indexOfContainsInList(page[indexOfHeader], "per")
            indexOfAmt = indexOfContainsInList(page[indexOfHeader], "Amount")

            for itemIndex, item in enumerate(page[indexOfHeader+1:]):
                if indexOfContainsInList(item, "continue") is not -1:
                    break
                if item[0].strip() == "" or len(item) < len(page[indexOfHeader]) :
                    continue

                aProductResult= {}

                poNoInfoLine =  get_list_containing(self.tables[1], "Reference No").split("\n")
                poNoInfoLine = re.sub(r'[^a-zA-Z0-9]', '', poNoInfoLine[-1]).lower()

                poNoInfo = poNoInfoLine[ poNoInfoLine.find("no")+2: poNoInfoLine.find("dt")].strip()

                gstRate = float(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)") - 2].split(" ")[indexOfContainsInList(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)") - 2].split(" "), "%")].replace("%", "").strip())

                amount = float(item[indexOfAmt].split("\n")[0].replace(",",""))

                aProductResult["debit_note_no"] = ""
                aProductResult["index"] = item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = float(item[indexOfRate].replace(",","").strip())
                aProductResult["Per"] = item[indexOfUnit]
                aProductResult["mrp"] = float(item[indexOfRate].replace(",","").strip())
                aProductResult["Amount"] = amount
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] = gstRate
                aProductResult["gst_type"] = gstType
                aProductResult["tax_applied"] = (amount * gstRate)/100
                aProductResult["po_no"] = poNoInfo
                products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]
        bankInfo = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
        return {
            "bank_name": bankInfo[indexOfContainsInList(bankInfo, "Bank Name")].split(":")[-1],
            "account_number": bankInfo[indexOfContainsInList(bankInfo, "A/c No")].split(":")[-1],
            "ifs_code": bankInfo[indexOfContainsInList(bankInfo, "IFS")].split(":")[-1],
        }

    def getItemTotalInfo(self):
        lastPage  =self.tables[len(self.tables)]
        lastPageAsText = self.text_data[len(self.text_data)].split("\n")
        returnData = {}
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[-1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = float(lastPageAsText[indexOfContainsInList(lastPageAsText, "Amount Chargeable (in words)")-1].split(" ")[-1].replace(",", ""))
        returnData["total_b4_tax"] =float(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)")-1].split(" ")[1].replace(",",""))
        returnData["total_tax"] = float(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)")-1].split(" ")[-1].replace(",",""))
        returnData["tax_rate"] = float(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)") - 2].split(" ")[indexOfContainsInList(lastPageAsText[indexOfContainsInList(lastPageAsText, "Tax Amount (in words)") - 2].split(" "), "%")].replace("%", "").strip())
        returnData["total_tax_percentage"] =  returnData["tax_rate"]
        return returnData