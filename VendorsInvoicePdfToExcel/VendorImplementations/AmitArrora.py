from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing
from fastapi import HTTPException

class AmitArrora:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalTaxPercentage = {}

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "GOPALS")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "GOPALS")],
            "vendor_address": ", ".join(vendorInfo[:indexOfContainsInList(vendorInfo, "GST")]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        return {
            "invoice_number": get_list_containing(firstPageText, "Invoice N").split("\n")[-1],
            "invoice_date":
                self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Dated") + 1].split(
                    " ")[-1]
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship"):]
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "PSL")],
            "receiver_address": ",".join(receiverInfo[(indexOfContainsInList(receiverInfo, "PSL") + 1):4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill"):]
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "PSL")],
            "billto_address": ",".join(billToInfo[(indexOfContainsInList(billToInfo, "PSL") + 1):4]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[-2].strip().split(",")[
                0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
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
            if indexOfContainsInList(gst_section, "IGST") != -1:
                raise HTTPException(status_code=400, detail="For AmitArrora IGST is not implemented")

            indexOfCGST = indexOfContainsInList(gst_section, "CGST")
            indexOfSGST = indexOfContainsInList(gst_section, "SGST")
            total_tax = {
                "IGST": 0,
                "SGST": lastPage[amount_charg_index + 3][indexOfSGST + 2] if indexOfSGST != -1 else 0,
                "CGST": lastPage[amount_charg_index + 3][indexOfCGST + 1] if indexOfCGST != -1 else 0,
            }
            self.totalTaxPercentage = {
                "IGST": 0,
                "SGST": float(
                    lastPage[amount_charg_index + 3][indexOfSGST + 1].replace("%", "")) if indexOfSGST != -1 else 0,
                "CGST": float(
                    lastPage[amount_charg_index + 3][indexOfCGST].replace("%", "")) if indexOfCGST != -1 else 0,
            }
            detected_gst = [gst for gst in gst_types if indexOfContainsInList(gst_section, gst) != -1]
            gstType = "_".join(detected_gst)

        totaltaxPercentage = self.totalTaxPercentage["IGST"] + self.totalTaxPercentage["CGST"] + \
                             self.totalTaxPercentage["SGST"]

        orPoInfo = \
        self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Order No.") + 1].split(" ")[
            0]

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

            for itemIndex, item in enumerate(aPage[indexOfHeader + 1:]):
                if indexOfContainsInList(item, "Total") is not -1:
                    break
                if item[0].strip() == "":
                    continue

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
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable") + 2][1]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable") + 2][-1]
        returnData["tax_rate"] = totaltaxPercentage
        returnData["total_tax_percentage"] = totaltaxPercentage
        return returnData
