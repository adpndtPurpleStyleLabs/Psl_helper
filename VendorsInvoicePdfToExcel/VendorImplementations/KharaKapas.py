import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing, find_nth_occurrence_of, substring_before_second_occurrence, substring_after_second_occurrence
from fastapi import HTTPException
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class KharaKapas:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.poInfo = ""
        self.totaltax =0
        self.totaltaxPercentage = 0
        self.count =0

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Kharakapas")][0].split("\n")
        return {
            "vendor_name": vendorInfo[2],
            "vendor_address": ", ".join(vendorInfo[4:10]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split("-")[-1].strip(),
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo =get_list_containing(firstPageText, "Date").split("\n")
        self.poInfo = invoiceInfo[indexOfContainsInList(invoiceInfo, "date")+2].split(" ")[-1]
        return {
            "invoice_number": get_list_containing(invoiceInfo, "E-In").split(" ")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "date")+2].split(" ")[-2]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Customer Name")+1:indexOfContainsInList(firstPageText, "Sr")]
        return {
            "receiver_name":" ".join(receiverInfo[0].split(" ")[:4]),
            "receiver_address": substring_after_second_occurrence(receiverInfo[0], "PSL")+ " " + receiverInfo[1] + " " + receiverInfo[2],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip().split(" ")[0]
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        billToInfo =  firstPageText[indexOfContainsInList(firstPageText, "Customer Name")+1:indexOfContainsInList(firstPageText, "Sr")]
        return {
            "billto_name": " ".join(billToInfo[0].split(" ")[:4]),
            "billto_address":  substring_after_second_occurrence(billToInfo[0], "PSL")+ " " + billToInfo[1] + " " + billToInfo[2],
            "place_of_supply": "N/A",
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip().split(" ")[0]
        }


    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        grandTotalList = firstPage[indexOfContainsInList(firstPage, "Taxable Amount")]

        gstType = ""
        if indexOfContainsInList(grandTotalList, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For KasbahClothing CGST is not implemented")

        if indexOfContainsInList(grandTotalList, "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(grandTotalList, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For KasbahClothing SGST is not implemented")

        total_tax = {
            "IGST": float(firstPage[indexOfContainsInList(firstPage, "Taxable Amount") + 1][-1].split(" ")[-1].replace(",",""))
            , "SGST": 0,
            "CGST": 0,
        }

        self.totaltax = total_tax["IGST"] + total_tax["SGST"] + total_tax["CGST"]

        totalPercentage = float(firstPage[indexOfContainsInList(firstPage, "Taxable Amount")][-1].split(" ")[-1].strip())
        self.totaltaxPercentage =totalPercentage
        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "Sr")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sr")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")

        for itemIndex, item in enumerate(firstPage[indexOfHeader+1:]):
            if indexOfContainsInList(item,"Output") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult= {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            if self.poInfo.find("OR") is not -1:
                aProductResult["or_po_no"] = self.poInfo
            else:
                aProductResult["po_no"] = self.poInfo

            aProductResult["debit_note_no"] = ""
            aProductResult["index"] =  item[indexOfSr]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = item[indexOfHsn]
            aProductResult["Qty"] = item[indexOfQty]
            aProductResult["Rate"] =item[indexOfRate].split(" ")[-1]
            aProductResult["Per"] = ""
            aProductResult["mrp"] =item[indexOfRate].split(" ")[-1]
            aProductResult["Amount"] = item[indexOfAmt].split(" ")[-1]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = totalPercentage
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)
            self.count +=1

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankDetails = lastPage[indexOfContainsInList(lastPage, "Bank")]
        bankDetails = bankDetails[0].split("\n")
        return {
            "bank_name":bankDetails[indexOfContainsInList(bankDetails, "Bank de")+1],
            "account_number":bankDetails[indexOfContainsInList(bankDetails, "A/c")].split('and')[0],
            "ifs_code":bankDetails[indexOfContainsInList(bankDetails, "A/c")].split('and')[1]
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(self.totaltax)
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Rupee")][0].split("\n")[-1]
        returnData["total_pcs"] = self.count
        returnData["total_amount_after_tax"] = get_list_containing(lastPage[indexOfContainsInList(lastPage, "Rounded Total")][0].split("\n"),"grand").split(" ")[-1]
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable Amount")+1][1].split(" ")[-1]
        returnData["total_tax"] = self.totaltax
        returnData["tax_rate"] = self.totaltaxPercentage
        returnData["total_tax_percentage"] = self.totaltaxPercentage
        return returnData