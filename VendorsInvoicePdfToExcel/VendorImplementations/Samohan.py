from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class Samohan:
    def __init__(self, tables, text):
        self.tables = tables
        self.text = text
        self.total_tax = {}

    def getVendorInfo(self):
        firstPage =self.text[1].split("\n")
        return {
            "vendor_name": firstPage[indexOfContainsInList(firstPage, "SAMM")][:firstPage[indexOfContainsInList(firstPage, "SAMM")].find("Inv")],
            "vendor_address": firstPage[indexOfContainsInList(firstPage, "SAMM")+1][:firstPage[indexOfContainsInList(firstPage, "SAMM")+1].find("LEX")+3]+" "+ firstPage[indexOfContainsInList(firstPage, "SAMM")+2][:firstPage[indexOfContainsInList(firstPage, "SAMM")+2].find("OAD")+3],
            "vendor_mob": "",
            "vendor_gst": firstPage[indexOfContainsInList(firstPage, "GST")].split(" ")[1],
            "vendor_email": firstPage[indexOfContainsInList(firstPage, "A/c")-1].split(" ")[0]
        }

    def getInvoiceInfo(self):
        firstPage = self.tables[1]
        return {
            "invoice_number": firstPage[2][0],
            "invoice_date": firstPage[2][-1],
        }

    def getReceiverInfo(self):
        firstPage = self.tables[1]
        firstPage.pop(0)
        billToInfo = firstPage[indexOfContainsInList(firstPage, "Bill To")][0].split("\n")
        return {
            "receiver_name": billToInfo[1],
            "receiver_address": billToInfo[2] + " " + billToInfo[3] + " " + billToInfo[4],
            "receiver_gst": billToInfo[5].split(":")[-1],
        }

    def getBillingInfo(self):
        firstPage = self.tables[1]
        firstPage.pop(0)
        billToInfo = firstPage[indexOfContainsInList(firstPage, "Bill To")][0].split("\n")
        return {
            "billto_name": billToInfo[1],
            "billto_address": billToInfo[2] + " " + billToInfo[3] + " " + billToInfo[4],
            "billto_gst": billToInfo[5].split(":")[-1],
            "place_of_supply": firstPage[indexOfContainsInList(firstPage, "Destination")][-1].split("\n")[-1]
        }

    def getItemInfo(self):
        firstPage = self.tables[1]
        products = []
        total_tax = {
            "IGST": 0,
            "SGST": firstPage[indexOfContainsInList(firstPage, "Tax Amount") + 1][2],
            "CGST": firstPage[indexOfContainsInList(firstPage, "Tax Amount") + 1][4],
        }
        self.total_tax = total_tax
        indexOfHeader = indexOfContainsInList(firstPage, "Sl No")
        indexOfPONo = indexOfContainsInList(firstPage[indexOfHeader], "PO")
        if indexOfPONo == -1 :
            indexOfPONo = indexOfContainsInList(firstPage, "Description")

        for i in range(indexOfHeader + 1, len(firstPage)):
            aProductResult = {}
            if firstPage[i][0] == '':
                break
            aProductResult["index"] = firstPage[i][0]
            aProductResult["vendor_code"] = firstPage[i][2]
            aProductResult["HSN/SAC"] = firstPage[i][3]
            aProductResult["Qty"] = firstPage[i][4]
            aProductResult["Rate"] = firstPage[i][6]
            aProductResult["Per"] = firstPage[i][8]
            aProductResult["mrp"] = firstPage[i][5]
            aProductResult["Amount"] = firstPage[i][9]
            aProductResult["gst_type"] = "CGST SGST"
            aProductResult["gst_rate"] = firstPage[indexOfContainsInList(firstPage, "CGST")][3]
            aProductResult["tax_applied"] = (int(firstPage[i][9]) * 0.01 * int(firstPage[i][7].replace("%", ""))) / 2
            aProductResult["po_cost"] = int(firstPage[i][9]) + (aProductResult["tax_applied"] *2)
            aProductResult["po_no"] = firstPage[i][indexOfPONo]
            aProductResult["or_po_no"] = ""
            aProductResult["debit_note_no"] = ""
            products.append(aProductResult)
        return products, total_tax

    def getVendorBankInfo(self):
        firstPage = self.text[1].split("\n")
        return {
            "bank_name": firstPage[indexOfContainsInList(firstPage, "Bank Na")].split(":")[-1],
            "account_number": firstPage[indexOfContainsInList(firstPage, "A/c")].split(" ")[2],
            "ifs_code": firstPage[indexOfContainsInList(firstPage, "IFS")],
        }

    def getItemTotalInfo(self):
        firstPage = self.tables[1]
        returnData = {}
        returnData["tax_amount_in_words"] = convert_amount_to_words(int(self.total_tax["IGST"] )+ int(self.total_tax["CGST"]) + int(self.total_tax["SGST"] ))
        returnData["amount_charged_in_words"] = convert_amount_to_words(int(firstPage[indexOfContainsInList(firstPage, "Total")][-1]))
        returnData["total_pcs"] = firstPage[indexOfContainsInList(firstPage, "Total")-3][4]
        returnData["total_amount_after_tax"] = str(firstPage[indexOfContainsInList(firstPage, "Total")][-1])
        returnData["total_b4_tax"] = firstPage[indexOfContainsInList(firstPage, "Total")+4][0]
        returnData["total_tax"] =firstPage[indexOfContainsInList(firstPage, "Total")+4][-1]
        returnData["tax_rate"] = str(round(int(firstPage[indexOfContainsInList(firstPage, "Total")+4][-1])/int( firstPage[indexOfContainsInList(firstPage, "Total")+4][0])*100))
        returnData["total_tax_percentage"] = str(round(int(firstPage[indexOfContainsInList(firstPage, "Total")+4][-1])/int( firstPage[indexOfContainsInList(firstPage, "Total")+4][0])*100))
        return returnData