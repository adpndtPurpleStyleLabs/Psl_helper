from VendorsInvoicePdfToExcel.helper import indexOfContainsInList


class AmitAgarwal:
    def __init__(self, tables, text_data):
        self.tables = tables
        self.text_data = text_data

    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        vendonInfo = {}
        return {
            "vendor_name": firstPageText[0],
            "vendor_address": firstPageText[1] + " " + firstPageText[2],
            "vendor_mob": firstPageText[3],
            "vendor_gst": firstPageText[6],
            "vendor_email": firstPageText[5]
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "invoice_number": firstPageText[indexOfContainsInList(firstPageText, "Invoice No")],
            "invoice_date": firstPageText[indexOfContainsInList(firstPageText, "Invoice Date")]
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Details of Receiver")
        return {
            "receiver_name": firstPageText[indexOfReceiver + 1].split("Name :")[-2],
            "receiver_address": firstPageText[indexOfReceiver + 2].split("Address :")[-2],
            "receiver_gst": firstPageText[indexOfReceiver + 3].split(" ")[
                indexOfContainsInList(firstPageText[indexOfReceiver + 3].split(" "), ":") + 1],
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        indexOfReceiver = indexOfContainsInList(firstPageText, "Details of Receiver")
        print(firstPageText[0])
        return {
            "billto_name": firstPageText[indexOfReceiver + 1].split("Name :")[-1],
            "billto_address": firstPageText[indexOfReceiver + 2].split("Address :")[-1],
            "billto_gst": firstPageText[indexOfReceiver + 4],
            "place_of_supply": firstPageText[indexOfReceiver + 2].split("Address :")[-2].split(",")[-2]
        }

    def getItemInfo(self):
        pages = self.tables
        products = []
        for index, aPage in enumerate(pages.values()):
            indexOfHeader = indexOfContainsInList(pages, "Name of Product")
            isOrderNoPrsent = False
            if indexOfContainsInList(aPage[indexOfHeader], "ORDER NO.") != 0:
                isOrderNoPrsent = True
            for prodIndex, aProduct in enumerate(aPage):
                if prodIndex <= indexOfHeader + 1:
                    continue
                orderNo = ""
                if isOrderNoPrsent:
                    orderNo = aPage[prodIndex][19]
                aProdInfo = {
                    "index": aPage[prodIndex][0].replace(".", ""),
                    "id_1": aPage[prodIndex][2],
                    "id_2": aPage[prodIndex][4],
                    "HSN/SAC": aPage[prodIndex][6],
                    "Qty": aPage[prodIndex][8],
                    "Rate": aPage[prodIndex][12],
                    "Per": "",
                    "Amount": aPage[prodIndex][18],
                    "orderNo": orderNo,
                }
                products.append(aProdInfo)
                if prodIndex == indexOfContainsInList(aPage, "Total Invoice") - 3:
                    break

        return products

    def getVendorBankInfo(self):
        lastPageText = self.tables[len(self.tables)]
        indexOfBankDetails = indexOfContainsInList(lastPageText, "Bank Details")
        bankDetailsList = lastPageText[indexOfContainsInList(lastPageText, "Bank Details")][0].split("\n")
        print(indexOfBankDetails)
        return {
            "bank_name": bankDetailsList[indexOfContainsInList(bankDetailsList, "BANK NAME")],
            "account_number": bankDetailsList[indexOfContainsInList(bankDetailsList, "ACCOUNT")],
            "ifs_code": bankDetailsList[indexOfContainsInList(bankDetailsList, "IFSC")],
        }

    def getItemTotalInfo(self):
        lastPageText = self.tables[len(self.tables)]
        returnData = {}
        print(lastPageText)

        returnData["total_pcs"] = lastPageText[indexOfContainsInList(lastPageText, "Total Invoice") - 2][1]
        returnData["total_amount_after_tax"] = lastPageText[indexOfContainsInList(lastPageText, "After Tax")][
            indexOfContainsInList(lastPageText[indexOfContainsInList(lastPageText, "After Tax")], "After Tax") + 1]
        returnData["total_b4_tax"] = lastPageText[indexOfContainsInList(lastPageText, "Before Tax")][
            indexOfContainsInList(lastPageText[indexOfContainsInList(lastPageText, "Before Tax")], "Before Tax") + 1]
        returnData["total_tax"] = lastPageText[indexOfContainsInList(lastPageText, "Tax Amount")][
            indexOfContainsInList(lastPageText[indexOfContainsInList(lastPageText, "Tax Amount")], "Tax Amount") + 1]
        returnData["tax_rate"] = ""
        returnData["total_tax_percentage"] = ""
        return returnData
