from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class Kalighata:
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
            "vendor_name": firstPageText[0],
            "vendor_address": firstPageText[1] + " " + firstPageText[2],
            "vendor_mob": firstPageText[indexOfContainsInList(firstPageText, "Ph ")],
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "GST No")],
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        invoiceDetails = firstPageText[indexOfContainsInList(firstPageText, "INV No")]
        return {
            "invoice_number": invoiceDetails[invoiceDetails.find("INV No"):invoiceDetails.find("Date")],
            "invoice_date": invoiceDetails[invoiceDetails.find("Date "):-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Bill to Party")
        return {
            "receiver_name": firstPageText[indexOfReceiver + 1][:firstPageText[indexOfReceiver + 1].find("INV")],
            "receiver_address": firstPageText[indexOfReceiver + 2][
                                :firstPageText[indexOfReceiver + 2].find("Vehic")] + " " + firstPageText[
                                    indexOfReceiver + 3] + " " + firstPageText[indexOfReceiver + 4][
                                                                 :firstPageText[indexOfReceiver + 4].find("Way")],
            "receiver_gst": firstPageText[indexOfReceiver + 5][0: firstPageText[indexOfReceiver + 5].find("PO")],
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Bill to Party")
        self.poNo = firstPageText[indexOfReceiver + 5][firstPageText[indexOfReceiver + 5].find("PO"):]
        return {
            "billto_name": firstPageText[indexOfReceiver + 1][:firstPageText[indexOfReceiver + 1].find("INV")],
            "billto_address": firstPageText[indexOfReceiver + 2][
                              :firstPageText[indexOfReceiver + 2].find("Vehic")] + " " + firstPageText[
                                  indexOfReceiver + 3] + " " + firstPageText[indexOfReceiver + 4][
                                                               :firstPageText[indexOfReceiver + 4].find("Way")],
            "billto_gst": firstPageText[indexOfReceiver + 5][0: firstPageText[indexOfReceiver + 5].find("PO")],
            "place_of_supply": firstPageText[indexOfContainsInList(firstPageText, "State")]
        }

    def getItemInfo(self):
        tables = self.tables
        firstTable = tables[1]
        firstPageByTabula = self.table_by_tabula[1]
        indexOfHeader = -1
        indexOfEndTotal = -1
        for index, aListOfTable in enumerate(tables.values()):
            if indexOfContainsInList(aListOfTable, "Description of Goods") != -1:
                indexOfHeader = indexOfContainsInList(aListOfTable, "Description of Goods")
            if indexOfContainsInList(aListOfTable, "TOTAL") != -1:
                indexOfEndTotal = indexOfContainsInList(aListOfTable, "TOTAL")
            if indexOfHeader != -1 and indexOfEndTotal != -1:
                break

        indexOfGstsTotals = indexOfContainsInList(firstPageByTabula, "IGST")
        totalsAndGstheaderList = firstPageByTabula[indexOfGstsTotals].split("\n")[0].split("$")
        totalsAndGst = firstPageByTabula[indexOfGstsTotals].split("\n")[1]

        hsnCode = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "HSN")]
        totalTaxablevalue = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "Taxable")]
        cGSTRate = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "CGST\rRate")]
        cGSTAmount = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "CGST Amount")].replace(",",
                                                                                                                   "")
        sGSTRate = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "SGST\rRate")]
        sGSTAmount = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "SGST Amount")].replace(",",
                                                                                                                   "")
        iGSTRate = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "IGST\rRate")]
        iGSTAmount = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "IGST Amount")].replace(",",
                                                                                                                   "")
        totalTaxAmount = totalsAndGst.split("$")[indexOfContainsInList(totalsAndGstheaderList, "Tax Amo")]
        self.taxableAmt = totalTaxablevalue
        self.totalTax = totalTaxAmount
        self.taxPercentage
        typeOfGst = ""
        if float(cGSTAmount) != 0:
            typeOfGst = typeOfGst + "CGST "
            self.taxPercentage = " CGST: " + cGSTRate
        if float(sGSTAmount) != 0:
            typeOfGst = typeOfGst + "SGST "
            self.taxPercentage = " SGST: " + sGSTRate
        if float(iGSTAmount) != 0:
            typeOfGst = typeOfGst + "IGST "
            self.taxPercentage = " IGST: " + iGSTRate

        total_tax = {
            "IGST": iGSTAmount,
            "SGST": sGSTAmount,
            "CGST": cGSTAmount,
        }

        if indexOfHeader != -1:
            products = []
            indexOfSrNo = indexOfContainsInList(firstTable[indexOfHeader], "S\n")
            indexOfDescriptionOfGoods = indexOfContainsInList(firstTable[indexOfHeader], "Descri")
            indexOfHsNCode = indexOfContainsInList(firstTable[indexOfHeader], "HSN")
            indexOfMrp = indexOfContainsInList(firstTable[indexOfHeader], "Descri")
            indexOfQty = indexOfContainsInList(firstTable[indexOfHeader], "Qty")
            indexOfPrice = indexOfContainsInList(firstTable[indexOfHeader], "Price")
            indexOfUnit = indexOfContainsInList(firstTable[indexOfHeader], "Unit")
            indexOfTaxRate = indexOfContainsInList(firstTable[indexOfHeader], "Tax\nRate")
            indexOfTaxAmount = indexOfContainsInList(firstTable[indexOfHeader], "Tax\nAmount")
            indexOfAmount = -1 if firstTable[indexOfHeader][-1] == "Amount" else 0

            for index in range(indexOfHeader + 1, indexOfEndTotal):
                if len(firstTable[index]) < 2:
                    break

                aProductResult = {}
                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                aProductResult["debit_note_no"] = ""
                if self.poNo.__contains__("OR"):
                    aProductResult["or_po_no"] = self.poNo
                else :
                    aProductResult["po_no"] = self.poNo

                aProductResult["index"] = firstTable[index][indexOfSrNo]
                aProductResult["vendor_code"] = firstTable[index][indexOfDescriptionOfGoods].split("\n")[-1]
                aProductResult["HSN/SAC"] = firstTable[index][indexOfHsNCode]
                aProductResult["Qty"] = firstTable[index][indexOfQty]
                aProductResult["Rate"] = firstTable[index][indexOfPrice]
                aProductResult["Per"] = firstTable[index][indexOfUnit]
                aProductResult["mrp"] = firstTable[index][indexOfPrice]
                aProductResult["Amount"] = firstTable[index][indexOfAmount]
                aProductResult["po_cost"] = firstTable[index][indexOfAmount]
                aProductResult["gst_type"] = typeOfGst
                aProductResult["gst_rate"] = firstTable[index][indexOfTaxRate]
                aProductResult["tax_applied"] = firstTable[index][indexOfTaxAmount]
                aProductResult["po_no"] = self.poNo
                products.append(aProductResult)

            return products, total_tax

    def getVendorBankInfo(self):
        firstPageByTabula = self.table_by_tabula[1]
        bankDetails = firstPageByTabula[-1].split("$")[
            indexOfContainsInList(firstPageByTabula[-1].split("$"), "BANK NAME")].split("\r")
        return {
            "bank_name": bankDetails[indexOfContainsInList(bankDetails, "NAME")],
            "account_number": bankDetails[indexOfContainsInList(bankDetails, "AC NO")],
            "ifs_code": bankDetails[indexOfContainsInList(bankDetails, "IFSC")],
        }

    def getItemTotalInfo(self):
        firstPageByTabula = self.table_by_tabula[1]
        firstPageTable = self.tables[1]

        returnData = {}
        returnData["tax_amount_in_words"] = firstPageByTabula[-1].split("$")[
            indexOfContainsInList(firstPageByTabula[-1].split("$"), "Only")]
        returnData["amount_charged_in_words"] = (firstPageTable[indexOfContainsInList(firstPageTable, "Only")][0][
                                                firstPageTable[indexOfContainsInList(firstPageTable, "Only")][0].find(
                                                    ":")+1:firstPageTable[indexOfContainsInList(firstPageTable, "Only")][
                                                             0].find("Only") + 4]).strip()
        returnData["total_pcs"] = firstPageTable[indexOfContainsInList(firstPageTable, "TOTAL")][4]
        returnData["total_amount_after_tax"] = firstPageTable[indexOfContainsInList(firstPageTable, "TOTAL")][-1]
        returnData["total_b4_tax"] = self.taxableAmt
        returnData["total_tax"] = firstPageTable[indexOfContainsInList(firstPageTable, "TOTAL")][-2]
        returnData["tax_rate"] = self.totalTax
        returnData["total_tax_percentage"] = self.taxPercentage
        return returnData