from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of, get_list_containing

import re
from fastapi import HTTPException


class IkshitaChoudhary:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = 0

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "IKSHI")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:3]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice no").split("\n")[-1],
            "invoice_date": get_list_containing(firstPageText, "Dated").split("\n")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship")][0].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ",".join(receiverInfo[2:4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:7]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]

        gstType = []
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            gstType.append("CGST")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "integrated") != -1:
            raise HTTPException(status_code=400, detail="For IkshitaChoudhary IGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            gstType.append("SGST")

        gstType = "_".join(gstType)

        taxInfoList = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in wor") - 1]
        cgstPercentage = float(taxInfoList[indexOfContainsInList(taxInfoList, "Rate")].split("\n")[-1].replace("%", ""))
        sgstPercentage = float(
            taxInfoList[find_nth_occurrence_of(taxInfoList, "Rate", 2)].split("\n")[-1].replace("%", ""))
        self.totalTaxPercentage = cgstPercentage + sgstPercentage
        cgstAmount = float(taxInfoList[indexOfContainsInList(taxInfoList, "Amount")].split("\n")[-1].strip())
        sgstAmount = float(taxInfoList[find_nth_occurrence_of(taxInfoList, "Amount", 2)].split("\n")[-1].strip())

        total_tax = {"IGST": 0, "SGST": sgstAmount,
                     "CGST": cgstAmount, }

        products = []

        for index in range(1, len(pages) + 1):
            page = pages[index]

            indexOfHeader = indexOfContainsInList(self.tables[1], "description")
            indexOfSr = indexOfContainsInList(page[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(page[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(page[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(page[indexOfHeader], "Quantity")
            indexOfRate = find_nth_occurrence_of(page[indexOfHeader], "Rate", 2)
            indexOfUnit = indexOfContainsInList(page[indexOfHeader], "per")
            indexOfAmt = indexOfContainsInList(page[indexOfHeader], "Amount")

            for itemIndex, item in enumerate(page[indexOfHeader + 1:]):
                if indexOfContainsInList(item, "continue") is not -1 or indexOfContainsInList(item, "Output") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                aProductResult = {}
                poNoInfo = get_list_containing(lastPage, "buyer").split("\n")[-1].split("(")[0]
                gstRate = self.totalTaxPercentage
                amount = float(item[indexOfAmt].replace(",", ""))
                aProductResult["debit_note_no"] = ""
                aProductResult["index"] = item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = item[indexOfRate]
                aProductResult["Per"] = item[indexOfUnit]
                aProductResult["mrp"] = item[indexOfRate]
                aProductResult["Amount"] = amount
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] = gstRate
                aProductResult["gst_type"] = gstType
                aProductResult["tax_applied"] = (amount * gstRate) / 100

                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                if poNoInfo.find("OR") is not -1:
                    aProductResult["or_po_no"] = poNoInfo
                else:
                    aProductResult["po_no"] = poNoInfo
                products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):

        return {
            "bank_name": "NA",
            "account_number": "NA",
            "ifs_code": "NA",
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = \
            lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[
            -1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = re.sub(r'[^a-zA-Z0-9.]+', '',
                                                      lastPage[indexOfContainsInList(lastPage, "Total")][-1])
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][
            indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Taxable")], "Taxable")].split("\n")[-1]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][-1].split("\n")[-1]
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
