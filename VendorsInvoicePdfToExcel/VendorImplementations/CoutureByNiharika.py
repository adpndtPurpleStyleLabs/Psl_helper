import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_amount_to_words, find_nth_occurrence_of
from fastapi import HTTPException

class CoutureByNiharika:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.gstPercentage = ""


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "COUTU")][0].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:4]),
            "vendor_mob": "N/A",
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "Biller Gst")][0].split("\n")[indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Biller Gst")][0].split("\n"), "Biller")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice No")]
        return {
            "invoice_number":invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(" ")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[indexOfContainsInList(invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n"), "Date")].replace("Invoice Date", "").strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        detailsHeader = firstPageText[indexOfContainsInList(firstPageText, "Buyer")]
        indexOfShipper = firstPageText[indexOfContainsInList(firstPageText, "Buyer") + 1]
        receiverInfo = indexOfShipper[indexOfContainsInList(detailsHeader, "Buyer") + 1].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": ", ".join(receiverInfo),
            "receiver_gst": firstPageText[indexOfContainsInList(firstPageText, "Buyer GSTIN")][
                indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Buyer GSTIN")],
                                      "Buyer GSTIN")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        detailsHeader = firstPageText[indexOfContainsInList(firstPageText, "Shipping Details")]
        indexOfShipper = indexOfContainsInList(detailsHeader, "Shipping Details")
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Shipping Details") + 1][indexOfShipper].split(
            "\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": ", ".join(billToInfo),
            "place_of_supply": firstPageText[indexOfContainsInList(firstPageText, "Place of")][
                indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Place of")],
                                      "Place of")].split(":")[-1].strip(),
            "billto_gst": firstPageText[indexOfContainsInList(firstPageText, "Buyer GSTIN")][
                indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Buyer GSTIN")],
                                      "Buyer GSTIN")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPageText = self.tables[1]
        lastPage = pages[len(pages)]

        gstInfoSection = self.table_by_tabula[len(pages)][
            find_nth_occurrence_of(self.table_by_tabula[len(pages)], "Total gst",2)].split("\n")
        getInfoHeader = gstInfoSection[indexOfContainsInList(gstInfoSection, "GST")].split("$")
        gstValues = gstInfoSection[indexOfContainsInList(gstInfoSection, "GST") + 1].split("$")

        gstType = ""
        if indexOfContainsInList(getInfoHeader, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan CGST is not implemented")

        if indexOfContainsInList(getInfoHeader, "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(getInfoHeader, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SGST is not implemented")

        total_tax = {"IGST": gstValues[indexOfContainsInList(getInfoHeader, "IGST") + 1], "SGST": 0, "CGST": 0, }
        self.gstPercentage = gstValues[indexOfContainsInList(getInfoHeader, "IGST %") ]

        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "description")
        indexOfSr = indexOfContainsInList(firstPageText[indexOfHeader], "S.No")
        indexOfHsn = indexOfContainsInList(firstPageText[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPageText[indexOfHeader], "Qty")
        indexOfRate = indexOfContainsInList(firstPageText[indexOfHeader], "MRP")
        indexOfAmt = indexOfContainsInList(firstPageText[indexOfHeader], "Amount")
        indexOfGstRate = indexOfContainsInList(firstPageText[indexOfHeader], "GST")
        indexOfPrice = indexOfContainsInList(firstPageText[indexOfHeader], "Price")

        poNoInfo = firstPageText[indexOfContainsInList(firstPageText, "Ref. No")][
            indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Ref. No")], "Ref. No")].split(
            "\n")[-1].split(":")[-1].split("/")[0].strip()

        for itemIndex, item in enumerate(firstPageText[indexOfHeader+1:]):
            if indexOfContainsInList(item, "Total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult= {}

            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            if poNoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = poNoInfo
            else:
                aProductResult["po_no"] = poNoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = "N/A"
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = item[indexOfGstRate]
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = float(item[indexOfPrice].replace(",","")) * (float( item[indexOfGstRate])/100)
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        return {
            "bank_name": "",
            "account_number": "",
            "ifs_code": "",
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        totalAfterTax = float(lastPage[indexOfContainsInList(lastPage, "Grand Total")][-1].strip().replace(",", ""))
        totalTax = float(lastPage[indexOfContainsInList(lastPage, "Total GST")][-1].strip().replace(",", ""))
        totalBeforeTax = float(
            lastPage[indexOfContainsInList(lastPage, "Total Taxable Value")][-1].strip().replace(",", ""))
        returnData["tax_amount_in_words"] = convert_amount_to_words(totalTax)
        returnData["amount_charged_in_words"] = convert_amount_to_words(totalAfterTax)
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total Quantity")][-1].strip().replace(",",
                                                                                                                  "")
        returnData["total_amount_after_tax"] = totalAfterTax
        returnData["total_b4_tax"] = totalBeforeTax
        returnData["total_tax"] = totalTax
        returnData["tax_rate"] = self.gstPercentage
        returnData["total_tax_percentage"] = self.gstPercentage
        return returnData
