from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of, get_list_containing, \
    convert_amount_to_words
from fastapi import HTTPException

class KkarmaAccessories:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalPercentage = 0
        self.totalGstAmount = 0
        self.count =0

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "kkarma")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[1:5]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(" ")[-1].strip(),
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "invoice no").split("\n")[-1],
            "invoice_date": get_list_containing(firstPageText, "DATE").split("\n")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[find_nth_occurrence_of(firstPageText, "BUYER",2)][0].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ",".join(receiverInfo[2:4]),
            "receiver_gst":receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(" ")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[find_nth_occurrence_of(firstPageText, "BUYER",2)][0].split("\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:4]),
            "place_of_supply": "N/A",
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(" ")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]

        listOfTaxHeader = lastPage[indexOfContainsInList(lastPage, "TAXABLE")]

        gstType = []
        if indexOfContainsInList(listOfTaxHeader, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For KkarmaAccessories CGST is not implemented")

        if indexOfContainsInList(listOfTaxHeader, "Integrated") != -1:
            gstType.append("IGST")

        if indexOfContainsInList(listOfTaxHeader, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For KkarmaAccessories SGST is not implemented")

        gstType = "_".join(gstType)
        total_tax = {"IGST": 0,
                     "SGST": 0,
                     "CGST": 0, }

        total_tax_percentage = {"IGST": 0,
                     "SGST": 0,
                     "CGST": 0, }

        indexOfIgst = indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "TAXABLE")], "Integrated")
        total_tax_percentage["IGST"] =float(lastPage[indexOfContainsInList(lastPage, "TAXABLE")+2][indexOfIgst].replace("%", ""))
        total_tax["IGST"] = float(lastPage[indexOfContainsInList(lastPage, "DECLARATION")-1][indexOfIgst+1])
        self.totalPercentage = total_tax_percentage["SGST"] + total_tax_percentage["CGST"] + total_tax_percentage["IGST"]
        self.totalGstAmount = total_tax["SGST"] + total_tax["CGST"] + total_tax["IGST"]
        products = []

        for index in range(1, len(pages) + 1):
            page = pages[index]
            indexOfHeader = indexOfContainsInList(self.tables[1], "description")
            indexOfSr = indexOfContainsInList(page[indexOfHeader], "no")
            indexOfQty = indexOfContainsInList(page[indexOfHeader], "QTY")
            indexOfRate = indexOfContainsInList(page[indexOfHeader], "Rate")
            indexOfHSN = indexOfContainsInList(page[indexOfHeader], "HSN")
            indexOfAmt = indexOfContainsInList(page[indexOfHeader], "Amount")

            poNoInfo = get_list_containing(page,"SUPPLIER'S REF.").split("\n")[-1].split(":")[-1]
            for itemIndex, item in enumerate(page[indexOfHeader + 1:]):
                if indexOfContainsInList(item, "TAXABLE") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                aProductResult = {}
                aProductResult["po_no"] = ""

                aProductResult["or_po_no"] = ""
                if poNoInfo.find("OR") is not -1:
                    aProductResult["or_po_no"] = poNoInfo
                else:
                    aProductResult["po_no"] = poNoInfo

                aProductResult["debit_note_no"] = ""
                aProductResult["index"] = item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHSN]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] =item[indexOfRate].split("\n")[0]
                aProductResult["Per"] = "N/A"
                aProductResult["mrp"] = item[indexOfRate].split("\n")[0]
                aProductResult["Amount"] = item[indexOfAmt].split("\n")[0]
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] = self.totalPercentage
                aProductResult["gst_type"] = gstType
                aProductResult["tax_applied"] = (float(item[indexOfAmt].split("\n")[0]) *  self.totalPercentage) /100
                products.append(aProductResult)
                self.count+=1

        return products, total_tax

    def getVendorBankInfo(self):
        return {
            "bank_name": "N/A",
            "account_number": "N/A",
            "ifs_code": "N/A",
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(self.totalGstAmount)
        returnData["amount_charged_in_words"] = convert_amount_to_words(
            float(lastPage[indexOfContainsInList(lastPage, "DECLARATION") - 1][1]) + self.totalGstAmount)
        returnData["total_pcs"] = self.count
        returnData["total_amount_after_tax"] = float(
            lastPage[indexOfContainsInList(lastPage, "DECLARATION") - 1][1]) + self.totalGstAmount
        returnData["total_b4_tax"] = float(lastPage[indexOfContainsInList(lastPage, "DECLARATION") - 1][1])
        returnData["total_tax"] = self.totalGstAmount
        returnData["tax_rate"] = self.totalPercentage
        returnData["total_tax_percentage"] = self.totalPercentage
        return returnData
