import re
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words
from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from VendorsInvoicePdfToExcel.helper import find_nth_occurrence_of
from fastapi import HTTPException

class Amyra:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula

    def getVendorInfo(self):
        firstPageText = self.text_data[1]
        vendorInfo = firstPageText.split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[0:5]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(" ")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1]
        invoiceInfo = firstPageText.split("\n")
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice#")].split(" ")[-1],
            "invoice_date": " ".join(invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice Date")].split(" ")[-3:])
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1]
        receiverInfo = firstPageText.split("\n")

        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "Bill") + 1][
                             :receiverInfo[indexOfContainsInList(receiverInfo, "Bill") + 1].find("Date")],
            "receiver_address": receiverInfo[indexOfContainsInList(receiverInfo, "Bill") + 2][
                                :receiverInfo[indexOfContainsInList(receiverInfo, "Bill") + 2].find("Due")] + " " +
                                receiverInfo[indexOfContainsInList(receiverInfo, "Bill") + 3],
            "receiver_gst": receiverInfo[find_nth_occurrence_of(receiverInfo, "GST", 2)]
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1]
        billToInfo = firstPageText.split("\n")
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "Bill") + 1][
                             :billToInfo[indexOfContainsInList(billToInfo, "Bill") + 1].find("Date")],
            "billto_address": billToInfo[indexOfContainsInList(billToInfo, "Bill") + 2][
                                :billToInfo[indexOfContainsInList(billToInfo, "Bill") + 2].find("Due")] + " " +
                                billToInfo[indexOfContainsInList(billToInfo, "Bill") + 3],
            "place_of_supply":billToInfo[indexOfContainsInList(billToInfo, "Place")].split(":")[-1],
            "billto_gst":billToInfo[find_nth_occurrence_of(billToInfo, "GST", 2)]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        indexOfHeader = indexOfContainsInList(self.tables[1], "Description")

        gstType = ""
        if indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "Sub")][0].split("\n"), "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "Sub")][0].split("\n"), "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "Sub")][0].split("\n"), "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        total_tax = {"IGST": firstPage[indexOfContainsInList(firstPage, "Sub")][0].split("\n")[-1].split(" ")[-1]
            , "SGST": 0,
                     "CGST": 0, }

        orPoInfo = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "P.O")].split(" ")[-1]


        products = []
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Item")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")
        count = 1
        for itemIndex, item in enumerate(firstPage[indexOfHeader + 1:]):
            if indexOfContainsInList(item, "Total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult = {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""

            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = count
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = item[indexOfQty]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt ]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = item[find_nth_occurrence_of(item, "%",2)].split("\n")[-1].replace("%", "")
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)
            count+=1

        return products, total_tax

    def getVendorBankInfo(self):
        firstPageText = self.text_data[1]
        bankinfo = firstPageText.split("\n")
        return {
            "bank_name": bankinfo[indexOfContainsInList(bankinfo, "BANK")],
            "account_number": bankinfo[indexOfContainsInList(bankinfo, "Account No")].split(" ")[-1],
            "ifs_code": bankinfo[indexOfContainsInList(bankinfo, "IFSC")].split(" ")[-1],
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        totalTax = lastPage[indexOfContainsInList(lastPage, "Sub Total")][0].split("\n")[-1].split(" ")[-1]
        totalAmount = lastPage[indexOfContainsInList(lastPage, "Sub Total")][0].split("\n")[0].split(" ")[-1].replace(
            ",", "")
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(totalTax)
        returnData["amount_charged_in_words"] = convert_amount_to_words(totalAmount)
        returnData["total_pcs"] = ""
        returnData["total_amount_after_tax"] = totalAmount
        returnData["total_b4_tax"] = float(totalAmount) - float(totalTax)
        returnData["total_tax"] = totalTax
        returnData["tax_rate"] = re.sub(r'[^a-zA-Z0-9.]+', "",
                                        lastPage[indexOfContainsInList(lastPage, "Sub Total")][0].split("\n")[-1].split(
                                            " ")[1])
        returnData["total_tax_percentage"] = re.sub(r'[^a-zA-Z0-9.]+', "",
                                                    lastPage[indexOfContainsInList(lastPage, "Sub Total")][0].split(
                                                        "\n")[-1].split(" ")[1])
        return returnData
