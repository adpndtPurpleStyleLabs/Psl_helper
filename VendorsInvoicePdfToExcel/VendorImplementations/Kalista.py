from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of, get_list_containing

class Kalista:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalPercentage = 0
        self.totalGstAmount = 0

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "kalis")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:4]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1].strip(),
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice no").split("\n")[-1].split(" ")[0],
            "invoice_date": self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "dated")+1].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Bill to"):]

        return {
            "receiver_name": receiverInfo[1],
            "receiver_address":",".join(receiverInfo[2:5]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill to"):]
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:6]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "supply")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[1]
        tabulaFirstPage = self.table_by_tabula[1][0].split("\n")
        indexOfDescTabula = indexOfContainsInList(tabulaFirstPage, "Description")+1
        listOfProductsTabula = tabulaFirstPage[indexOfDescTabula].split("\r")
        gstType = []
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            gstType.append("CGST")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType.append("IGST")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            gstType.append("SGST")

        listOfTaxHeader = lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1]
        gstType = "_".join(gstType)
        total_tax = {"IGST": 0,
                     "SGST": 0,
                     "CGST": 0, }

        total_tax_percentage = {"IGST": 0,
                     "SGST": 0,
                     "CGST": 0, }

        if gstType == "CGST_SGST":
            indexOfCGST = indexOfContainsInList(listOfTaxHeader, "CGST")
            indexOfSGST = indexOfContainsInList(listOfTaxHeader, "SGST") +1
            total_tax_percentage["CGST"] = float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)")-2][indexOfCGST].split("\n")[-1].replace("%", ""))
            total_tax_percentage["SGST"] = float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)")-2][indexOfSGST].split("\n")[-1].replace("%", ""))
            total_tax["CGST"] =  float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)") - 1][indexOfCGST+1].replace(",", ""))
            total_tax["SGST"] = float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)") - 1][indexOfSGST+1].replace(",", ""))

        if gstType == "IGST":
            indexOfIGST = indexOfContainsInList(listOfTaxHeader, "IGST")
            total_tax_percentage["IGST"] = float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)")-2][indexOfIGST].split("\n")[-1].replace("%", ""))
            total_tax["IGST"] =  float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words)") - 1][indexOfIGST+1].replace(",", ""))

        self.totalPercentage = total_tax_percentage["SGST"] + total_tax_percentage["CGST"] + total_tax_percentage["IGST"]
        self.totalGstAmount = total_tax["SGST"] + total_tax["CGST"] + total_tax["IGST"]
        products = []

        for index in range(1, len(pages) + 1):
            page = pages[index]
            indexOfHeader = indexOfContainsInList(self.tables[1], "description")
            indexOfSr = indexOfContainsInList(page[indexOfHeader], "Sl")
            indexOfQty = indexOfContainsInList(page[indexOfHeader], "Quantity")
            indexOfRate = indexOfContainsInList(page[indexOfHeader], "Rate")
            indexOfUnit = indexOfContainsInList(page[indexOfHeader], "per")
            indexOfAmt = indexOfContainsInList(page[indexOfHeader], "Amount")

            itemsTable = page[indexOfHeader + 1]
            numberOfItems = len(itemsTable[indexOfSr].split("\n"))
            for index in range(numberOfItems):
                aProductResult = {}

                aProductResult["index"] = itemsTable[indexOfSr].split("\n")[index]
                poNoInfo = itemsTable[1].split("\n")[find_nth_occurrence_of(itemsTable[1].split("\n"), "PO NO",index+1)].split(" ")[2]
                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                if poNoInfo.find("OR") is not -1:
                    aProductResult["or_po_no"] = poNoInfo
                else:
                    aProductResult["po_no"] = poNoInfo
                aProductResult["HSN/SAC"] = listOfProductsTabula[find_nth_occurrence_of(listOfProductsTabula, "Pcs", index+1)].split(" ")[0]
                aProductResult["Qty"] =itemsTable[indexOfQty-1].split("\n")[index]
                aProductResult["Rate"] = itemsTable[indexOfRate-1].split("\n")[index]
                amount = itemsTable[indexOfRate-1].split("\n")[index]
                aProductResult["mrp"] =aProductResult["Rate"]
                aProductResult["Amount"] =  itemsTable[indexOfAmt-1].split("\n")[index]
                aProductResult["tax_applied"] = (float(amount.replace(",","")) * self.totalPercentage)/100
                aProductResult["gst_rate"] = self.totalPercentage
                aProductResult["Per"] = itemsTable[indexOfUnit-1].split("\n")[index]
                aProductResult["gst_type"] = gstType
                products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankInfo = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
        if indexOfContainsInList(lastPage,"Bank Details") == -1:
            return {
                "bank_name": "",
                "account_number": "",
                "ifs_code": "",
            }

        return {
            "bank_name": get_list_containing(bankInfo, "Bank Name").split(":")[-1].strip(),
            "account_number": get_list_containing(bankInfo, "A/c No").split(":")[-1].strip(),
            "ifs_code": get_list_containing(bankInfo, "IFS Cod").split(":")[-1].strip(),
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = \
            lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[
            -1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][
            indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Total")], "Pcs")]
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in") - 1][1]
        returnData["total_tax"] = self.totalGstAmount
        returnData["tax_rate"] = self.totalPercentage
        returnData["total_tax_percentage"] = self.totalPercentage
        return returnData
