from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class Lashkaraa:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "SKB")][
            indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "SKB")], "SKB")].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": vendorInfo[1] + " " + vendorInfo[2] + " " + vendorInfo[3] + " " + vendorInfo[
                indexOfContainsInList(vendorInfo, "Sta")],
            "vendor_mob": "",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "E-M")]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invo")][
            indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Invo")], "Invo")].split("\n")
        return {
            "invoice_number": invoiceInfo[-1].split(" ")[0],
            "invoice_date": firstPageText[indexOfContainsInList(firstPageText, "Date")][0].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Consi")][
            indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Consi")], "Consi")].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": receiverInfo[2] + " " + receiverInfo[3] + " " + receiverInfo[4],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")],
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][
            indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Bill to")], "Bill to")].split(
            "\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": billToInfo[2] + " " + billToInfo[3] + " " + billToInfo[4],
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "Place")],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")]
        }

    def getItemInfo(self):
        firstPage = self.tables[1]
        indexOfHeader = indexOfContainsInList(firstPage, "Descrip")
        indexOfSrNo = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
        indexOfProductInfo = indexOfContainsInList(firstPage[indexOfHeader], "Desc")
        indexOfHsnCode = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quanti")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfUnit = indexOfContainsInList(firstPage[indexOfHeader], "per")
        indexOfAmount = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

        indexOfTaxRateHeader = indexOfContainsInList(firstPage, "Amount Char") + 1
        iGSTPercentage = firstPage[indexOfTaxRateHeader + 2][
            indexOfContainsInList(firstPage[indexOfTaxRateHeader], "IGST")]

        # assuming only one product
        products = []
        aProductResult = {}
        aProductResult["index"] = firstPage[indexOfHeader + 1][indexOfSrNo]
        aProductResult["vendor_code"] = firstPage[indexOfHeader + 1][indexOfProductInfo]
        aProductResult["or_po_no"] = ""
        aProductResult["debit_note_no"] = ""
        aProductResult["po_no"] = self.tables[1][indexOfContainsInList(self.tables[1], "Order No")][
            indexOfContainsInList(self.tables[1][indexOfContainsInList(self.tables[1], "Order No")], "Order No")].split(
            "\n")[-1]
        aProductResult["HSN/SAC"] = firstPage[indexOfHeader + 1][indexOfHsnCode]
        aProductResult["Qty"] = firstPage[indexOfHeader + 1][indexOfQty]
        aProductResult["Rate"] = float(firstPage[indexOfHeader + 1][indexOfRate].replace(",",""))
        aProductResult["Per"] = firstPage[indexOfHeader + 1][indexOfUnit]
        aProductResult["mrp"] = float(firstPage[indexOfHeader + 1][indexOfAmount].split("\n")[0].replace(",",""))
        aProductResult["Amount"] = float(firstPage[indexOfHeader + 1][indexOfAmount].split("\n")[0].replace(",",""))
        appliedTax = float(iGSTPercentage.replace("%", "").strip()) * float(
            firstPage[indexOfHeader + 1][indexOfAmount].split("\n")[0].replace(",", "").strip()) / 100
        aProductResult["po_cost"] = appliedTax + float(
            firstPage[indexOfHeader + 1][indexOfAmount].split("\n")[0].replace(",", "").strip())
        aProductResult["gst_type"] = "IGST"
        aProductResult["gst_rate"] = float(iGSTPercentage.replace("%","").strip())
        aProductResult["tax_applied"] = appliedTax
        products.append(aProductResult)
        total_tax = {
            "IGST": appliedTax,
            "SGST": 0,
            "CGST": 0,
        }

        return products, total_tax

    def getVendorBankInfo(self):
        firstPage = self.tables[1]
        bankAdCode = firstPage[indexOfContainsInList(firstPage, "BANK AD CODE")][0].split("\n")[
            indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "BANK AD CODE")][0].split("\n"), "BANK")]

        return {
            "bank_name": bankAdCode[:bankAdCode.find("for")],
            "account_number": "",
            "ifs_code": "",
        }

    def getItemTotalInfo(self):
        firstPage = self.tables[1]
        totalList = firstPage[indexOfContainsInList(firstPage, "Amount Char") - 1]
        listOfTaxheader = firstPage[indexOfContainsInList(firstPage, "Amount Char") + 1]

        returnData = {}
        returnData["tax_amount_in_words"] = \
        firstPage[indexOfContainsInList(firstPage, "Tax Amount (in")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = \
        firstPage[indexOfContainsInList(firstPage, "Amount Char")][0].split("\n")[-1]
        returnData["total_pcs"] = totalList[indexOfContainsInList(totalList, "PCS")]
        returnData["total_amount_after_tax"] = float(totalList[-1].split(" ")[-1].replace(",",""))
        returnData["total_b4_tax"] = float(firstPage[indexOfContainsInList(firstPage, "Amount Char") + 3][
            indexOfContainsInList(listOfTaxheader, "Taxab")].replace(",","").strip())
        returnData["total_tax"] = float(firstPage[indexOfContainsInList(firstPage, "Amount Char") + 3][
            indexOfContainsInList(listOfTaxheader, "IGST") + 1].replace(",","").strip())
        returnData["tax_rate"] =  float(firstPage[indexOfContainsInList(firstPage, "Amount Char") + 3][
            indexOfContainsInList(listOfTaxheader, "IGST")].replace("%","").strip())
        returnData["total_tax_percentage"] = returnData["tax_rate"]
        return returnData