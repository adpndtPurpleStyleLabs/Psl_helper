from fastapi import HTTPException
from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing, find_nth_occurrence_of
import re

class LinenBloomMen:
    def __init__(self, tables, text):
        self.tables = tables
        self.text = text
        self.gstRate = ""

    def getVendorInfo(self):
        firstPage = self.tables[1]
        return {
            "vendor_name": firstPage[0][0].split("\n")[0],
            "vendor_address": firstPage[0][0].split("\n")[1] + " " + firstPage[0][0].split("\n")[2] + " " +
                              firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "State")],
            "vendor_mob": "",
            "vendor_gst": firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "GST")].split(":")[-1].strip(),
            "vendor_email": firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "Mail")].split(":")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPage = self.tables[1]
        return {
            "invoice_number": firstPage[0][indexOfContainsInList(firstPage[0], "Invoice")].split("\n")[-1],
            "invoice_date":
                self.text[1].split("\n")[indexOfContainsInList(self.text[1].split("\n"), "Dated") + 1].split(" ")[
                    -1].strip()
        }

    def getReceiverInfo(self):
        firstPage = self.tables[1]
        receiverInfo = get_list_containing(firstPage, "ship").split("\n")
        receiverInfo = receiverInfo[
                       indexOfContainsInList(receiverInfo, "Ship ") + 1: indexOfContainsInList(receiverInfo, "Bill ")]
        return {
            "receiver_name": receiverInfo[0],
            "receiver_address": ", ".join(receiverInfo[1:2]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GSTIN")].split(":")[-1],
        }

    def getBillingInfo(self):
        firstPage = self.tables[1]
        billInfo = get_list_containing(firstPage, "bill to").split("\n")
        billInfo = billInfo[
                   indexOfContainsInList(billInfo, "Bill ") + 1:]

        return {
            "billto_name": billInfo[0],
            "billto_address": ", ".join(billInfo[1:2]),
            "billto_gst": billInfo[indexOfContainsInList(billInfo, "GSTIN")].split(":")[-1],
            "place_of_supply": billInfo[indexOfContainsInList(billInfo, "State")].split(",")[0].split(":")[-1]
        }

    def getItemInfo(self):
        allPages = self.tables
        lenOfPages = len(allPages)
        firstPage = self.tables[1]
        products = []
        lastPage = allPages[lenOfPages]

        total_tax = {
            "IGST": 0,
            "SGST": 0,
            "CGST": 0,
        }

        total_tax = {"IGST": float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in")-1][-1].replace(",","")), "SGST": 0,
                     "CGST": 0, }

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")


        indexOfHeader = indexOfContainsInList(firstPage, "HSN/")
        indexOfSrNo = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
        indexOfDescription = indexOfContainsInList(firstPage[indexOfHeader], "Descrip")
        indexOfHsnCode = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOFQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
        indexRateWithTax = indexOfContainsInList(firstPage[indexOfHeader], "Incl. of")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate") + 1
        indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
        indexOfAmount = indexOfContainsInList(firstPage[indexOfHeader], "Amount")



        listOfInfo = firstPage[indexOfHeader+1]
        listOfIndex =listOfInfo[indexOfSrNo].split("\n")
        listOfHsn = listOfInfo[indexOfHsnCode].split("\n")
        listOfQty = listOfInfo[indexOFQty].split("\n")
        listOfAmt = listOfInfo[indexRateWithTax].split("\n")
        listOfRate = listOfInfo[indexOfRate].split("\n")
        listOfPer = listOfInfo[indexOfPer].split("\n")

        listOfPoNos = []
        for index,aPage in enumerate(self.tables.values()):
            indexOfHederInDynamicPage =indexOfContainsInList(aPage, "HSN/")
            indexOfDescriptionInDynamicPage = indexOfContainsInList(firstPage[indexOfHederInDynamicPage], "Descrip")
            indexOfDynamicInfo =  aPage[indexOfHeader+1]
            listOfDynamicDescription =  indexOfDynamicInfo[indexOfDescriptionInDynamicPage].split("\n")
            listOfPoNosOfAPage =  [s.split(" ")[-1] for s in listOfDynamicDescription if "po no" in s.lower()]
            listOfPoNos+=listOfPoNosOfAPage

        self.gstRate = get_list_containing(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in")-2],"%").split("\n")[-1].replace("%", "").strip()

        count = 0
        for index in range(len(listOfIndex)):
            aProductResult = {}
            aProductResult["vendor_code"] = ""
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            poNo =  listOfPoNos[count]
            if poNo.__contains__("OR"):
                aProductResult["or_po_no"] = poNo
            else:
                aProductResult["po_no"] = poNo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = listOfIndex[count]
            aProductResult["HSN/SAC"] = listOfHsn[count]
            aProductResult["Qty"] = listOfQty[count]
            aProductResult["Rate"] = listOfRate[count]
            aProductResult["Per"] = listOfPer[count]
            aProductResult["mrp"] = listOfRate[count]
            aProductResult["Amount"] =  listOfAmt[count]
            aProductResult["gst_type"] = gstType
            aProductResult["gst_rate"] =  self.gstRate
            aProductResult["tax_applied"] =  float(listOfAmt[count].replace(",",""))-float(listOfRate[count].replace(",",""))
            aProductResult["po_cost"] = ""

            products.append(aProductResult)
            count+=1

        return products, total_tax


    def getGstInformation(self):
        lastPage = self.tables[len(self.tables)]
        return {
            "gst_type": lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1], "GST")],
            "gst_rate":  self.gstRate
        }

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankDetails = lastPage[indexOfContainsInList(lastPage, "Bank De")][0].split("\n")
        return {
            "bank_name": bankDetails[indexOfContainsInList(bankDetails, "Bank Name")].split(" ")[2].replace(":",""),
            "account_number": bankDetails[indexOfContainsInList(bankDetails, "Bank Name")].split(" ")[-1],
            "ifs_code": bankDetails[indexOfContainsInList(bankDetails, "IFS")].split(":")[-1],
        }

    def getItemTotalInfo(self):
        returnData = {}
        lastPage = self.tables[len(self.tables)]
        totalCount = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_pcs"] = totalCount if totalCount.strip() != "" else "N/A"
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "OUTPUT")+1][0].split("\n")[0]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "OUTPUT")+1][0].split("\n")[-1]
        returnData["tax_rate"] = self.gstRate
        returnData["total_tax_percentage"] =  self.gstRate
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[-1]

        return returnData