from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing
from fastapi import HTTPException

class Espana:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.gstPercentage = ""
        self.totalb4tax = ""
        self.totalaftertax = ""
        self.taxApplied = ""

        if self.text_data[len(self.tables)].find("e-Way") is not -1:
            self.text_data.pop(len(self.tables))
            self.tables.pop(len(self.tables))

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "ESPANA")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:4]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice No")]
        return {
            "invoice_number":invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split("\n")[-1],
            "invoice_date": self.text_data[1][self.text_data[1].find("Dated"):].split("\n")[7].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship") : indexOfContainsInList(receiverInfo, "Bill")]
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ", ".join(receiverInfo[2:4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill") :]
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:4]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }


    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        total_tax = { "IGST": lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)") -1][-1].split("\n")[-1].replace(",",""),  "SGST": 0, "CGST": 0,}

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "HSN/")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
        indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

        listOfTotalTaxs =lastPage[indexOfContainsInList(lastPage, "Amount Chargeable (") : indexOfContainsInList(lastPage, "Tax Amount (in words)")]

        for itemIndex, item in enumerate(firstPage[indexOfHeader+1:]):

            if indexOfContainsInList(item,"Total") is not -1:
                break
            if item[0].strip() == "" or item.__len__() <4:
                continue

            aProductResult= {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Order No")+1].split(" ")[0]
            if orPoInfo.find("Consignee") is not -1:
                orPoInfo = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Reference No")+2].split(" ")[0]
            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            gstPercentage =  get_list_containing(listOfTotalTaxs, "%").split("\n")[-1].strip().replace("%","")
            self.gstPercentage = gstPercentage
            aProductResult["debit_note_no"] = ""
            aProductResult["index"] =  item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = float(item[indexOfRate].strip().replace(",",""))
            aProductResult["Per"] = item[indexOfPer]
            aProductResult["mrp"] = float(item[indexOfRate].strip().replace(",",""))
            aProductResult["Amount"] = float(item[indexOfAmt].split("\n")[0].strip().replace(",",""))
            self.totalb4tax =  aProductResult["Amount"]
            aProductResult["po_cost"] = ""
            aProductResult["tax_applied"] = float(item[indexOfAmt].split("\n")[0].replace(",","")) * (float(gstPercentage)/100)
            self.taxApplied = aProductResult["tax_applied"]
            aProductResult["gst_rate"] = float(gstPercentage)
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
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[
            -1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = float(lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1].strip().replace(",",""))
        returnData["total_b4_tax"] = self.totalb4tax
        returnData["total_tax"] = self.taxApplied
        returnData["tax_rate"] = float(self.gstPercentage)
        returnData["total_tax_percentage"] =float(returnData["tax_rate"])
        return returnData