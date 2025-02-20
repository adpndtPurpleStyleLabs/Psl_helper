from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class SheetalBatra:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalmountBeforetax = 0
        self.totaltax = 0
        self.taxRate = ""

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        return {
            "vendor_name": firstPageText[0][0].split("\n")[0],
            "vendor_address": firstPageText[0][0].split("\n")[1] + " " + firstPageText[0][0].split("\n")[2],
            "vendor_mob": "",
            "vendor_gst": firstPageText[0][0].split("\n")[3],
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageTable = self.tables[1]
        firstPageText = self.text_data[1].split("\n")
        return {
            "invoice_number": firstPageTable[indexOfContainsInList(firstPageTable, "Invoice")][
                indexOfContainsInList(firstPageTable[indexOfContainsInList(firstPageTable, "Invoice")],
                                      "Invoice")].split("\n")[-1],
            "invoice_date": firstPageText[indexOfContainsInList(firstPageText, "Dated") + 1].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageTable = self.tables[1]
        receiverInfo = firstPageTable[indexOfContainsInList(firstPageTable, "Consignee")][0].split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "M/s")],
            "receiver_address": receiverInfo[2] + " " + receiverInfo[indexOfContainsInList(receiverInfo, "State")],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")],
        }

    def getBillingInfo(self):
        firstPageTable = self.tables[1]
        billToInfo = firstPageTable[indexOfContainsInList(firstPageTable, "Bill to")][0].split("\n")
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "M/s")],
            "billto_address": billToInfo[2] + " " + billToInfo[4],
            "place_of_supply": billToInfo[4],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")]

        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]
        indexOfTaxHeader = indexOfContainsInList(pages[len(pages)], "E. &") + 1
        self.totalItems = lastPage[indexOfTaxHeader - 2][indexOfContainsInList(lastPage[indexOfTaxHeader - 2], "Pcs")]
        taxHeader = lastPage[indexOfTaxHeader]
        taxTotals = lastPage[indexOfTaxHeader + 2]
        cGSTIndex = indexOfContainsInList(taxHeader, "Central")
        sGSTIndex = indexOfContainsInList(taxHeader, "State Tax")

        if cGSTIndex is -1:
            cGSTIndex = indexOfContainsInList(taxHeader, "CGST")
        if sGSTIndex is -1:
            sGSTIndex = indexOfContainsInList(taxHeader, "SGST")

        cGstPercentage = taxTotals[cGSTIndex]
        sGstPercentage = taxTotals[sGSTIndex + 1]
        for aPage in pages.values():
            indexOfHeader = indexOfContainsInList(aPage, "Descri")
            headerOfProduct = aPage[indexOfContainsInList(aPage, "Descri")]
            indexOfSrNo = indexOfContainsInList(headerOfProduct, "Sl")
            indexOfDescription = indexOfContainsInList(headerOfProduct, "Descri")
            indexOfHsn = indexOfContainsInList(headerOfProduct, "HSN")
            indexOfQty = indexOfContainsInList(headerOfProduct, "Quantity")
            indexOfRate = indexOfContainsInList(headerOfProduct, "Rate")
            indexOfPer = indexOfContainsInList(headerOfProduct, "per")
            indexOfAmount = indexOfContainsInList(headerOfProduct, "Amount")
            products = []

            noOfProductsInPage = len(aPage[indexOfHeader + 1][indexOfSrNo].split("\n"))
            listOfPoOrOrPo = aPage[indexOfHeader + 1][indexOfDescription].split("\n")[1::2][0:noOfProductsInPage]
            totaltax = 0
            totalSgst = 0
            totalCgst = 0
            runningSumTotalmountBeforetax = 0
            for i in range(0, noOfProductsInPage):
                mrp = float(aPage[indexOfHeader + 1][indexOfAmount].split("\n")[i].replace(",", ""))
                runningSumTotalmountBeforetax = runningSumTotalmountBeforetax + mrp
                productCgstAmount = (float(cGstPercentage.replace("%", "")) * mrp / 100)
                productSgstAmount = (float(sGstPercentage.replace("%", "")) * mrp / 100)
                totaltax = totaltax + productCgstAmount + productSgstAmount
                totalCgst = totalCgst + productCgstAmount
                totalSgst = totalSgst + productSgstAmount
                aProductResult = {}
                aProductResult["debit_note_no"] = ""
                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                if str(listOfPoOrOrPo[i]).lower().__contains__("or"):
                    aProductResult["or_po_no"] = ("OR-"+listOfPoOrOrPo[i].split(" ")[-1]).replace(" ","")
                else:
                    aProductResult["po_no"] = listOfPoOrOrPo[i]

                aProductResult["index"] = aPage[indexOfHeader + 1][indexOfSrNo].split("\n")[i]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = aPage[indexOfHeader + 1][indexOfHsn].split("\n")[i]
                aProductResult["Qty"] = aPage[indexOfHeader + 1][indexOfQty].split("\n")[i]
                aProductResult["Rate"] = aPage[indexOfHeader + 1][indexOfRate].split("\n")[i]
                aProductResult["Per"] = aPage[indexOfHeader + 1][indexOfPer].split("\n")[i]
                aProductResult["mrp"] = aPage[indexOfHeader + 1][indexOfAmount].split("\n")[i]
                aProductResult["Amount"] = aPage[indexOfHeader + 1][indexOfAmount].split("\n")[i]
                aProductResult["po_cost"] = productCgstAmount + productSgstAmount + mrp
                gstType = ""
                if float(cGstPercentage.replace("%", "")) > 0:
                    gstType = gstType + " CGST " + cGstPercentage
                if float(sGstPercentage.replace("%", "")) > 0:
                    gstType = gstType + " SGST " + sGstPercentage
                self.taxRate = gstType
                aProductResult["gst_type"] = gstType
                aProductResult["gst_rate"] = sGstPercentage
                aProductResult["tax_applied"] = productCgstAmount
                products.append(aProductResult)
            total_tax = {
                "IGST": 0,
                "SGST": totalSgst,
                "CGST": totalCgst,
            }
            self.totalmountBeforetax = runningSumTotalmountBeforetax
            self.totaltax = totaltax
            return products, total_tax

    def getVendorBankInfo(self):
        return {
            "bank_name": "",
            "account_number": "",
            "ifs_code": "",
        }

    def getItemTotalInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]
        indexOfTaxHeader = indexOfContainsInList(pages[len(pages)], "E. &") + 1
        self.totalItems = lastPage[indexOfTaxHeader - 2][indexOfContainsInList(lastPage[indexOfTaxHeader - 2], "Pcs")]

        returnData = {}
        returnData["tax_amount_in_words"] = \
        lastPage[indexOfTaxHeader + 4][indexOfContainsInList(lastPage[indexOfTaxHeader + 4], "Tax Amount")].split("\n")[
            0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount C")][0].split("\n")[-1]
        returnData["total_pcs"] = self.totalItems
        returnData["total_amount_after_tax"] = lastPage[indexOfTaxHeader - 2][-1].split(" ")[-1]
        returnData["total_b4_tax"] = self.totalmountBeforetax
        returnData["total_tax"] = self.totaltax
        returnData["tax_rate"] = self.taxRate
        returnData["total_tax_percentage"] = self.taxRate
        return returnData
