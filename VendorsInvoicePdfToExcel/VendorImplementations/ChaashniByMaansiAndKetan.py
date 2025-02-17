from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing,convert_amount_to_words
from fastapi import HTTPException

class ChaashniByMaansiAndKetan:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = {}

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Antya")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "Antya")],
            "vendor_address":", ".join(vendorInfo[indexOfContainsInList(vendorInfo, "Antya"):5]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1].split(" ")[1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "email")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = get_list_containing(firstPageText, "Invoice N").split("\n")
        return {
            "invoice_number": get_list_containing(invoiceInfo, "Invoice").split(":")[-1].strip(),
            "invoice_date": get_list_containing(invoiceInfo, "Date").split(":")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo =get_list_containing(firstPageText, "Shipped to").split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "PSL")],
            "receiver_address":",".join(receiverInfo[(indexOfContainsInList(receiverInfo, "PSL") + 1):4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =get_list_containing(firstPageText, "Billed to").split("\n")
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "PSL")],
            "billto_address": ",".join(billToInfo[(indexOfContainsInList(billToInfo, "PSL") + 1):4]),
            "place_of_supply": get_list_containing(get_list_containing(firstPageText, "Place of supply").split("\n"), "Place ").split(":")[-1].strip(),
            "billto_gst" : billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        gstType = ""
        indexOfGrandTotal = lastPage[indexOfContainsInList(lastPage, "Grand Total")-1]
        total_tax = {}
        if indexOfGrandTotal != -1:
            gst_types = ["CGST", "SGST", "IGST"]

            if indexOfContainsInList(indexOfGrandTotal, "IGST") != -1:
                raise HTTPException(status_code=400, detail="For Amrti Dawani IGST is not implemented")

            indexOfCGST = indexOfContainsInList(indexOfGrandTotal[0].split("\n"), "CGST")
            indexOfSGST = indexOfContainsInList(indexOfGrandTotal[0].split("\n"), "SGST")

            listOfTaxs =  indexOfGrandTotal[1].split("\n")
            total_tax = {
                "IGST": 0,
                "SGST": listOfTaxs[indexOfSGST+1],
                "CGST": listOfTaxs[indexOfCGST+1],
            }
            self.totalTaxPercentage = {
                "IGST": 0,
                "SGST": float(indexOfGrandTotal[0].split("\n")[indexOfSGST].split("@")[-1].replace("%", "").strip()),
                "CGST": float(indexOfGrandTotal[0].split("\n")[indexOfCGST].split("@")[-1].replace("%", "").strip()),
            }
            detected_gst = [gst for gst in gst_types if indexOfContainsInList(indexOfGrandTotal, gst) != -1]
            gstType = "_".join(detected_gst)

        totaltaxPercentage = self.totalTaxPercentage["IGST"] + self.totalTaxPercentage["CGST"] + \
                             self.totalTaxPercentage["SGST"]

        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(self.tables[1], "HSN")
            indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "S.N")
            indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
            indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "Unit")
            indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Price")
            indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

            count =0
            listOfItems = aPage[indexOfHeader + 1 : indexOfHeader + 1 + indexOfContainsInList(aPage[indexOfHeader + 1:], "Total")+1]
            for itemIndex, item in enumerate(listOfItems):
                count +=1
                if indexOfContainsInList(item, "Total") is not -1 or  indexOfContainsInList(item, "add") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                orPoInfo =item[indexOfItemname].split("\n")[-1].split(" ")[0].strip()
                aProductResult = {}
                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                if orPoInfo.find("OR") is not -1:
                    aProductResult["or_po_no"] = orPoInfo
                else:
                    aProductResult["po_no"] = orPoInfo

                aProductResult["debit_note_no"] = ""
                aProductResult["index"] = item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = item[indexOfRate]
                aProductResult["Per"] = item[indexOfPer].split("\n")[0]
                aProductResult["mrp"] = item[indexOfRate].split("\n")[0]
                aProductResult["Amount"] = item[indexOfAmt].split("\n")[0]
                aProductResult["po_cost"] = ""
                aProductResult["gst_rate"] = totaltaxPercentage
                aProductResult["gst_type"] = gstType
                products.append(aProductResult)

        return products, total_tax

    def getVendorBankInfo(self):
        pages = self.tables
        lastPage = pages[len(pages)]
        bankInfo = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
        return {
            "bank_name": get_list_containing(bankInfo[indexOfContainsInList(bankInfo, "Bank Details")].split("|"), "detail").split(":")[-1].strip(),
            "account_number": get_list_containing(bankInfo[indexOfContainsInList(bankInfo, "Bank Details")].split("|"), "Account").split(":")[-1].strip(),
            "ifs_code": bankInfo[indexOfContainsInList(bankInfo, "ifsc")],
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        totaltaxPercentage = self.totalTaxPercentage["IGST"] + self.totalTaxPercentage["CGST"] + \
                             self.totalTaxPercentage["SGST"]
        totalsList = lastPage[indexOfContainsInList(lastPage, "total tax")][0].split("\n")
        returnData["tax_amount_in_words"] = convert_amount_to_words(float(totalsList[2].split(" ")[-1].replace(',',"")))
        returnData["amount_charged_in_words"] =convert_amount_to_words(float(get_list_containing(totalsList, "grand").split(" ")[-1].replace(",","")))
        returnData["total_pcs"] = get_list_containing(totalsList, "grand").split(" ")[-3]
        returnData["total_amount_after_tax"] =get_list_containing(totalsList, "grand").split(" ")[-1]
        returnData["total_b4_tax"] =totalsList[2].split(" ")[2]
        returnData["total_tax"] =totalsList[2].split(" ")[-1]
        returnData["tax_rate"] = totaltaxPercentage
        returnData["total_tax_percentage"] = totaltaxPercentage
        return returnData
