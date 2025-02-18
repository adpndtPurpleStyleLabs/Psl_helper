from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing, split_every_second_space, \
    convert_amount_to_words

class BasilLeaf:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = ""
        self.taxableAmount = ""

    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "vendor_name": firstPageText[indexOfContainsInList(firstPageText, "X &")],
            "vendor_address": ", ".join(firstPageText[indexOfContainsInList(firstPageText, "X &") + 1].split(",")[:-1]),
            "vendor_mob": firstPageText[indexOfContainsInList(firstPageText, "PH")].split(" ")[-1],
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "GST")].split(" ")[-1],
            "vendor_email": firstPageText[indexOfContainsInList(firstPageText, "email")].split(" ")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "invoice_number": firstPageText[indexOfContainsInList(firstPageText, "Invoice no") + 1].split(" ")[-2],
            "invoice_date": firstPageText[0].split(",")[0]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfo = firstPageText[
                       indexOfContainsInList(firstPageText, "Customer name"):indexOfContainsInList(firstPageText, "#")]
        return {
            "receiver_name": receiverInfo[0].split(":")[-1].strip(),
            "receiver_address": ", ".join(receiverInfo[
                                          indexOfContainsInList(receiverInfo, "Address"):indexOfContainsInList(
                                              receiverInfo, "GST")]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        billToInfo = firstPageText[
                     indexOfContainsInList(firstPageText, "Customer name"):indexOfContainsInList(firstPageText, "#")]
        return {
            "billto_name": billToInfo[0].split(":")[-1].strip(),
            "billto_address": ", ".join(
                billToInfo[indexOfContainsInList(billToInfo, "Address"):indexOfContainsInList(billToInfo, "GST")]),
            "place_of_supply": "",
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        firstPageText = self.text_data[1].split("\n")
        totalTaxHeaderList = firstPageText[indexOfContainsInList(firstPageText, "summary")].split(" ")
        listOfTotalTax = firstPageText[indexOfContainsInList(firstPageText, "summary") + 1].split(" ")
        self.totalTaxPercentage = listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "summary") + 1]

        gstTypeList = []

        indexOfHeader = indexOfContainsInList(firstPage, "#")
        total_tax = {
            "IGST": float(listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "IGST") + 1].replace(",", "")),
            "SGST": float(listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "S/UTGST") + 1].replace(",", "")),
            "CGST": float(listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "CGST") + 1].replace(",", ""))}
        if total_tax["IGST"] > 0:
            gstTypeList.append("IGST")
        if total_tax["CGST"] > 0:
            gstTypeList.append("CGST")
        if total_tax["SGST"] > 0:
            gstTypeList.append("SGST")

        gstType = "_".join(gstTypeList)

        products = []
        listOfHeader = self.tables[1][indexOfContainsInList(self.tables[1], "#")]
        indexOfSr = indexOfContainsInList(listOfHeader, "#")
        indexOfItemname = indexOfContainsInList(listOfHeader, "item name")
        indexOfHsn = indexOfContainsInList(listOfHeader, "HSN")
        indexOfQty = indexOfContainsInList(listOfHeader, "Qty")
        indexOfRate = indexOfContainsInList(listOfHeader, "Mrp")
        indexOfAmt = indexOfContainsInList(listOfHeader, "Taxable")

        for itemIndex, item in enumerate(firstPage[indexOfHeader + 1:]):
            if indexOfContainsInList(item, "total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult = {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = firstPageText[indexOfContainsInList(firstPageText, "P.O.") + 1].split(" ")[-2].strip()
            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = ""
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = self.totalTaxPercentage
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = total_tax["CGST"] + total_tax["SGST"] + total_tax["IGST"]

            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        bankInfo = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "bank") + 1:]
        return {
            "bank_name": get_list_containing(bankInfo, "bank"),
            "account_number": get_list_containing(bankInfo, "Acc").split(" ")[-1],
            "ifs_code": get_list_containing(bankInfo, "Ifsc").split(" ")[-1],
        }

    def getItemTotalInfo(self):
        lastPageText = self.text_data[len(self.tables)].split("\n")
        totalList = lastPageText[
                    indexOfContainsInList(lastPageText, "TOTAL QTY"):indexOfContainsInList(lastPageText, "terms")]
        totalTax = float(get_list_containing(totalList, "total gst t").split(" ")[-1])
        grandTotal = float(get_list_containing(totalList, "NET AMOUNT").split(" ")[-1])
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(totalTax)
        returnData["amount_charged_in_words"] = convert_amount_to_words(grandTotal)
        returnData["total_pcs"] = get_list_containing(totalList, "total qty").split(" ")[-1]
        returnData["total_amount_after_tax"] = grandTotal
        returnData["total_b4_tax"] = float(get_list_containing(totalList, "GST TAXABLE VALUE").split(" ")[-1])
        returnData["total_tax"] = totalTax
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
