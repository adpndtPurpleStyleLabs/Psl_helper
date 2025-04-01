from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_to_ddmmyy,indexOfWordInListExactMatch
from fastapi import HTTPException

class SkbRetailPvtLtd:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "SKB")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "SKB")],
            "vendor_address": ", ".join(vendorInfo[:indexOfContainsInList(vendorInfo, "GST")]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "mail")].split(":")[-1]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice N")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(" ")[-2].split("\n")[-1],
            "invoice_date":convert_to_ddmmyy( self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Date"):][0].split(":")[-1])
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship"):]
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "PSL")],
            "receiver_address":",".join(receiverInfo[(indexOfContainsInList(receiverInfo, "PSL")+1):4]),
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1].strip()
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        billToInfo = billToInfo[indexOfContainsInList(billToInfo, "Bill") :]
        return {
            "billto_name": billToInfo[indexOfContainsInList(billToInfo, "PSL")],
            "billto_address":",".join(billToInfo[(indexOfContainsInList(billToInfo, "PSL")+1):4]),
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "State")].split(":")[-2].strip().split(",")[0],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1].strip()
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SkbRetailPvtLtd is not implemented")

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            gstType = "IGST"

        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            raise HTTPException(status_code=400, detail="For Ruhaan SkbRetailPvtLtd is not implemented")

        total_tax = {
            "IGST": float(lastPage[indexOfContainsInList(lastPage, "Taxable") + 2][-1].replace(",", "")),
            "SGST": 0,
             "CGST": 0
        }

        orPoInfo = firstPage[indexOfContainsInList(firstPage, "Buyer’s Order No.")][
            indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "Buyer’s Order No.")], "Buyer’s Order No.")].split("\n")[
            -1].strip()

        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(self.tables[1], "HSN")
            indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
            indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
            indexOfRate = indexOfWordInListExactMatch(firstPage[indexOfHeader], "Rate")
            indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

            getPercentage =  float(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 3][
                    indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 3], "%")].replace(
                    "%", ""))
            for itemIndex, item in enumerate(aPage[indexOfHeader + 1:]):
                if indexOfContainsInList(item, "Total") is not -1:
                    break
                if item[0].strip() == "":
                    continue

                aProductResult = {}
                aProductResult["po_no"] = orPoInfo
                aProductResult["index"] = item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = float(item[indexOfRate].replace(",",""))
                aProductResult["Per"] = item[indexOfPer]
                aProductResult["mrp"] =  float(item[indexOfRate].replace(",",""))
                aProductResult["Amount"] = float(item[indexOfAmt].split("\n")[0].strip().replace(",",""))
                aProductResult["po_cost"] = ""
                aProductResult["tax_applied"] = float(item[indexOfRate].replace(",","")) * (0.01) * getPercentage
                aProductResult["gst_rate"] = float(getPercentage)
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
        lastPage  =self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[-1]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Total")],"PCS")]
        returnData["total_amount_after_tax"] = float(lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1].strip().replace(",",""))
        returnData["total_b4_tax"] = float(lastPage[indexOfContainsInList(lastPage, "Taxable")+2][1].strip().replace(",",""))
        returnData["total_tax"] =float(lastPage[indexOfContainsInList(lastPage, "Taxable")+2][-1].strip().replace(",",""))
        returnData["tax_rate"] = float(lastPage[indexOfContainsInList(lastPage, "Taxable")+2][2].replace("%", "").strip().replace(",",""))
        returnData["total_tax_percentage"] =returnData["tax_rate"]
        return returnData
