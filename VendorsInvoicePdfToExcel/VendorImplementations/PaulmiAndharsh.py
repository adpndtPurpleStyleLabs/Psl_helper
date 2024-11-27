from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class PaulmiAndHarsh:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.total_tax_percentage = ""
        self.total_b4_tax = ""
        self.tax_rate = ""
        self.total_tax = ""
        self.total_amount_after_tax = ""
        self.bankDetails = []
        self.total_pcs = ""

    def getVendorInfo(self):
        firstPageText = self.tables[1]
        vendorInfo =firstPageText[indexOfContainsInList(firstPageText, "Paulm")][0].split("\n")
        return {
            "vendor_name": vendorInfo[indexOfContainsInList(vendorInfo, "Paul")],
            "vendor_address": vendorInfo[indexOfContainsInList(vendorInfo, "Paul")+1] + " "+ vendorInfo[indexOfContainsInList(vendorInfo, "Paul") + 2][: vendorInfo[indexOfContainsInList(vendorInfo, "Paul")+2].find("acc")],
            "vendor_mob": vendorInfo[indexOfContainsInList(vendorInfo, "Mob")],
            "vendor_gst": vendorInfo[indexOfContainsInList(vendorInfo, "GST")+1].split(" ")[0],
            "vendor_email": vendorInfo[indexOfContainsInList(vendorInfo, "acc")][vendorInfo[indexOfContainsInList(vendorInfo, "acc")].find("acc"):].split(" ")[0]
        }

    def getInvoiceInfo(self):
        firstPageText = self.tables[1]
        invoiceInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice No")][1].split("\n")
        return {
            "invoice_number": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice N")].split(":")[-1].strip(),
            "invoice_date": invoiceInfo[indexOfContainsInList(invoiceInfo, "Invoice Date")].split(":")[-1].strip()
        }

    def getReceiverInfo(self):
        firstPageText = self.tables[1]
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Ship To")][0].split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+1],
            "receiver_address": receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+2] + " "+ receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+3] + " "+receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+4] + " "+ receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+5] + " "+ receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+6],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "Ship To"):][indexOfContainsInList(receiverInfo[indexOfContainsInList(receiverInfo, "Ship To")+6], "GST")].split(":")[-1]
        }

    def getBillingInfo(self):
        firstPageText = self.tables[1]
        billToInfo = firstPageText[indexOfContainsInList(firstPageText, "Invoice To")][0].split("\n")
        billToInfo = billToInfo[:indexOfContainsInList(billToInfo, "Ship To")]
        return {
            "billto_name": billToInfo[1],
            "billto_address": billToInfo[2] + " " + billToInfo[3] + " " + billToInfo[4],
            "place_of_supply": billToInfo[indexOfContainsInList(billToInfo, "Place")],
            "billto_gst": billToInfo[indexOfContainsInList(billToInfo, "GST")].split(":")[-1]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]
        indexOfHeader = indexOfContainsInList(self.tables[1], "Item N")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "Sr")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Item Name")
        indexOfpo = indexOfContainsInList(firstPage[indexOfHeader], "CPO")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "Hsn No")
        indexOfMrp = indexOfContainsInList(firstPage[indexOfHeader], "MRP")
        indexOfUnit = indexOfContainsInList(firstPage[indexOfHeader], "UOM")
        indexOfQty =indexOfContainsInList(firstPage[indexOfHeader], "Pcs")
        indexOfRate =indexOfContainsInList(firstPage[indexOfHeader], "Rate")
        indexOfAmt = indexOfContainsInList(firstPage[indexOfHeader], "Amount")
        pageNoContainingTotal = -1
        for index, aPage in enumerate(pages.values()):
            if indexOfContainsInList(self.tables[index+1], "Total") != -1:
                pageNoContainingTotal = index+1
                break

        products = []
        totalTaxInfoList = pages[pageNoContainingTotal][indexOfContainsInList(pages[pageNoContainingTotal], "Taxable ")][-1].split("\n")
        self.total_b4_tax = totalTaxInfoList[indexOfContainsInList(totalTaxInfoList, "Taxable V")].split(" ")[-1]
        self.total_tax = totalTaxInfoList[indexOfContainsInList(totalTaxInfoList, "IGST")].split(" ")[-1]
        self.total_tax_percentage = totalTaxInfoList[indexOfContainsInList(totalTaxInfoList, "IGST")].split(" ")[-2]
        self.total_amount_after_tax = totalTaxInfoList[indexOfContainsInList(totalTaxInfoList, "Net A")].split(" ")[-1]
        self.bankDetails = pages[pageNoContainingTotal][indexOfContainsInList(pages[pageNoContainingTotal], "Taxable ")][0].split("\n")
        self.total_pcs = pages[pageNoContainingTotal][indexOfContainsInList(pages[pageNoContainingTotal], "Total")][4]
        for i in range(1,pageNoContainingTotal+1):
            if i == 1:
                startIndex = indexOfHeader+1
                endIndex = len(pages[i])
            else:
                startIndex = 0
                endIndex = indexOfContainsInList(pages[i], "Total")

            for j in range(startIndex, endIndex):
                if len(pages[i][j]) >4 and pages[i][j][indexOfItemname].strip() != '' :
                    aProductResult = {}
                    aProductResult["index"] = pages[i][j][indexOfSr]
                    aProductResult["vendor_code"] = pages[i][j][indexOfItemname]
                    aProductResult["po_no"] =pages[i][j][indexOfpo]
                    aProductResult["or_po_no"] = ""
                    aProductResult["debit_note_no"] = ""
                    aProductResult["HSN/SAC"] =pages[i][j][indexOfHsn]
                    aProductResult["Qty"] = pages[i][j][indexOfQty]
                    aProductResult["Rate"] = pages[i][j][indexOfRate]
                    aProductResult["Per"] = pages[i][j][indexOfUnit]
                    aProductResult["mrp"] = pages[i][j][indexOfMrp]
                    aProductResult["Amount"] = pages[i][j][indexOfAmt]
                    aProductResult["po_cost"] = (float(pages[i][j][indexOfAmt].strip()) * float(self.total_tax_percentage.replace("%", ""))/100) +float(pages[i][j][indexOfAmt].strip())
                    aProductResult["gst_type"] = "IGST"
                    aProductResult["gst_rate"] = self.total_tax_percentage
                    aProductResult["tax_applied"] = float(pages[i][j][indexOfAmt].strip()) * float(self.total_tax_percentage.replace("%", ""))/100
                    products.append(aProductResult)

        total_tax = {
            "IGST": self.total_tax,
            "SGST": 0,
            "CGST": 0,
        }
        return products, total_tax

    def getItemTotalInfo(self):
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(float(self.total_tax.strip().replace(",", "")))
        returnData["amount_charged_in_words"] = " ".join(self.bankDetails[indexOfContainsInList( self.bankDetails, "Rs.") : indexOfContainsInList( self.bankDetails, "only")])
        returnData["total_pcs"] = self.total_pcs
        returnData["total_amount_after_tax"] =  self.total_amount_after_tax
        returnData["total_b4_tax"] =  self.total_b4_tax
        returnData["total_tax"] =  self.total_tax
        returnData["tax_rate"] =  self.total_tax_percentage
        returnData["total_tax_percentage"] = self.total_tax_percentage
        return returnData

    def getVendorBankInfo(self):
        return {
            "bank_name":self.bankDetails[indexOfContainsInList(self.bankDetails, "Bank N")],
            "account_number": self.bankDetails[indexOfContainsInList(self.bankDetails, "A/C")],
            "ifs_code": self.bankDetails[indexOfContainsInList(self.bankDetails, "IFSC")],
        }