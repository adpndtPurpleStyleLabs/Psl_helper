from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing, convert_amount_to_words

class SahilAnejaCouture:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalSumOfTax = ""
        self.totalTaxPercentage = ""
        self.totalPcs = ""

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Sahil")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Sahil")], "Sahil")].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address":", ".join(vendorInfo[:3]),
            "vendor_mob": vendorInfo[indexOfContainsInList(vendorInfo, "PH")].split(" ")[-1],
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(" ")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice N")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Invoice N")], "Invoice")]
        return {
            "invoice_number": invoiceInfo.split("\n")[indexOfContainsInList(invoiceInfo.split("\n"), "Invo")].split(":")[-1],
            "invoice_date": invoiceInfo.split("\n")[indexOfContainsInList(invoiceInfo.split("\n"), "Date")].split(":")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[
                       indexOfContainsInList(firstPageText, "Details of Receiver"):indexOfContainsInList(firstPageText,
                                                                                                         "S. No")]
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")]
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "Name")].split(":")[-1],
            "receiver_address": ", ".join(receiverInfo[1:3]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(" ")[-1]
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[
                       indexOfContainsInList(firstPageText, "Details of Receiver"):indexOfContainsInList(firstPageText,
                                                                                                         "S. No")]
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")]
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split("\n")
        return {
            "billto_name": receiverInfo[indexOfContainsInList(receiverInfo, "Name")].split(":")[-1],
            "billto_address": ", ".join(receiverInfo[1:3]),
            "place_of_supply": receiverInfo[indexOfContainsInList(receiverInfo, "state")].split(":")[-1],
            "billto_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(" ")[-1]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        total_tax = {
            "IGST": self.extract_tax_amount(lastPage, "IGST"),
            "SGST":  self.extract_tax_amount(lastPage, "SGST"),
            "CGST":  self.extract_tax_amount(lastPage, "CGST")
        }

        self.totalSumOfTax = total_tax["IGST"] + total_tax["SGST"] + total_tax["CGST"]

        CGSTPercentage = self.extract_percentage(lastPage, "CGST")
        SGSTPercentage = self.extract_percentage(lastPage, "SGST")
        IGSTPercentage = self.extract_percentage(lastPage, "IGST")

        self.totalTaxPercentage = CGSTPercentage + SGSTPercentage + IGSTPercentage

        gstType = "_".join(filter(None, [
            "CGST" if CGSTPercentage > 0 else "",
            "SGST" if SGSTPercentage > 0 else "",
            "IGST" if IGSTPercentage > 0 else "",
        ]))

        products = []
        indexOfHeader = firstPage[indexOfContainsInList(firstPage, "S. N")]
        indexOfSr = indexOfContainsInList(indexOfHeader, "S. N")
        indexOfItemname = indexOfContainsInList(indexOfHeader, "DESCRIPTION")
        indexOfHsn =indexOfContainsInList(indexOfHeader, "HSN")
        indexOfQty = indexOfContainsInList(indexOfHeader, "Qty")
        indexOfRate = indexOfContainsInList(indexOfHeader, "Rate")
        indexOfAmt = indexOfContainsInList(indexOfHeader, "Amount")

        srNoList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfSr].split("\n")
        poNoList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfItemname].split("\n")
        hsnNoList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfHsn].split("\n")
        rateList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfRate].split("\n")
        amtList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfAmt].split("\n")
        qtyList = firstPage[indexOfContainsInList(firstPage, "S. N")+1:][0][indexOfQty].split("\n")

        self.totalPcs = srNoList[-1]
        for index in srNoList:
            aProductResult= {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = poNoList[int(index.strip())-1]
            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = index
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = hsnNoList[int(index.strip())-1]
            aProductResult["Qty"] =  qtyList[int(index.strip())-1]
            aProductResult["Rate"] = rateList[int(index.strip())-1]
            aProductResult["Per"] = "N/A"
            aProductResult["mrp"] = rateList[int(index.strip())-1]
            aProductResult["Amount"] = amtList[int(index.strip())-1]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = CGSTPercentage + SGSTPercentage + IGSTPercentage
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = float(amtList[int(index.strip())-1].replace(" ","").replace(",","")) * 0.01 * aProductResult["gst_rate"]
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        return {
            "bank_name": "",
            "account_number": get_list_containing(get_list_containing(lastPage, "Account").split("\n"),  "Acc").split(":")[-1].strip(),
            "ifs_code": get_list_containing(get_list_containing(lastPage, "Account").split("\n"),  "IFSC").split(":")[-1].strip(),
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        totalInfo = lastPage[indexOfContainsInList(lastPage, "Total Invoice"):indexOfContainsInList(lastPage, "Bank")]
        returnData = {}

        totalAmountAftertax = float(lastPage[indexOfContainsInList(lastPage, "After Tax")][-1].replace(",", ""))
        totalAmountBeforeTax = float(totalInfo[indexOfContainsInList(totalInfo, "Before")][-1].replace(",", ""))
        returnData["tax_amount_in_words"] = convert_amount_to_words(self.totalSumOfTax)
        returnData["amount_charged_in_words"] = convert_amount_to_words(totalAmountAftertax)
        returnData["total_pcs"] = self.totalPcs
        returnData["total_amount_after_tax"] = totalAmountAftertax
        returnData["total_b4_tax"] = totalAmountBeforeTax
        returnData["total_tax"] = self.totalSumOfTax
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData

    def extract_percentage(self, lastPage, tax_type):
        tax_line_index = indexOfContainsInList(lastPage, f"Add: {tax_type}")
        if tax_line_index == -1:
            return 0

        tax_line = lastPage[tax_line_index]
        percentage_index = indexOfContainsInList(tax_line, "%")
        if percentage_index == -1:
            return 0

        percentage_value = tax_line[percentage_index].split(" ")[-1].replace("%", "").strip()
        return float(percentage_value) if percentage_value else 0

    def extract_tax_amount(self, lastPage, tax_type):
        tax_line_index = indexOfContainsInList(lastPage, f"Add: {tax_type}")
        if tax_line_index == -1:
            return 0

        tax_value = lastPage[tax_line_index][-1].replace(",", "").strip()
        return float(tax_value) if tax_value else 0