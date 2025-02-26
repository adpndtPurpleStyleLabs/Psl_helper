import re
from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, find_nth_occurrence_of
from fastapi import HTTPException

class SaakshaAndKinni:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula


    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo = firstPageText[indexOfContainsInList(firstPageText, "SAAK")][0].split("\n")
        return {
            "vendor_name": ", ".join(vendorInfo[0]),
            "vendor_address": ", ".join(vendorInfo[:5]),
            "vendor_mob": "N/A",
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")].split(":")[-1],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "Email")].split(":")[-1]
        }


    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Dated")]
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split("\n")[-1].strip(),
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Date")].split("\n")[-1].strip()
        }


    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship to")][0].split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "Ship to")+1],
            "receiver_address": receiverInfo[1:5],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].split(":")[-1]
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")
        return {
            "billto_name": firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")[1],
            "billto_address": ", ".join(firstPageText[indexOfContainsInList(firstPageText, "Bill to")][0].split("\n")[1:5]),
            "place_of_supply": firstPageText[indexOfContainsInList(firstPageText, "Destina")][indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "Destina")], "Destina")].split("\n")[-1],
            "billto_gst":billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        lastPage = pages[len(pages)]
        total_tax = { "IGST": 0,  "SGST": 0, "CGST": 0,}

        gstType = ""
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "CGST") != -1:
            total_tax["CGST"] =  lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 2][1].split("\n")[-1]
            gstType += "_CGST"
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "IGST") != -1:
            raise HTTPException(status_code=400, detail="For Saaksha IGST is not implemented")
        if indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 1], "SGST") != -1:
            total_tax["SGST"] =  lastPage[indexOfContainsInList(lastPage, "Amount Charg") + 2][3].split("\n")[-1]
            gstType += "_SGST"

        poNo = firstPage[indexOfContainsInList(firstPage, "Buyer's")][indexOfContainsInList(firstPage[indexOfContainsInList(firstPage, "Buyer's")], "Buyer's")].split("\n")[-1]
        isPoNo = False

        if (poNo.find("Buyer") == -1):
            isPoNo = True

        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(self.tables[1], "HSN/")
            indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sl")
            indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
            indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
            indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Quantity")
            indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "per")
            indexOfRate = indexOfContainsInList(firstPage[indexOfHeader], "Rate")
            indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")

            count = 1
            for itemIndex, item in enumerate(aPage[indexOfHeader+1:]):
                if item[0].strip() == "":
                    continue
                if item[0].find('continue') is not -1 or item[0].find('Amount Chargeable') is not -1:
                    break

                aProductResult= {}
                aProductResult["po_no"] = ""
                aProductResult["or_po_no"] = ""
                aProductResult["debit_note_no"] = ""
                if isPoNo:
                    aProductResult["po_no"] = poNo
                else:
                    aProductResult["or_po_no"] = aPage[indexOfHeader+1:][find_nth_occurrence_of(aPage[indexOfHeader+1:], "PO NO", count)][indexOfItemname].split(":")[-1]

                gstPercentage = float(item[indexOfItemname].split("_")[-1].replace("%", ""))
                aProductResult["index"] =  item[indexOfSr]
                aProductResult["vendor_code"] = ""
                aProductResult["HSN/SAC"] = item[indexOfHsn]
                aProductResult["Qty"] = item[indexOfQty]
                aProductResult["Rate"] = item[indexOfRate]
                aProductResult["Per"] = item[indexOfPer]
                aProductResult["mrp"] = item[indexOfRate]
                aProductResult["Amount"] = item[indexOfAmt]
                aProductResult["po_cost"] = ""
                aProductResult["tax_applied"] = float(item[indexOfAmt].replace(",","")) * gstPercentage * 0.01
                aProductResult["gst_rate"] = gstPercentage
                aProductResult["gst_type"] = gstType.strip('_') if gstType.startswith('_') or gstType.endswith('_') else gstType
                products.append(aProductResult)
                count+=1


        return products, total_tax

    def getVendorBankInfo(self):
        lastPage  =self.tables[len(self.tables)]
        bankInfoList = lastPage[indexOfContainsInList(lastPage, "Bank")][0].split("\n")
        return {
            "bank_name": bankInfoList[indexOfContainsInList(bankInfoList, "Name")].split(":")[-1],
            "account_number": bankInfoList[indexOfContainsInList(bankInfoList, "A/c")].split(":")[-1],
            "ifs_code": bankInfoList[indexOfContainsInList(bankInfoList, "IFS")].split(":")[-1],
        }


    def getItemTotalInfo(self):
        lastPage  =self.tables[len(self.tables)]
        returnData = {}
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (")][0].split(":")[1].split("\n")[0]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Cha" )][0].split("\n")[-1]
        returnData["total_pcs"] = "1"
        returnData["total_amount_after_tax"] = str(re.sub(r'[^a-zA-Z0-9.]+', '', lastPage[indexOfContainsInList(lastPage, "Amount Cha")-1][-1]) )
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "Taxable")][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Taxable")], "Taxable")].split("\n")[-1]
        returnData["total_tax"] =lastPage[indexOfContainsInList(lastPage, "Tax Amount")][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Tax Amount")], "Tax Amount")].split("\n")[-1]
        returnData["tax_rate"] = 0
        for aList in lastPage[indexOfContainsInList(lastPage, "Taxable")+1]:
            if aList.find('Rate') is not -1:
                returnData["tax_rate"] += float(re.sub(r'\D', '', (aList.split("\n")[-1])))

        returnData["total_tax_percentage"] =returnData["tax_rate"]
        return returnData