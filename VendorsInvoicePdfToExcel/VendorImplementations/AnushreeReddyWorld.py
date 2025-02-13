from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_amount_to_words, find_nth_occurrence_of
from fastapi import HTTPException
import re

class AnushreeReddyWorld:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTax = ""
        self.gstPercentage = ""

    def getVendorInfo(self):
        firstPageText = self.text_data[1]
        firstPageText = firstPageText.split("\n")
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Anu") : indexOfContainsInList(firstPageText, "Bill")]
        return {
            "vendor_name": vendorInfo[0][: vendorInfo[0].find("LLP")+3],
            "vendor_address": ", ".join(vendorInfo[1:3]),
            "vendor_mob": "",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1]
        firstPageText = firstPageText.split("\n")
        firstPageTable = firstPageText[indexOfContainsInList(firstPageText, "Date")].split(":")
        return {
                "invoice_number": firstPageTable[indexOfContainsInList(firstPageTable, "Invoice")+1].split(" ")[0],
                "invoice_date": firstPageTable[indexOfContainsInList(firstPageTable, "Date")+1]
            }

    def getReceiverInfo(self):
        firstPageText = self.table_by_tabula[1][0].split("\r")
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill"): indexOfContainsInList(firstPageText, "GST state")]
        receiverAddress = receiverInfo[2][:receiverInfo[2].find(receiverInfo[2][:3],2)] + " " +  receiverInfo[3][:receiverInfo[3].find(receiverInfo[3][:3],2)] + " "  +receiverInfo[4][:receiverInfo[4].find(receiverInfo[4][:3],2)]
        getInfo = receiverInfo[indexOfContainsInList(receiverInfo, "GST")]
        return {
            "receiver_name":receiverInfo[indexOfContainsInList(receiverInfo, "Bill")].split(":")[-1],
            "receiver_address": receiverAddress,
            "receiver_gst": getInfo[: getInfo.find(getInfo[:3],2)].split(":")[-1].strip(),
        }

    def getBillingInfo(self):
        firstPageText = self.table_by_tabula[1][0].split("\r")
        receiverInfo = firstPageText[
                       indexOfContainsInList(firstPageText, "Bill"): indexOfContainsInList(firstPageText, "GST state")]
        receiverAddress = receiverInfo[2][:receiverInfo[2].find(receiverInfo[2][:3], 2)] + " " + receiverInfo[3][
                                                                                                 :receiverInfo[3].find(
                                                                                                     receiverInfo[3][
                                                                                                     :3], 2)] + " " + \
                          receiverInfo[4][:receiverInfo[4].find(receiverInfo[4][:3], 2)]
        getInfo = receiverInfo[indexOfContainsInList(receiverInfo, "GST")]
        return {
            "billto_name": receiverInfo[indexOfContainsInList(receiverInfo, "Bill")].split(":")[-1],
            "billto_address": receiverAddress,
            "place_of_supply": receiverInfo[10],
            "billto_gst":  getInfo[: getInfo.find(getInfo[:3],2)].split(":")[-1].strip()
        }

    def getItemInfo(self):
        firstPageText =self.text_data[1].split("\n")
        total_tax = {
            "IGST": firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-1].split(" ")[-4],
            "SGST": firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-1].split(" ")[-2],
            "CGST": firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-1].split(" ")[-3]
        }

        self.totalTax = float(total_tax["IGST"]) + float(total_tax["SGST"]) + float(total_tax["CGST"])

        IGSTPercenatge = float(firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-2].split(" ")[-8])
        SGSTPercenatge = float(firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-2].split(" ")[-6])
        CGSTPercenatge = float(firstPageText[find_nth_occurrence_of(firstPageText, "Challan",1)-2].split(" ")[-4])

        gstType = "_".join(tax for tax in ["IGST", "SGST", "CGST"] if float(total_tax[tax]) > 0)

        productInfoList = firstPageText[indexOfContainsInList(firstPageText, "Group"):indexOfContainsInList(firstPageText, "Grand")+1]

        products = []

        poNoInfo = firstPageText[indexOfContainsInList(firstPageText, "Ref.")].split(":")[2].replace("Date", "").strip().replace("PONO", "")
        aProductResult= {}

        aProductResult["po_no"] = ""
        aProductResult["or_po_no"] = ""
        if poNoInfo.find("OR") is not -1:
            aProductResult["or_po_no"] = poNoInfo
        else:
            aProductResult["po_no"] = poNoInfo

        aProductResult["debit_note_no"] = ""
        aProductResult["index"] = "1"
        aProductResult["vendor_code"] = ""
        aProductResult["HSN/SAC"] = productInfoList[indexOfContainsInList(productInfoList, "Pcs")].split(" ")[-5]
        aProductResult["Qty"] = " ".join(productInfoList[indexOfContainsInList(productInfoList, "Pcs")].split(" ")[-3:-1])
        aProductResult["Rate"] = productInfoList[indexOfContainsInList(productInfoList, "Pcs")].split(" ")[-1]
        aProductResult["Per"] = ""
        aProductResult["mrp"] = aProductResult["Rate"]
        aProductResult["Amount"] = productInfoList[indexOfContainsInList(productInfoList, "Grand")].split(" ")[-1]
        aProductResult["po_cost"] = ""
        aProductResult["gst_rate"] = IGSTPercenatge + CGSTPercenatge + SGSTPercenatge
        self.gstPercentage = aProductResult["gst_rate"]
        aProductResult["gst_type"] = gstType
        products.append(aProductResult)

        return products, total_tax



    def getVendorBankInfo(self):
        firstPageText =self.text_data[1].split("\n")
        bankDetails = firstPageText[indexOfContainsInList(firstPageText, "Bank"):]
        return {
            "bank_name": re.sub(r'(?<!^)([A-Z])', r' \1',bankDetails[indexOfContainsInList(bankDetails, "BankNa")].split(":")[indexOfContainsInList(bankDetails[indexOfContainsInList(bankDetails, "BankNa")].split(":"), "BankName")+1].split(" ")[0]),
            "account_number": bankDetails[indexOfContainsInList(bankDetails, "Account")].split(":")[indexOfContainsInList(bankDetails[indexOfContainsInList(bankDetails, "Account")].split(":"), "Account")+1].split(" ")[0],
            "ifs_code": bankDetails[indexOfContainsInList(bankDetails, "IFSC")].split(":")[indexOfContainsInList(bankDetails[indexOfContainsInList(bankDetails, "IFSC")].split(":"), "IFSC")+1].split(" ")[0],
        }

    def getItemTotalInfo(self):
        firstPageText =self.text_data[1].split("\n")
        returnData = {}

        totalAfterTax = float(
            firstPageText[indexOfContainsInList(firstPageText, "Grand")].split(" ")[-1].replace(",", ""))
        totalTax = self.totalTax
        totalBeforeTax = float(firstPageText[find_nth_occurrence_of(firstPageText, "Pcs", 2)].split(" ")[-11])
        returnData["tax_amount_in_words"] = convert_amount_to_words(totalTax)
        returnData["amount_charged_in_words"] = convert_amount_to_words(totalAfterTax)
        returnData["total_pcs"] =firstPageText[find_nth_occurrence_of(firstPageText, "Total",1)].split(" ")[-2]
        returnData["total_amount_after_tax"] = totalAfterTax
        returnData["total_b4_tax"] = totalBeforeTax
        returnData["total_tax"] = totalTax
        returnData["tax_rate"] = self.gstPercentage
        returnData["total_tax_percentage"] = self.gstPercentage
        return returnData

