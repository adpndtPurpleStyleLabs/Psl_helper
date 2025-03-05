from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing,extractNumbers
from fastapi import HTTPException
import re

class AbkasaDesignerApparelsPvtLtd:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.gstPercentage = ""

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "ABKASA")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0].strip(),
            "vendor_address": ", ".join(vendorInfo[:3]),
            "vendor_mob": "N/A",
            "vendor_gst": get_list_containing(vendorInfo, "GST").split(":")[-1].strip(),
            "vendor_email": get_list_containing(vendorInfo, "mail").split(":")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice").split("\n")[-1],
            "invoice_date": self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Dated")+1].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ", ".join(receiverInfo[2:4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        billToInfo =  billToInfo[indexOfContainsInList(billToInfo, "Bill to"): ]
        return {
            "billto_name": billToInfo[1],
            "billto_address":", ".join(billToInfo[2:4]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        gstTypeList = get_list_containing(get_list_containing(lastPage, "OUTPUT").split("\n"), "OUTPUT")
        gstPercentage = gstTypeList.split(" ")[indexOfContainsInList(gstTypeList.split(" "), "%")]
        self.gstPercentage = gstPercentage.strip()
        gstType = ""
        if gstTypeList.find("CGST") != -1:
            raise HTTPException(status_code=400, detail="For AbkasaDesignerApparelsPvtLtd CGST is not implemented")

        if gstTypeList.find("IGST")  != -1:
            gstType = "IGST"

        if gstTypeList.find("SGST") != -1:
            raise HTTPException(status_code=400, detail="For AbkasaDesignerApparelsPvtLtd SGST is not implemented")

        total_tax = {"IGST": lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)")-1][-1], "SGST": 0,
                     "CGST": 0, }


        indexOfHeader =indexOfContainsInList(self.tables[1], "Description")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")
        indexOfDiscount = indexOfContainsInList(firstPage[indexOfHeader], "Disc")

        listOfSrNo = firstPage[indexOfHeader + 1:][0][indexOfSr].split("\n")

        listOfPo= []
        listOfPoNoOnTop = get_list_containing(firstPage, "Buyer’s").split("\n")[-1].replace(" ","").split(",")
        if indexOfContainsInList(listOfPoNoOnTop, "Buyer")  is not -1:
            listOfPoNoOnTop.pop(indexOfContainsInList(listOfPoNoOnTop, "Buyer") )
        if len(listOfPoNoOnTop) > 0:
            listOfPo = listOfPoNoOnTop
        else:
            listOfPo =self.getListOfProductDescriptions(firstPage[indexOfHeader + 1:][0][indexOfItemname])
        listofHsn = firstPage[indexOfHeader + 1:][0][indexOfHsn].split("\n")
        listOfQty = firstPage[indexOfHeader + 1:][0][indexOfQty].split("\n")
        listOfAmount = firstPage[indexOfHeader + 1:][0][indexOfAmt].split("\n")
        listOfRate = firstPage[indexOfHeader + 1:][0][indexOfRate].split("\n")
        listOfDiscount = firstPage[indexOfHeader + 1:][0][indexOfDiscount].split("\n")

        products = []

        itemCount = 1
        for aIndex in range(0, len(listOfSrNo)):
            aPoNo = listOfPo[aIndex].split(",")
            aHsnNo = listofHsn[aIndex].strip()
            aQty = listOfQty[aIndex]
            aAmount = float(listOfAmount[aIndex].replace(",", ""))
            aDiscount = float(listOfDiscount[aIndex].replace("%", "").replace(" ", "").strip())


            quantityOfItem = float(extractNumbers(aQty))
            amountPerPiece = aAmount/quantityOfItem
            ratePerPiece = (amountPerPiece * 100) /aDiscount
            pieceCountIndex = 0
            while pieceCountIndex < quantityOfItem:
                aProductResult = {}
                aProductResult["or_po_no"] = "OR-"+aPoNo[pieceCountIndex]
                aProductResult["po_no"] = ""
                aProductResult["debit_note_no"] = ""
                aProductResult["vendor_code"] = ""
                aProductResult["index"] = itemCount
                aProductResult["HSN/SAC"] = aHsnNo
                aProductResult["Qty"] = "1 nos"
                aProductResult["Rate"] = ratePerPiece
                aProductResult["Per"] = "N/A"
                aProductResult["mrp"] = ratePerPiece
                aProductResult["Amount"] = amountPerPiece
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] = gstPercentage
                aProductResult["tax_applied"] = amountPerPiece * float(gstPercentage.replace("%", ""))/100
                aProductResult["gst_type"] = gstType
                products.append(aProductResult)
                itemCount+=1
                pieceCountIndex+=1

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
        returnData["tax_amount_in_words"] = \
        lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = get_list_containing(lastPage, "Tax Amount (in words)").split("\n")[indexOfContainsInList(get_list_containing(lastPage, "Tax Amount (in words)").split("\n"), "Tax Amount (in wo")].split(":")[-1].strip()
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] =lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] =lastPage[indexOfContainsInList(lastPage, "Taxable")+2][1]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")+2][-1]
        returnData["tax_rate"] =self.gstPercentage
        returnData["total_tax_percentage"] =self.gstPercentage
        return returnData

    def getListOfProductDescriptions(self, listOfProductsDesriptions):
        listOfProductsDesriptions = listOfProductsDesriptions.replace("PO NO", "PONO")
        listOfProductsDesriptions = listOfProductsDesriptions.split("\n")
        outputList = []
        letsStart = False
        searchType = "S NO"
        if indexOfContainsInList(listOfProductsDesriptions, "PONO") != -1:
            searchType = "PONO"

        i = -1
        while i < len(listOfProductsDesriptions)-1:
           i+=1
           if listOfProductsDesriptions[i].find("Output") != -1:
               break
           if listOfProductsDesriptions[i+1].find(searchType) == -1  and letsStart == False:
                continue
           else:
               letsStart = True
           temp = ""
           for j in range(i, len(listOfProductsDesriptions)-1):
               i = j
               if listOfProductsDesriptions[j + 1].find("Output") != -1:
                   outputList.append(temp)
                   break
               temp+=","+listOfProductsDesriptions[j+1]
               if listOfProductsDesriptions[j+2].find(searchType) != -1 :
                   outputList.append(temp)
                   break
        output2 =  [re.sub(r'[a-zA-Z]', '', s) for s in outputList]
        output3 = []
        for item in output2:
            temp = item[item.find("-")+1:].strip().replace(" , ", ",").replace(" ", ",").replace(",,", ",")
            if item == ",":
                output2.remove(item)
            if temp != "":
                output3.append(temp)
        return output3




