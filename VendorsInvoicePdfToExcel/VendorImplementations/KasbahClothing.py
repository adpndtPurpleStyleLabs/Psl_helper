import re

from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from fastapi import HTTPException
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class KasbahClothing:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "NISHCHAI")][0].split("\n")
        return {
            "vendor_name": vendorInfo[2],
            "vendor_address":vendorInfo[3],
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(" ")[2],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Dated")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice")].split("\n")[
                indexOfContainsInList(invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice")].split("\n"),
                                      "Invoice")].split(":")[-1],
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[
                indexOfContainsInList(invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n"),
                                      "Date")].split(":")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Shipped to")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Shipped to")], "Ship")]
        return {
            "receiver_name": receiverInfo.split("\n")[1],
            "receiver_address": receiverInfo.split("\n")[2],
            "receiver_gst": receiverInfo.split("\n")[indexOfContainsInList(receiverInfo.split("\n"), "GST")].split(":")[-1]
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Billed to")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Billed to")], "Billed")]
        placeOfSupplyList = firstPageText[indexOfContainsInList(firstPageText, "Place")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Place")], "Place")].split("\n")

        return {
            "billto_name": billToInfo.split("\n")[1],
            "billto_address": ", ".join(billToInfo.split("\n")[2:4]),
            "place_of_supply": placeOfSupplyList[indexOfContainsInList(placeOfSupplyList, "Place")].split(":")[-1],
            "billto_gst": billToInfo.split("\n")[indexOfContainsInList(billToInfo.split("\n"), "GST")].split(":")[-1]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        grandTotalList = firstPage[indexOfContainsInList(firstPage, "Grand Tota")]
        total_tax = { "IGST": grandTotalList[indexOfContainsInList(grandTotalList, "IGST")].split("\n")[indexOfContainsInList(grandTotalList[indexOfContainsInList(grandTotalList, "IGST")].split("\n"), "IGST")+1].split(" ")[1]
        ,  "SGST": 0, "CGST": 0,}

        gstType = ""
        if indexOfContainsInList(grandTotalList, "CGST") != -1:
            raise HTTPException(status_code=400, detail="For KasbahClothing CGST is not implemented")

        if indexOfContainsInList(grandTotalList, "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(grandTotalList, "SGST") != -1:
            raise HTTPException(status_code=400, detail="For KasbahClothing SGST is not implemented")

        products = []
        indexOfHeader = indexOfContainsInList(self.tables[1], "S.N.")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "S.N.")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
        indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "Unit")
        indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Price")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")
        indexOfGstRate = indexOfContainsInList(firstPage[indexOfHeader], "GST\nRate")
        indexOfGstAmount = indexOfContainsInList(firstPage[indexOfHeader], "GST\nAmount")

        for itemIndex, item in enumerate(firstPage[indexOfHeader+1:]):
            if indexOfContainsInList(item,"Total") is not -1:
                break
            if item[0].strip() == "":
                continue

            aProductResult= {}
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            orPoInfo = firstPage[indexOfContainsInList(firstPage, "PO NO")][indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "PO NO")], "PO NO")].split("\n")[-2].split(":")[-1]
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
            aProductResult["Per"] = item[indexOfPer]
            aProductResult["mrp"] = item[indexOfRate]
            aProductResult["Amount"] = item[indexOfAmt].split("\n")[0]
            aProductResult["po_cost"] = ""
            aProductResult["gst_rate"] = item[indexOfGstRate]
            aProductResult["gst_type"] = gstType
            products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankDetails = lastPage[indexOfContainsInList(lastPage, "Bank")]
        return {
            "bank_name": bankDetails[0].split("\n")[0][bankDetails[0].split("\n")[0].find("Details"):bankDetails[0].split("\n")[0].find("A/C")],
            "account_number": bankDetails[0].split("\n")[0][bankDetails[0].split("\n")[0].find("A/C"):],
            "ifs_code": bankDetails[0].split("\n")[indexOfContainsInList(bankDetails[0].split("\n"), "IFSC")],
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(lastPage[indexOfContainsInList(lastPage, "Total Tax")][0].split("\n")[-2].split(" ")[-1].replace(",", ""))
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Rupee")][0].split("\n")[-1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Grand T")][0].split(" ")[indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Grand T")][0].split(" "), "Pcs")-1 ] + " Pcs"
        returnData["total_amount_after_tax"] = re.sub(r'[^a-zA-Z0-9.]+', '',
                                                      lastPage[indexOfContainsInList(lastPage, "Total")][-1])
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Total Tax")][0].split("\n")[-2].split(" ")[2]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Total Tax")][0].split("\n")[-2].split(" ")[-1]
        returnData["tax_rate"] = lastPage[indexOfContainsInList(lastPage, "Total Tax")][0].split("\n")[-2].split(" ")[1]
        returnData["total_tax_percentage"] = returnData["tax_rate"]
        return returnData