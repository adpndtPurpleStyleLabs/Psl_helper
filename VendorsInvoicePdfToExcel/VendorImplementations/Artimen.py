from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing, split_every_second_space, convert_amount_to_words
import re
from fastapi import HTTPException

class Artimen:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = ""
        self.taxableAmount =""


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Artim")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "Arti")],
            "vendor_address": ", ".join(vendorInfo[indexOfContainsInList(vendorInfo, "Arti") :5]),
            "vendor_mob": vendorInfo[indexOfContainsInList(vendorInfo, "Tel")].split(" ")[2],
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST") ].split(": ")[-1].split(" ")[0],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "Tel")].split(" ")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = get_list_containing(firstPageText, "Invoice No").split("\n")
        return {
            "invoice_number":get_list_containing(invoiceInfo, "Invoice No").split(":")[-1].strip(),
            "invoice_date": get_list_containing(invoiceInfo, "Date").split(":")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Party")][0].split("\n")
        return {
            "receiver_name": receiverInfo[1],
            "receiver_address": receiverInfo[1:3],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Party")][0].split("\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address":  billToInfo[1:3],
            "place_of_supply": get_list_containing(get_list_containing(firstPageText, "Place of").split("\n"), "Place").split(":")[-1].strip(),
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        taxInfo = get_list_containing(lastPage, "total tax").split("\n")
        totalTaxHeaderList = split_every_second_space(taxInfo[indexOfContainsInList(taxInfo, "total tax")])
        listOfTotalTax =  taxInfo[indexOfContainsInList(taxInfo, "total tax")+1].split(" ")
        self.totalTaxPercentage = listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "tax Rate")]

        gstTypeList = []
        if indexOfContainsInList(totalTaxHeaderList, "CGST")  != -1:
            gstTypeList.append("CGST")

        if indexOfContainsInList(totalTaxHeaderList, "IGST")  != -1:
            raise HTTPException(status_code=400, detail="For Artimen IGST is not implemented")

        if indexOfContainsInList(totalTaxHeaderList, "SGST") != -1:
            gstTypeList.append("SGST")

        total_tax = { "IGST": 0,  "SGST": listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "SGST Amt")], "CGST": listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "CGST Amt")],}
        gstType = "_".join(gstTypeList)

        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "S.N")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "S.N")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
        indexOfUnit = indexOfContainsInList(firstPage[indexOfHeader], "Unit")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Price")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount(")
        indexOfCGST = indexOfContainsInList(firstPage[indexOfHeader], "CGST\nAmount")
        indexOfSGST = indexOfContainsInList(firstPage[indexOfHeader], "SGST\nAmount")

        for itemIndex, item in enumerate(firstPage[indexOfHeader+1:]):
            if indexOfContainsInList(item, "total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult= {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = get_list_containing(firstPage, "PO No").split(" ")[2].strip()
            if orPoInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = orPoInfo
            else:
                aProductResult["po_no"] = orPoInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] =  item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] = item[indexOfRate]
            aProductResult["Per"] = item[indexOfUnit]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = self.totalTaxPercentage
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = float(item[indexOfCGST].replace(",", ""))+float(item[indexOfSGST].replace(",", ""))

            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        pages = self.tables
        return {
            "bank_name": "NA",
            "account_number": "NA",
            "ifs_code": "NA",
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        taxInfo = get_list_containing(lastPage, "total tax").split("\n")
        totalTaxHeaderList = split_every_second_space(taxInfo[indexOfContainsInList(taxInfo, "total tax")])
        listOfTotalTax = taxInfo[indexOfContainsInList(taxInfo, "total tax") + 1].split(" ")
        self.totalTaxPercentage = listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "tax Rate")]
        taxableAmount = listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "Taxable Amt")]
        totalTax = listOfTotalTax[indexOfContainsInList(totalTaxHeaderList, "Total Tax")]
        grandTotal = float(lastPage[indexOfContainsInList(lastPage, "party -")][-1].replace(",", ""))
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(float(totalTax.replace(",", "")))
        returnData["amount_charged_in_words"] = convert_amount_to_words(grandTotal)
        returnData["total_pcs"] = 1
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "party -")][-1].replace(",", "")
        returnData["total_b4_tax"] = float(taxableAmount.replace(",", ""))
        returnData["total_tax"] = float(totalTax.replace(",", ""))
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
