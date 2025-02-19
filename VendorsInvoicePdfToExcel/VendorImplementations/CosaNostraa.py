from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of, get_list_containing

import re
from fastapi import HTTPException

class CosaNostraa:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Sala")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:4]),
            "vendor_mob": vendorInfo[indexOfContainsInList(vendorInfo, "Con")].split(" ")[-1],
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice no").split("\n")[-1],
            "invoice_date": get_list_containing(firstPageText, "Dated").split("\n")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Bill"):]

        return {
            "receiver_name": receiverInfo[1],
            "receiver_address":",".join(receiverInfo[2:6]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill"):]
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo[2:6]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "supply")].split(":")[1].split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]

        total_tax = {"IGST": lastPage[indexOfContainsInList(lastPage, "Taxable") + 1][1].split("\n")[-1], "SGST": 0,
                     "CGST": 0, }

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For CosaNostraa CGST is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For CosaNostraa SGST is not implemented")

        poNoList = get_list_containing(pages[1], "Buyer's").split("\n")[-1].split(",")
        products = []

        count = -1
        for index in range(1, len(pages) + 1):
            page = pages[index]
            indexOfHeader = indexOfContainsInList(self.tables[1], "description")
            indexOfSr = indexOfContainsInList(page[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(page[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(page[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(page[indexOfHeader], "Quantity")
            indexOfRate = indexOfContainsInList(page[indexOfHeader], "Rate")
            indexOfUnit = indexOfContainsInList(page[indexOfHeader], "per")
            indexOfAmt = indexOfContainsInList(page[indexOfHeader], "Amount")

            for itemIndex, item in enumerate(page[indexOfHeader + 1:]):
                if indexOfContainsInList(item, "continue") is not -1 or indexOfContainsInList(item, "Output") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                count+=1
                aProductResult = {}

                poNoInfo =poNoList[count]

                gstRate = float(lastPage[indexOfContainsInList(lastPage, "Taxable") + 1][0].split("\n")[
                                    -1].replace("%", "").strip())

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
        lastPage = self.tables[len(self.tables)]
        bankInfo = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
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
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = re.sub(r'[^a-zA-Z0-9.]+', '',
                                                      lastPage[indexOfContainsInList(lastPage, "Total")][-1])
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][
            indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Taxable")], "Taxable")].split("\n")[-1]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][-1].split("\n")[-1]
        returnData["tax_rate"] = lastPage[indexOfContainsInList(lastPage, "Taxable") + 1][0].split("\n")[-1].replace(
            "%", "").strip()
        returnData["total_tax_percentage"] = lastPage[indexOfContainsInList(lastPage, "Taxable") + 1][0].split("\n")[
            -1].replace("%", "").strip()
        return returnData
