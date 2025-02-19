from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, substring_after_second_occurrence, \
    get_list_containing, substring_before_second_occurrence, convert_amount_to_words

import re
from fastapi import HTTPException


class Crimzon:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTax = 0
        self.totalTaxPercentage = 0
        self.totalTaxableAmount = 0

    def getVendorInfo(self):
        firstPageText = self.text_data[1]
        vendorInfo = firstPageText.split("\n")
        return {
            "vendor_name": vendorInfo[0][:vendorInfo[0].find("Sale")],
            "vendor_address": ", ".join(vendorInfo[1:4]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1]
        invoiceInfo = firstPageText.split("\n")
        return {
            "invoice_number": get_list_containing(invoiceInfo, "Invoice no").split(" ")[3].strip(),
            "invoice_date": get_list_containing(invoiceInfo, "Invoice no").split(" ")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1]
        receiverInfo = firstPageText.split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship"):]
        return {
            "receiver_name": receiverInfo[0][receiverInfo[0].find("Ship"):].split(":")[-1],
            "receiver_address": substring_after_second_occurrence(receiverInfo[1],
                                                                  "Address") + " " + substring_after_second_occurrence(
                receiverInfo[2], receiverInfo[2].split(" ")[0]) + " " + substring_after_second_occurrence(
                receiverInfo[3], receiverInfo[3].split(" ")[0]) + " " + substring_after_second_occurrence(
                receiverInfo[4], receiverInfo[4].split(" ")[0]) + " " + substring_after_second_occurrence(
                receiverInfo[5], receiverInfo[5].split(" ")[0]),
            "receiver_gst": substring_after_second_occurrence(get_list_containing(receiverInfo, "GST"), "GST")
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1]
        billToInfo = firstPageText.split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill"):]

        return {
            "billto_name": billToInfo[0][billToInfo[0].find("Bill"):].split(":")[-1],
            "billto_address": substring_before_second_occurrence(billToInfo[1],
                                                                 "Address") + " " + substring_before_second_occurrence(
                billToInfo[2], billToInfo[2].split(" ")[0]) + " " + substring_before_second_occurrence(
                billToInfo[3], billToInfo[3].split(" ")[0]) + " " + substring_before_second_occurrence(
                billToInfo[4], billToInfo[4].split(" ")[0]) + " " + substring_before_second_occurrence(
                billToInfo[5], billToInfo[5].split(" ")[0]),
            "place_of_supply": "",
            "billto_gst": substring_before_second_occurrence(get_list_containing(billToInfo, "GST"), "GST").split(":")[
                -1].strip()
        }

    def getItemInfo(self):
        pages = self.text_data
        lastPage = pages[len(pages)]
        firstPage = pages[1].split("\n")

        taxInfoList = firstPage[indexOfContainsInList(firstPage, "Amount In Words") + 1:indexOfContainsInList(firstPage,
                                                                                                              "Challan")]
        listOfTaxHeader = taxInfoList[indexOfContainsInList(taxInfoList, "HSN")].split(" ")
        listOfTaxInfo = taxInfoList[indexOfContainsInList(taxInfoList, "HSN") + 2].split(" ")
        self.totalTaxableAmount = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "Taxable") - 1])
        cgstTaxAmount = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "CGST")])
        sgstTaxAmount = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "SGST") + 1])
        igstTaxAmount = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "IGST") + 2])

        cgstTaxPercentage = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "CGST") - 1])
        sgstTaxPercentage = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "SGST")])
        igstTaxPercentage = float(listOfTaxInfo[indexOfContainsInList(listOfTaxHeader, "IGST") + 1])

        self.totalTax = cgstTaxAmount + sgstTaxAmount + igstTaxAmount
        self.totalTaxPercentage = cgstTaxPercentage + sgstTaxPercentage + igstTaxPercentage
        total_tax = {"IGST": igstTaxAmount, "SGST": sgstTaxAmount, "CGST": cgstTaxAmount}
        gstType = "_".join([atype for atype in total_tax if total_tax[atype] > 0])

        products = []

        indexOfHeader = indexOfContainsInList(firstPage, "barcode")
        listOfItemHeader = firstPage[indexOfHeader].split(" ")

        indexOfItemname = indexOfContainsInList(listOfItemHeader, "item")
        indexOfHsn = indexOfContainsInList(listOfItemHeader, "HSN") - len(listOfItemHeader)
        indexOfQty = indexOfContainsInList(listOfItemHeader, "Qty") - len(listOfItemHeader)
        indexOfRate = indexOfContainsInList(listOfItemHeader, "MRP") - len(listOfItemHeader)
        indexOfUnit = indexOfContainsInList(listOfItemHeader, "UOM") - len(listOfItemHeader)
        indexOfAmt = indexOfContainsInList(listOfItemHeader, "Amount") - len(listOfItemHeader)

        poNoList = firstPage[indexOfContainsInList(firstPage, "Doc No.")]
        poNoInfo = poNoList[poNoList.find("PO"): poNoList.find("Date")].split("-")[-1].strip()
        itemCount = 0
        for itemIndex, itemStr in enumerate(firstPage[indexOfHeader + 1:]):
            item = itemStr.split(" ")
            if len(item) < 6:
                break
            if item[0].strip() == "":
                continue

            aProductResult = {}
            gstRate = self.totalTaxPercentage

            itemCount += 1
            amount = float(item[indexOfAmt].replace(",", ""))
            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = itemCount
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
        lastPage = self.text_data[len(self.text_data)].split("\n")
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(self.totalTax)
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount In Words")].split(":")[
            -1].strip()
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")].split(" ")[-2]
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Grand")].split(" ")[-1]
        returnData["total_b4_tax"] = self.totalTaxableAmount
        returnData["total_tax"] = self.totalTax
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
