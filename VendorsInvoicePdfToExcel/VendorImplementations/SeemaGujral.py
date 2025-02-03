from VendorsInvoicePdfToExcel.helper import get_state_using_gst_id
from fastapi import HTTPException
from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class SeemaGujral:
    def __init__(self, tables, text):
        self.tables = tables
        self.text = text

    def getVendorInfo(self):
        firstPage = self.tables[1]
        for atable in firstPage:
            for alist in atable:
                if str(alist).__contains__('MOB') and str(alist).__contains__('SEEMA') and str(alist).__contains__(
                        'E-Mail') and str(alist).__contains__('GST'):
                    return {
                        "vendor_name": str(alist).split("\n")[0],
                        "vendor_address": alist[:alist.find("MOB")],
                        "vendor_mob": str(alist).split("\n")[3],
                        "vendor_gst": str(alist).split("\n")[4],
                        "vendor_email": str(alist).split("\n")[6]
                    }
        raise HTTPException(status_code=400, detail="Error while getting Vendor Information")

    def getInvoiceInfo(self):
        firstPage = self.tables[1]
        for atable in firstPage:
            for alist in atable:
                if str(alist).__contains__('Invoice No'):
                    alist.split("\n")
                    return {
                        "invoice_number": alist.split("\n")[indexOfContainsInList( alist.split("\n"), "Invoice")+1].split(" ")[0],
                        "invoice_date": self.text[1].split("\n")[
                                            self.indexOfContainsInList(self.text[1].split("\n"), "Date")][
                                        self.text[1].split("\n")[
                                            self.indexOfContainsInList(self.text[1].split("\n"), "Date")].find(
                                            ":") + 1:],
                    }
        raise HTTPException(status_code=400, detail="Error while getting Invoice Information")

    def getReceiverInfo(self):
        firstPage = self.tables[1]
        for atable in firstPage:
            for alist in atable:
                if str(alist).__contains__('Consignee (Ship to)') and str(alist).__contains__('PSL'):
                    return {
                        "receiver_name": str(alist.split("\n")[self.indexOfContainsInList(alist.split("\n"),
                                                                                          "to)") + 1: self.indexOfContainsInList(
                            alist.split("\n"), "to)") + 2][0]),
                        "receiver_address": alist[alist.find("to)") + 3: alist.find("GST")].replace("\n", " "),
                        "receiver_gst": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "GST")],
                    }
        raise HTTPException(status_code=400, detail="Error while getting Receiver Information")

    def getBillingInfo(self):
        firstPage = self.tables[1]
        for atable in firstPage:
            for alist in atable:
                if str(alist).__contains__('Buyer (Bill to)') and str(alist).__contains__('PSL'):
                    return {
                        "billto_name": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"),"to)") + 1: self.indexOfContainsInList(alist.split("\n"), "to)") + 2][0],
                        "billto_address": alist[alist.find("to)") + 3: alist.find("GST")].replace("\n", " "),
                        "billto_gst": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "GST")],
                        "place_of_supply": get_state_using_gst_id(float(alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "GST")].split(":")[1][:2]))
                    }

    def getItemInfo(self):
        products = []
        total_tax = {
            "IGST" : 0,
            "SGST" : 0,
            "CGST" : 0,
        }
        for paneNo, aPage in enumerate(self.tables.values()):
            indexOfProducts = 0
            for index, atable in enumerate(aPage):
                if indexOfProducts != 0:
                    break
                for alist in atable:
                    if str(alist).__contains__('Description of Goods'):
                        indexOfProducts = index + 1
                        break

            taxInfo = self.getGstInformation()
            listOfProducts = aPage[indexOfProducts:]
            productsInfo = listOfProducts[0]
            for index, aProduct in enumerate(productsInfo[0].split("\n")):
                if aProduct == "" :
                    continue

                tax_applied = (float(productsInfo[4].split("\n")[index].replace(",", "")) * float(
                    taxInfo["gst_rate"].replace("%", ""))) / 100
                itemDesc = self.makeItemDescriptionData(productsInfo[1])

                aProductResult= {}
                aProductResult["index"] = aProduct
                aProductResult["vendor_code"] = " ".join(itemDesc[index].split("\n")[0].split(" ")[:-1])
                aProductResult["HSN/SAC"] = itemDesc[index].split("\n")[0].split(" ")[-1]
                aProductResult["Qty"] = productsInfo[3].split("\n")[index]
                aProductResult["Rate"] = productsInfo[4].split("\n")[index]
                aProductResult["Per"] = productsInfo[5].split("\n")[index]
                aProductResult["mrp"] = productsInfo[2].split("\n")[index]
                aProductResult["Amount"] = productsInfo[6].split("\n")[index]
                aProductResult["gst_type"] = taxInfo["gst_type"]
                aProductResult["gst_rate"] = taxInfo["gst_rate"]
                aProductResult["tax_applied"] = tax_applied
                aProductResult["po_cost"] = float(productsInfo[4].split("\n")[index].replace(",", "")) + tax_applied
                if aProductResult["gst_type"] == "IGST":
                    total_tax["IGST"] = total_tax["IGST"] + tax_applied
                elif aProductResult["gst_type"] == "SGST":
                    total_tax["SGST"] = total_tax["SGST"] + tax_applied
                elif aProductResult["gst_type"] == "CGST":
                    total_tax["CGST"] = total_tax["CGST"] + tax_applied


                if productsInfo[1].__contains__('MARK DOWN') and productsInfo[1].__contains__(
                        'AGAINTS'):
                    debitNote = itemDesc[index][itemDesc[index].find("DEBIT"): itemDesc[index].find("MARK")]
                    aProductResult["po_no"] = ""
                    aProductResult["or_po_no"] =""
                    aProductResult["debit_note_no"] =debitNote[debitNote.find("NO.")+3 :]

                elif productsInfo[1].__contains__('MARK DOWN'):
                    po = ""
                    or_po = ""
                    id_2 = itemDesc[index].split("\n")[
                        self.indexOfContainsInList(itemDesc[index].split("\n"), "MARK") - 1]
                    if id_2.__contains__('OR') or id_2.__contains__('AD') or id_2.__contains__('CG'):
                        or_po = id_2
                    else:
                        po = id_2
                    aProductResult["po_no"] = po
                    aProductResult["or_po_no"] = or_po
                    aProductResult["debit_note_no"] = ""

                else:
                    aProductResult["vendor_code"] = productsInfo[1].split("\n")[(index) * 2]
                    aProductResult["po_no"] = productsInfo[1].split("\n")[(index * 2) + 1]
                    aProductResult["or_po_no"] = ""
                    aProductResult["debit_note_no"] = ""
                    aProductResult["HSN/SAC"] = productsInfo[2].split("\n")[index]
                    aProductResult["mrp"] = productsInfo[4].split("\n")[index]

                products.append(aProductResult)
        return products, total_tax


    def getGstInformation(self):
        lengthOfPdf = len(self.tables)
        listOfTableOfGst = self.tables[lengthOfPdf][self.indexOfContainsInList(self.tables[lengthOfPdf], " @")]
        gstInfoList = listOfTableOfGst[self.indexOfContainsInList(listOfTableOfGst, " @")].split("\n")
        getInfoStr = gstInfoList[self.indexOfContainsInList(gstInfoList, " @")]
        return {
            "gst_type": str(getInfoStr.split(" ")[0]).upper(),
            "gst_rate": getInfoStr[getInfoStr.find("@") + 1: getInfoStr.find("%") + 1]
        }

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        for atable in lastPage:
            for alist in atable:
                if str(alist).__contains__('Company’s Bank'):
                    return {
                        "bank_name": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "Bank Name")],
                        "account_number": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "A/c")],
                        "ifs_code": alist.split("\n")[self.indexOfContainsInList(alist.split("\n"), "IFS")],
                    }

    def getItemTotalInfo(self):
        returnData = {}
        indexOfTotalPCS = 0
        lastPage = self.tables[len(self.tables)]
        for index, atable in enumerate(lastPage):
            for alist in atable:
                if str(alist).__contains__('Company’s Bank'):
                    returnData["tax_amount_in_words"] = alist.split("\n")[
                        self.indexOfContainsInList(alist.split("\n"), "Tax Amount")].split(":")[-1]
                if str(alist).__contains__('Amount Chargeable'):
                    indexOfTotalPCS = index - 1
                    returnData["amount_charged_in_words"] = alist[alist.find("O.E\n") + 4:]

        if (indexOfTotalPCS != 0):
            returnData["total_pcs"] = lastPage[indexOfTotalPCS][
                self.indexOfContainsInList(lastPage[indexOfTotalPCS], "PC")]
            returnData["total_amount_after_tax"] = lastPage[indexOfTotalPCS][-1]
            returnData["total_b4_tax"] = lastPage[indexOfTotalPCS - 1][0].split("\n")[0]
            returnData["total_tax"] = lastPage[indexOfTotalPCS - 1][0].split("\n")[1]
            returnData["tax_rate"] = lastPage[indexOfTotalPCS - 1][0].split("\n")[1]
            returnData["total_tax_percentage"] = lastPage[indexOfTotalPCS + 4][
                self.indexOfContainsInList(lastPage[indexOfTotalPCS + 4], "%")]

        return returnData

    def indexOfContainsInList(self, list, word):
        count = 0
        for alist in list:
            if str(alist).__contains__(word):
                return count
            count += 1
        return 0

    def makeItemDescriptionData(self, inputData):
        productDescriptionData = []
        listOfWords = inputData.split("\n")
        length = len(listOfWords)
        i = 0
        while (i < length - 1):
            prodInfo = str(listOfWords[i])
            while (i < length - 1):
                if listOfWords[i + 1].__contains__("MARK") or listOfWords[i + 1].__contains__("AGAINTS") or listOfWords[
                    i + 1].__contains__("OR") or listOfWords[
                    i + 1].__contains__("PCS"):
                    prodInfo = prodInfo + "\n " + str(listOfWords[i + 1])
                    i += 1
                else:
                    i += 1
                    break
            productDescriptionData.append(prodInfo)
        return productDescriptionData