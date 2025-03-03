from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from VendorsInvoicePdfToExcel.helper import strip_array_before_specified_word
from VendorsInvoicePdfToExcel.helper import substring_before_second_occurrence
from VendorsInvoicePdfToExcel.helper import substring_after_second_occurrence
from VendorsInvoicePdfToExcel.helper import find_nth_occurrence_of
from VendorsInvoicePdfToExcel.helper import lastIndexOfContainsInList
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words
from VendorsInvoicePdfToExcel.helper import clear_or_po_no

class Masaba:

    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalmountBeforetax = ""
        self.totaltax = ""
        self.totalAfterTax = ""
        self.totalItems = ""

    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "vendor_name": firstPageText[indexOfContainsInList(firstPageText, "MASABA")].strip(),
            "vendor_address": firstPageText[indexOfContainsInList(firstPageText, "MASABA")+1].strip() + " " + firstPageText[indexOfContainsInList(firstPageText, "MASABA")+2].strip(),
            "vendor_mob": "",
            "vendor_gst":firstPageText[indexOfContainsInList(firstPageText, "GSTIN")].strip().split(":")[-1],
            "vendor_email": ""
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "invoice_number": firstPageText[indexOfContainsInList(firstPageText, "Sales Order No")].split(":")[-1] ,
            "invoice_date": firstPageText[indexOfContainsInList(firstPageText, "date")].strip().split(" ")[indexOfContainsInList(firstPageText[indexOfContainsInList(firstPageText, "date")].strip().split(" "), "date")+1]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfoArr =strip_array_before_specified_word(firstPageText,"Details of receive")
        return {
            "receiver_name": substring_after_second_occurrence(receiverInfoArr[1], "Name"),
            "receiver_address": substring_after_second_occurrence(receiverInfoArr[2], "Address").replace("Address", "") + " "
            + receiverInfoArr[find_nth_occurrence_of(receiverInfoArr, "State", 2)] + " "
            + receiverInfoArr[find_nth_occurrence_of(receiverInfoArr, "State code ", 2)],
            "receiver_gst": receiverInfoArr[find_nth_occurrence_of(receiverInfoArr, "GSTIN", 2)].split(" ")[-1],
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfoArr = strip_array_before_specified_word(firstPageText, "Details of receive")
        return {
                "billto_name": substring_before_second_occurrence(receiverInfoArr[1], "Name").replace("Name", ""),
                "billto_address": substring_before_second_occurrence(receiverInfoArr[2], "Address").replace("Address", ""),
                "billto_gst": receiverInfoArr[indexOfContainsInList(receiverInfoArr, "GST")].split(" ")[-1],
                "place_of_supply": receiverInfoArr[indexOfContainsInList(receiverInfoArr, "GST")].split(" ")[-1]
            }

    def getItemInfo(self):
        pages = self.tables
        firstPage = pages[1]
        products = []
        header = firstPage[indexOfContainsInList(firstPage, "Sr")]
        indexOfSrNo = indexOfContainsInList(header, "Sr")
        indexOfHSN = indexOfContainsInList(header, "HSN")
        indexOfQty = indexOfContainsInList(header, "Qty")
        indexOfTotal = indexOfContainsInList(header, "Total")
        indexOfTotalAfterDiscount =indexOfContainsInList(header, "Taxable\nvalue")
        indexOfTotalTaxAmount = indexOfContainsInList(header, "Tax\namount")
        indexOfRateOfTax = find_nth_occurrence_of(header, "Rate", 2)
        indexOfTaxComponent =indexOfContainsInList(header, "Tax\nco")
        totalSgst = 0
        totalCgst = 0

        for i in range(1, len(firstPage)):
            if firstPage[i][indexOfContainsInList(header, "Sr")] == "":
                continue
            aProductResult = {}

            customerRef = self.text_data[1].split("\n")[indexOfContainsInList( self.text_data[1].split("\n"), "Customer referenc")].split(":")[-1]
            aProductResult["debit_note_no"] = ""
            aProductResult["po_no"] = ""
            aProductResult["or_po_no"] = ""
            if customerRef.__contains__("OR"):
                aProductResult["or_po_no"] = clear_or_po_no(customerRef)
                print(aProductResult["or_po_no"])
            else :
                aProductResult["po_no"] = customerRef

            gstComponent = ""
            gstRate = 0
            aProductResult["index"] = firstPage[i][indexOfSrNo]
            aProductResult["vendor_code"] = ""
            aProductResult["HSN/SAC"] = firstPage[i][indexOfHSN]
            aProductResult["Qty"] = firstPage[i][indexOfQty]
            aProductResult["Rate"] = firstPage[i][indexOfTotalAfterDiscount]
            aProductResult["Per"] = "Per Item"
            aProductResult["Amount"] =  firstPage[i][indexOfTotalAfterDiscount]
            aProductResult["mrp"] =  firstPage[i][indexOfTotal]

            for gstIndex in range(i+1, i+3):
                if "CGST" in firstPage[gstIndex][indexOfTaxComponent]:
                    totalCgst = totalCgst + float(firstPage[gstIndex][indexOfTotalTaxAmount].replace(",", ""))
                    gstComponent = gstComponent + "CGST "
                    gstRate = gstRate + float(firstPage[gstIndex][indexOfRateOfTax].replace("%", ""))
                elif "SGST" in firstPage[gstIndex][indexOfTaxComponent]:
                    totalSgst = totalSgst + float(firstPage[gstIndex][indexOfTotalTaxAmount].replace(",", ""))
                    gstComponent = gstComponent + "SGST "
                    gstRate = gstRate + float(firstPage[gstIndex][indexOfRateOfTax].replace("%", ""))

            aProductResult["gst_rate"] = str(gstRate) + "%"
            aProductResult["gst_type"] = gstComponent
            aProductResult["tax_applied"] = float(
                firstPage[i][indexOfTotalAfterDiscount].replace(",", "")) * 0.01 * gstRate
            products.append(aProductResult)

        total_tax = {
            "IGST": 0,
            "SGST": totalSgst,
            "CGST": totalCgst,
        }

        totals = lastIndexOfContainsInList(firstPage, "Total")
        self.totalmountBeforetax = firstPage[totals-1][indexOfTotal]
        self.totaltax = firstPage[totals-1][indexOfTotalTaxAmount]
        self.totalAfterTax = firstPage[totals-1][indexOfTotalAfterDiscount]
        self.totalItems = firstPage[totals-1][indexOfQty]
        return products, total_tax

    def getVendorBankInfo(self):
        return {
            "bank_name": "",
            "account_number": "",
            "ifs_code": "",
        }

    def getItemTotalInfo(self):
        returnData = {}
        returnData["tax_amount_in_words"] =convert_amount_to_words(self.totaltax.replace(",", ""))
        returnData["amount_charged_in_words"] =convert_amount_to_words(self.totalAfterTax.replace(",", ""))
        returnData["total_pcs"] = self.totalItems
        returnData["total_amount_after_tax"] =self.totalAfterTax
        returnData["total_b4_tax"] = self.totalmountBeforetax
        returnData["total_tax"] = self.totaltax
        returnData["tax_rate"] = str((float(self.totaltax.replace(",", ""))/float(self.totalAfterTax.replace(",", "")))*100) + "%"
        returnData["total_tax_percentage"] =str((float(self.totaltax.replace(",", ""))/float(self.totalAfterTax.replace(",", "")))*100) + "%"
        return returnData