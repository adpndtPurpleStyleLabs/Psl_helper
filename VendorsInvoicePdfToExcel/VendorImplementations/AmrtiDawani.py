from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing
from fastapi import HTTPException

class AmrtiDawani:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = {}

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "Amrti")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "Amrti")],
            "vendor_address": ", ".join(vendorInfo[:indexOfContainsInList(vendorInfo, "GST")]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice N").split("\n")[-1],
            "invoice_date": get_list_containing(firstPageText, "Dated").split("\n")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo =get_list_containing(firstPageText, "Bill to").split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "PSL")],
            "receiver_address": ",".join(receiverInfo[(indexOfContainsInList(receiverInfo, "PSL") + 1):7]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo =get_list_containing(firstPageText, "Bill to").split("\n")
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "PSL")],
            "billto_address": ",".join(billToInfo[(indexOfContainsInList(billToInfo, "PSL") + 1):7]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[-2].strip().split(",")[
                0],
            "billto_gst" : billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        gstType = ""
        amount_charg_index = indexOfContainsInList(lastPage, "Amount Charg")
        total_tax = {}
        if amount_charg_index != -1:
            gst_section = lastPage[amount_charg_index + 1]
            gst_types = ["CGST", "SGST", "IGST"]


            if indexOfContainsInList(gst_section, "SGST") != -1 or indexOfContainsInList(gst_section, "CGST") != -1:
                raise HTTPException(status_code=400, detail="For Amrti Dawani SGST and CGST is not implemented")

            total_tax = {
                "IGST": lastPage[indexOfContainsInList(lastPage, "Tax Amount")][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Tax Amount")], "Tax Amount")].split("\n")[-1],
                "SGST": 0,
                "CGST": 0,
            }
            self.totalTaxPercentage = {
                "IGST": float(lastPage[amount_charg_index+2][indexOfContainsInList(lastPage[amount_charg_index+2], "Rate")].split("\n")[-1].strip().replace("%","")),
                "SGST": 0,
                "CGST": 0,
            }
            detected_gst = [gst for gst in gst_types if indexOfContainsInList(gst_section, gst) != -1]
            gstType = "_".join(detected_gst)

        totaltaxPercentage = self.totalTaxPercentage["IGST"] + self.totalTaxPercentage["CGST"] + \
                             self.totalTaxPercentage["SGST"]

        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(self.tables[1], "HSN")
            indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
            indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
            indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
            indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

            count =0
            listOfItems = aPage[indexOfHeader + 1 : indexOfHeader + 1 + indexOfContainsInList(aPage[indexOfHeader + 1:], "Total")+1]
            for itemIndex, item in enumerate(listOfItems):
                count +=1
                if indexOfContainsInList(item, "Total") is not -1:
                    break
                if item[0].strip() == "":
                    continue


                orPoInfo = self.getPoNo(listOfItems[count:])
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
            "bank_name": bankInfo[indexOfContainsInList(bankInfo, "Bank Name")].split(":")[-1],
            "account_number": bankInfo[indexOfContainsInList(bankInfo, "A/c No")].split(":")[-1],
            "ifs_code": bankInfo[indexOfContainsInList(bankInfo, "IFS")].split(":")[-1],
        }

    def getItemTotalInfo(self):
        lastPage = self.tables[len(self.tables)]
        returnData = {}
        totaltaxPercentage = self.totalTaxPercentage["IGST"] + self.totalTaxPercentage["CGST"] + \
                             self.totalTaxPercentage["SGST"]
        returnData["tax_amount_in_words"] = \
            lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[
            -1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] = get_list_containing(lastPage, "Taxable").split("\n")[-1]
        returnData["total_tax"] =get_list_containing(lastPage, "Tax Amount").split("\n")[-1]
        returnData["tax_rate"] = totaltaxPercentage
        returnData["total_tax_percentage"] = totaltaxPercentage
        return returnData

    def getPoNo(self, list):
        for item in list:
            indexOfPo = indexOfContainsInList(item, "PO")
            if indexOfPo != -1:
                return  get_list_containing(item, "PO").split(" ")[-1].strip()
        raise HTTPException(status_code=404, detail="PoNo not present for item")