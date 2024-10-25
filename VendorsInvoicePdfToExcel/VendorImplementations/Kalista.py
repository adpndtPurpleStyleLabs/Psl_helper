from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class Kalista:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.taxableAmt = -1
        self.totalTax = -1
        self.taxPercentage = ""
        self.poNo = ""


    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "vendor_name": firstPageText[indexOfContainsInList(firstPageText, "Ref.")+1],
            "vendor_address":  ' '.join(firstPageText[indexOfContainsInList(firstPageText, "Ref.")+2:indexOfContainsInList(firstPageText, "State")-1]),
            "vendor_mob": "",
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "GST")],
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        invoiceDetails = firstPageText[indexOfContainsInList(firstPageText, "Invoice No")]
        return {
            "invoice_number": invoiceDetails[:invoiceDetails.find("Date")].strip(),
            "invoice_date": invoiceDetails[invoiceDetails.find("Date"):]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Party")
        sublistOfReceiver  = firstPageText[indexOfReceiver:indexOfContainsInList(firstPageText, "Place of")]

        return {
            "receiver_name": firstPageText[indexOfReceiver].split(":")[-1].strip(),
            "receiver_address": firstPageText[indexOfReceiver+1] + " " + firstPageText[indexOfReceiver+2],
            "receiver_gst": sublistOfReceiver[ indexOfContainsInList(sublistOfReceiver, "GST")] ,
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Party")
        sublistOfReceiver = firstPageText[indexOfReceiver:indexOfContainsInList(firstPageText, "Place of")+1]

        return {
            "billto_name": firstPageText[indexOfReceiver].split(":")[-1].strip(),
            "billto_address": firstPageText[indexOfReceiver+1] + " " + firstPageText[indexOfReceiver+2],
            "billto_gst": sublistOfReceiver[ indexOfContainsInList(sublistOfReceiver, "GST")],
            "place_of_supply":firstPageText[indexOfContainsInList(firstPageText, "Place")].split(": ")[-1].strip()
        }

    def getItemInfo(self):
        firsttable_by_tabula = self.table_by_tabula
        firstTable = self.tables[1]
        indexOfheader = indexOfContainsInList(firstTable, "Descrip")
        indexOfIndex = indexOfContainsInList(firstTable[indexOfheader], "Sl")
        indesOfDescGoods = indexOfContainsInList(firstTable[indexOfheader], "Desc")
        indexOfHsnCode = indexOfContainsInList(firstTable[indexOfheader], "HSN")
        indexOfQty =indexOfContainsInList(firstTable[indexOfheader], "Quant")
        indexOfRate = indexOfContainsInList(firstTable[indexOfheader], "Rate")
        indexOfAmount = indexOfContainsInList(firstTable[indexOfheader], "Amount")
        indexOfUnit = indexOfContainsInList(firstTable[indexOfheader], "per")

        noOfProducts = len(firstTable[indexOfheader+1][indexOfIndex].split("\n"))
        indexOfHeaderFromText = indexOfContainsInList(self.text_data[1].split("\n"), "Description")

        products = []
        firstpagelistoftext = self.text_data[1].split("\n")
        indexOfTaxHeader = indexOfContainsInList(firstpagelistoftext, "Amount Chargeable")+2
        indexOfTaxCGST= indexOfContainsInList(firstpagelistoftext[indexOfTaxHeader].split(" "), "CGST")
        indexOfTaxSGST= indexOfContainsInList(firstpagelistoftext[indexOfTaxHeader].split(" "), "SGST")

        indexOf1stProduct = -1
        for i in range(indexOfHeaderFromText, len(firstpagelistoftext)):
            if firstpagelistoftext[i].split(" ")[0] == str(1):
                indexOf1stProduct = i
                break


        for i in range(0,noOfProducts):
            endIndexOfProduct = -1
            for j in range(indexOf1stProduct, len(firstpagelistoftext)):
                if firstpagelistoftext[j].split(" ")[0] == str(i+2):
                    endIndexOfProduct = j
                    break
            sublistOfProdInfo = firstpagelistoftext[indexOf1stProduct:endIndexOfProduct]
            indexOf1stProduct = endIndexOfProduct

            aProductResult = {}
            aProductResult["index"] = firstTable[indexOfheader+1][indexOfIndex].split("\n")[i]
            if len(sublistOfProdInfo) == 3:
                aProductResult["vendor_code"] =  sublistOfProdInfo[indexOfContainsInList(sublistOfProdInfo, "Po No") + 1]
            else :
                aProductResult["vendor_code"] = sublistOfProdInfo[indexOfContainsInList(sublistOfProdInfo, "Po No")].split(" ")[-1]

            aProductResult["HSN/SAC"] = firstTable[indexOfheader+1][indexOfHsnCode].split("\n")[i]
            aProductResult["Qty"] = firstTable[indexOfheader+1][indexOfQty].split("\n")[i]
            aProductResult["Rate"] = firstTable[indexOfheader+1][indexOfRate].split("\n")[i]
            aProductResult["Per"] =firstTable[indexOfheader+1][indexOfUnit].split("\n")[i]
            aProductResult["mrp"] =  firstTable[indexOfheader+1][indexOfRate].split("\n")[i]
            aProductResult["Amount"] = firstTable[indexOfheader+1][indexOfAmount].split("\n")[i]
            # aProductResult["po_cost"]  =

