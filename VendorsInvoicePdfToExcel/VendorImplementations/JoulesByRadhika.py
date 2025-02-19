from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of, get_list_containing, \
    convert_amount_to_words

import re
from fastapi import HTTPException


class JoulesByRadhika:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = 0
        self.taxableValue=0
        self.totaltax=0


    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "vendor_name": firstPageText[indexOfContainsInList(firstPageText, "Jew")],
            "vendor_address": firstPageText[indexOfContainsInList(firstPageText, "Jew")+1:3],
            "vendor_mob": firstPageText[indexOfContainsInList(firstPageText, "Tel No")].split(":")[-1].strip(),
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "GSTIN")].split(":")[-1].strip(),
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "invoice No")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice No")].split(":")[-1].strip(),
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split(":")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        shippingInfo = firstPageText[indexOfContainsInList(firstPageText, "PSL")][1].split("\n")
        return {
            "receiver_name": shippingInfo[0][:shippingInfo[0].find("Base")],
            "receiver_address": ", ".join(shippingInfo[0:3]),
            "receiver_gst": "N/A"
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =  firstPageText[indexOfContainsInList(firstPageText, "PSL")][0].split("\n")
        return {
            "billto_name": billToInfo[0],
            "billto_address": ", ".join(billToInfo[2:8]),
            "place_of_supply": get_list_containing(firstPageText, "Destination").split(":")[-1].strip(),
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        pages = pages[1]

        listOfTotalTax = pages[indexOfContainsInList(pages, "A/C NO")+2:]
        totalTaxHeaderList = listOfTotalTax[indexOfContainsInList(listOfTotalTax, "HSN")]
        totaltaxList = listOfTotalTax[indexOfContainsInList(listOfTotalTax, "HSN")+1]

        self.taxableValue =float(totaltaxList[indexOfContainsInList(totalTaxHeaderList, "Taxable")].replace(",", "").split("\n")[0])

        sgstamount = float(totaltaxList[indexOfContainsInList(totalTaxHeaderList, "SGST")].replace(",", ""))
        cgsteAmount = float(totaltaxList[indexOfContainsInList(totalTaxHeaderList, "CGST")].replace(",", ""))
        igsteAmount = float(totaltaxList[indexOfContainsInList(totalTaxHeaderList, "IGST")].replace(",", ""))

        total_tax = {"IGST": igsteAmount, "SGST": sgstamount, "CGST": cgsteAmount}
        gstType = "_".join([atype for atype in total_tax if total_tax[atype] > 0])

        self.totalTaxPercentage = float(totaltaxList[0][totaltaxList[0].find(">")+1:].replace("%", "").strip())
        self.totaltax =float(totaltaxList[indexOfContainsInList(totalTaxHeaderList, "total tax am")].replace(",", ""))
        products = []

        indexOfHeader = indexOfContainsInList(self.tables[1], "SKU")
        indexOfSr = indexOfContainsInList(pages[indexOfHeader], "S\n")
        indexOfHsn = indexOfContainsInList(pages[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(pages[indexOfHeader], "Qty")
        indexOfRate = indexOfContainsInList(pages[indexOfHeader], "Rate")
        indexOfUnit = indexOfContainsInList(pages[indexOfHeader], "per")
        indexOfAmt = indexOfContainsInList(pages[indexOfHeader], "Amount")

        for itemIndex, item in enumerate(pages[indexOfHeader + 1:]):
            if indexOfContainsInList(item, "Amount char") is not -1 or indexOfContainsInList(item, "total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult = {}
            poNoInfo = item[indexOfContainsInList(pages[indexOfHeader], "PO.")].split(" ")[-1]
            gstRate = self.totalTaxPercentage
            amount = float(item[indexOfAmt].replace(",", ""))
            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn].split("\n")[0]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = ""
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
        page =  self.tables[1]
        bankInfo = page[indexOfContainsInList(page, "Bank Name")]
        return {
            "bank_name": bankInfo[0].split("|")[0].split(":")[-1],
            "account_number": page[indexOfContainsInList(page, "A/C No")][0].split("|")[0].split(":")[-1],
            "ifs_code": page[indexOfContainsInList(page, "branch")][0].split("|")[-1].split(":")[-1]
        }

    def getItemTotalInfo(self):
        lastPage =self.tables[1]
        returnData = {}
        grandTotal = float(lastPage[indexOfContainsInList(lastPage, "TOTAL")][-1].replace(",", "").strip())
        returnData["tax_amount_in_words"] = convert_amount_to_words(self.totaltax)
        returnData["amount_charged_in_words"] =lastPage[indexOfContainsInList(lastPage, "Amount Chargable In (Words)")][0].split("-")[-1]
        returnData["total_amount_after_tax"] =grandTotal
        returnData["total_b4_tax"] = self.taxableValue
        returnData["total_tax"] =self.totaltax
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
