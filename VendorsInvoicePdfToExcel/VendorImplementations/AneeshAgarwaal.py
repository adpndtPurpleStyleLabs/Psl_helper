from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_amount_to_words, get_list_containing, \
    find_nth_occurrence_of
from fastapi import HTTPException
import re


class AneeshAgarwaal:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTax = 0
        self.totalTaxPercentage = 0

    def getVendorInfo(self):
        vendorInfo = self.tables[1][indexOfContainsInList(self.tables[1], "Anee")]
        vendorInfo = vendorInfo[indexOfContainsInList(vendorInfo, "Aneesh")].split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[1:4]),
            "vendor_mob": "",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1].strip(),
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Dated")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice")].split("\n")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = get_list_containing(firstPageText, "Ship to").split("\n")
        return {
            "receiver_name":receiverInfo[1],
            "receiver_address": ", ".join(receiverInfo[1:4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip(),
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = get_list_containing(firstPageText, "Bill to").split("\n")
        return {
            "billto_name": receiverInfo[1],
            "billto_address": ", ".join(receiverInfo[1:4]),
            "place_of_supply": receiverInfo[indexOfContainsInList(receiverInfo, "Place")].split(":")[-1].strip(),
            "billto_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def taxInfo(self):
        lastPage = self.tables[len(self.tables)]
        totalTaxHeaders = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 4]
        indexOfCGST = indexOfContainsInList(totalTaxHeaders, "CGST")
        indexOfSGST = indexOfContainsInList(totalTaxHeaders, "SGST")

        total_tax = {
            "IGST": 0,
            "SGST": float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 1][indexOfSGST + 1].replace(",", "").strip()),
            "CGST": float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 1][indexOfCGST].replace(",", "").strip())
        }

        gstType = "_".join(filter(None, [
            "CGST" if indexOfCGST != -1 else "",
            "SGST" if indexOfSGST != -1 else ""
        ]))

        gstPercentage = {
            "IGST": 0,
            "SGST": float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 2][indexOfSGST].replace("%", "").strip()),
            "CGST": float(lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 2][indexOfCGST + 1].replace("%", "").strip())
        }
        self.totalTax = total_tax["IGST"] + total_tax["SGST"] + total_tax["CGST"]
        self.totalTaxPercentage =  gstPercentage["IGST"] + gstPercentage["SGST"] + gstPercentage["CGST"]

        return total_tax, gstType, gstPercentage



    def getItemInfo(self):
        firstPageText = self.tables[1]
        total_tax, gstType, gstPercentage = self.taxInfo()
        products = []

        indexOfHeader = indexOfContainsInList(firstPageText, "Description")
        headerList = firstPageText[indexOfContainsInList(firstPageText, "Description")]
        headers = ["Sl", "Description", "HSN", "Quantity", "Rate", "Amount", "Taxable", "Total\nAmount", "CGST", "SGST", "per"]
        indexMap = {key: indexOfContainsInList(headerList, key) for key in headers}

        count = indexOfHeader + 1
        for itemIndex, item in enumerate(firstPageText[indexOfHeader + 2:]):
            count +=1
            if len(item) <2:
                break

            if item[0].strip() == "":
                continue

            aProductResult = {}
            poNoIfo = firstPageText[count+2][indexMap["Description"]]
            aProductResult["or_po_no"] = ""
            aProductResult["po_no"] = ""
            if poNoIfo.find("OR") is not -1:
                aProductResult["or_po_no"] = poNoIfo
            else:
                aProductResult["po_no"] = poNoIfo
            aProductResult["debit_note_no"] = ""
            aProductResult["index"] = item[indexMap["Sl"]]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] =  item[indexMap["HSN"]]
            aProductResult["Qty"] =item[indexMap["Quantity"]]
            aProductResult["Rate"] =item[indexMap["Taxable"]]
            aProductResult["Per"] = item[indexMap["per"]]
            aProductResult["mrp"] = item[indexMap["Taxable"]]
            aProductResult["Amount"] = item[indexMap["Total\nAmount"]+2]
            aProductResult["po_cost"] = ""
            aProductResult["tax_applied"] = float(item[indexMap["CGST"] + 1].replace(",", "")) + float(
                item[indexMap["SGST"] + 2].replace(",", ""))
            aProductResult["gst_rate"] = gstPercentage["SGST"] + gstPercentage["CGST"]
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankDetails = lastPage[indexOfContainsInList(lastPage, "Bank Detail")][0].split("\n")

        return {
            "bank_name":get_list_containing(bankDetails, "Bank Name").split(":")[-1].strip(),
            "account_number":get_list_containing(bankDetails, "A/c No").split(":")[-1].strip(),
            "ifs_code": get_list_containing(bankDetails, "IFS Code ").split(":")[-1].strip(),
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}

        totalBeforeTax = float(
            lastPage[indexOfContainsInList(lastPage, "Tax Amount (in words) : ") - 1][0].replace(",", "").strip())
        totalAfterTax = totalBeforeTax + self.totalTax
        returnData["tax_amount_in_words"] = \
        get_list_containing(lastPage, "Tax Amount (in words)").split("\n")[0].split(":")[-1].strip()
        returnData["amount_charged_in_words"] = get_list_containing(lastPage, "Amount Chargeable (in words)")[
                                                get_list_containing(lastPage, "Amount Chargeable (in words)").find(
                                                    "INR"):get_list_containing(lastPage,
                                                                               "Amount Chargeable (in words)").find(
                                                    "Only") + 4]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Amount Chargeable") - 1][3]
        returnData["total_amount_after_tax"] = totalAfterTax
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Amount Chargeable") - 1][7].split(" ")[
            -1]
        returnData["total_tax"] = self.totalTax
        returnData["tax_rate"] = self.totalTaxPercentage
        returnData["total_tax_percentage"] = self.totalTaxPercentage
        return returnData
