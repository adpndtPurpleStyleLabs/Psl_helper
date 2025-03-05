from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, get_list_containing
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words

class AmitAgarwal:
    def __init__(self, tables, text_data):
        self.tables = tables
        self.text_data = text_data
        self.typeOfInvoice = ""
        self.isOrderColomOverFlowed = False
        self.poIdsList = []

    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
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
            "invoice_number": firstPageText[indexOfContainsInList(firstPageText, "Invoice No")].split(":")[-1].strip(),
            "invoice_date":firstPageText[indexOfContainsInList(firstPageText, "Invoice Date")].split(":")[-1].strip()
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

    def getTypeOfInvoice(self, pdf):
        length = len(pdf)
        lastPage = pdf[length]
        secondLastPage = pdf[length-1] if length > 1 else lastPage
        typeOfInvoice = "NA"
        indexOfTotalInvoiceAmountInWords = indexOfContainsInList(lastPage, 'Total Invoice Amount in Words:')
        if indexOfTotalInvoiceAmountInWords != -1:
            if (indexOfContainsInList(lastPage, 'PO ON') != -1) :
                self.poIdsList = get_list_containing(get_list_containing(lastPage, "CLIENT ORDER PO").split("\n"), "CLIENT ORDER PO").split(":")[-1].replace(")","").strip().split(",")
                return "po"
            elif  (indexOfContainsInList(lastPage, 'client name') != -1):
                self.poIdsList = get_list_containing(get_list_containing(lastPage, "CLIENT name").split("\n"), "CLIENT name").split(":")[-1].replace(")","").strip().split(",")
                return "po"
            elif  (indexOfContainsInList(lastPage, 'OUTRIGHT PCS') != -1):
                return "or_po"

        if typeOfInvoice == "NA":
            for aTableList in secondLastPage:
                indexOfTotalInvoiceAmountInWords = indexOfContainsInList(aTableList, 'Total Invoice Amount in Words:')
                if indexOfTotalInvoiceAmountInWords != -1:
                    if (indexOfContainsInList(aTableList, 'PO NO') != -1 or indexOfContainsInList(aTableList, 'name') != -1):
                        typeOfInvoice = "po"
                        break
                    if (indexOfContainsInList(aTableList, 'OUTRIGHT') != -1):
                        typeOfInvoice = "or_po"
                        break

        return typeOfInvoice

    def getItemInfo(self):
        pages = self.tables
        products = []
        typeOfInvoice = self.getTypeOfInvoice(pages)
        self.typeOfInvoice = typeOfInvoice
        firstPage = pages[1]
        indexOfHeader = -1
        for indexOfList, aList in enumerate(firstPage):
            indexOfHeader = indexOfList if indexOfContainsInList(aList, "Name of Product") != -1 else indexOfHeader
            if indexOfHeader != -1:
                break
        indexOfCGST = indexOfContainsInList(firstPage[indexOfHeader], "CGST")
        indexOfSGST = indexOfContainsInList(firstPage[indexOfHeader], "SGST")
        indexOfIGST = indexOfContainsInList(firstPage[indexOfHeader], "I GST")
        isOrderNoOverFlowed = True if typeOfInvoice == "or_po" and indexOfContainsInList(firstPage[indexOfHeader], "ORDER NO") == -1 else False
        self.isOrderColomOverFlowed = isOrderNoOverFlowed
        orderNoList = self.create_na_list(1000)
        if isOrderNoOverFlowed:
            if indexOfContainsInList(pages[2], "ORDER NO") != -1:
                orderNoList = pages[2]

        for index, aPage in enumerate(pages.values()):
            for prodIndex, aProduct in enumerate(aPage):
                if prodIndex <= indexOfHeader + 1:
                    continue

                gstType = gstRate = gstApplied = ""
                if aPage[prodIndex][indexOfSGST] != '':
                    gstType = "CGST"
                    gstRate = aPage[prodIndex][indexOfSGST]
                    gstApplied = aPage[prodIndex][indexOfIGST+1]
                elif aPage[prodIndex][indexOfCGST+1] != '':
                    gstType = "SGST"
                    gstRate = aPage[prodIndex][indexOfCGST+1]
                    gstApplied =  aPage[prodIndex][indexOfIGST+2]
                elif aPage[prodIndex][indexOfIGST+2] != '':
                    gstType = "IGST"
                    gstRate = aPage[prodIndex][indexOfIGST+2]
                    gstApplied = aPage[prodIndex][indexOfIGST+3]

                or_po_value = ""
                if self.typeOfInvoice == "or_po":
                    indexOfOrderNo = indexOfContainsInList(firstPage[indexOfHeader], "ORDER NO")
                    if indexOfOrderNo != -1:
                        or_po_value =  (aPage[prodIndex][indexOfContainsInList(aPage[indexOfOrderNo], "Order")]
                                        .replace("(","")
                                        .replace(")","")
                                        .strip())

                    if isOrderNoOverFlowed :
                        or_po_value = orderNoList[int(aPage[prodIndex][0].replace(".", "").strip())][0]

                aProdInfo = {
                    "index": aPage[prodIndex][0].replace(".", ""),
                    "vendor_code": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "STYLE")],
                    "HSN/SAC": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "HSN")],
                    "Qty": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "Qty")],
                    "mrp": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "RAT")],
                    "Rate": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "Taxable")],
                    "Amount": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "Taxable")],
                    "gst_type": gstType,
                    "gst_rate": gstRate,
                    "Per": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "PCS")],
                    "tax_applied": gstApplied,
                    "po_cost": aPage[prodIndex][indexOfContainsInList(aPage[indexOfHeader], "TOTAL")+3],
                    "po_no":  self.poIdsList[int(aPage[prodIndex][0].replace(".", "").strip()) -1] if typeOfInvoice == "po"  else "",
                    "or_po_no":  or_po_value,
                    "debit_note_no": "" if not typeOfInvoice else "",
                }
                products.append(aProdInfo)
                if prodIndex == indexOfContainsInList(aPage, "Total Invoice") - 3:
                    break
        total_tax = self.calculateTotal()
        return products,total_tax

    def create_na_list(self, length):
        return [None] * length

    def calculateTotal(self):
        pages =  self.tables
        length = len(pages)
        lastPage = pages[length]
        secondLastPage = pages[length-1] if len(pages) > 1 else lastPage
        indexOfCGST = indexOfSGST = indexOfIGST = -1
        total_tax = {
            "IGST": 0,
            "SGST": 0,
            "CGST": 0,
        }
        for index, aList in enumerate(lastPage):
            if indexOfContainsInList(aList, "Before Tax") != -1 :
                indexOfCGST = index+1
                indexOfSGST = indexOfCGST+1
                indexOfIGST = indexOfSGST+1
                return {
                    "CGST": float(lastPage[indexOfCGST][-1]),
                    "SGST": float(lastPage[indexOfSGST][-1]),
                    "IGST": float(lastPage[indexOfIGST][-1]),
                }
                break

        if indexOfCGST == -1 :
            for index, aList in enumerate(secondLastPage):
                if indexOfContainsInList(aList, "Before Tax") != -1:
                    indexOfCGST = index + 1
                    indexOfSGST = indexOfCGST + 1
                    indexOfIGST = indexOfSGST + 1
                    return {
                        "CGST": float(secondLastPage[indexOfCGST][-1]),
                        "SGST": float(secondLastPage[indexOfSGST][-1]),
                        "IGST": float(secondLastPage[indexOfIGST][-1]),
                    }
        return total_tax

    def getVendorBankInfo(self):
        pages = self.tables
        length = len(self.tables)
        lastPage = pages[length]
        secondLastPage = pages[length-1] if len(pages) > 1 else lastPage
        indexOfPageContainingBankDetails = -1
        indexOfBankDetailsInThatPage = -1
        for index, aList in enumerate(lastPage):
            if indexOfContainsInList(aList, " Bank Details") != -1:
                indexOfPageContainingBankDetails = length
                indexOfBankDetailsInThatPage = index
                break

        if indexOfPageContainingBankDetails == -1:
            for index, aList in enumerate(secondLastPage):
                if indexOfContainsInList(aList, " Bank Details") != -1:
                    indexOfPageContainingBankDetails = length-1
                    indexOfBankDetailsInThatPage = index
                    break


        bankDetails = pages[indexOfPageContainingBankDetails][indexOfBankDetailsInThatPage][indexOfContainsInList(pages[indexOfPageContainingBankDetails][indexOfBankDetailsInThatPage], "BANK")].split("\n")

        return {
            "bank_name": bankDetails[indexOfContainsInList(bankDetails, "BANK NAME")].split(":")[-1],
            "account_number": bankDetails[indexOfContainsInList(bankDetails, "ACCOUNT")].split(".")[-1],
            "ifs_code": bankDetails[indexOfContainsInList(bankDetails, "IFSC")].split(":")[-1]
        }

    def getItemTotalInfo(self):
        pages = self.tables
        length = len(pages)
        lastPage = pages[length]
        secondLastPage = pages[length-1] if len(pages) > 1 else lastPage
        indexOfTotals = -1
        indexOfPateOfTotals = -1
        for index, aList in enumerate(lastPage):
           if  indexOfContainsInList(aList, "Total Amount Before") != -1:
               indexOfPateOfTotals = length
               indexOfTotals = index
               break

        if indexOfTotals == -1 :
            for index, aList in enumerate(secondLastPage):
                if indexOfContainsInList(aList, "Total Amount Before") != -1:
                    indexOfPateOfTotals = length -1
                    indexOfTotals = index
                    break

        indexOfTotalAmount = -1 if self.typeOfInvoice == "or_po" and self.isOrderColomOverFlowed  else -2
        if self.typeOfInvoice == "po":
             indexOfTotalAmount = -1

        indexOfTaxableAmount =0
        if self.typeOfInvoice ==  "or_po":
            indexOfTaxableAmount = 4
        elif self.typeOfInvoice == "po":
            indexOfTaxableAmount = 5

        return {
            "total_pcs" : pages[indexOfPateOfTotals][indexOfTotals-2][1],
            "total_amount_after_tax" : pages[indexOfPateOfTotals][indexOfTotals - 2][indexOfTotalAmount],
            "total_b4_tax" : pages[indexOfPateOfTotals][indexOfTotals - 2][indexOfTaxableAmount],
            "total_tax" : pages[indexOfPateOfTotals][indexOfTotals +4][-1],
            "tax_rate" : "N/A",
            "total_tax_percentage" : "N/A",
            "tax_amount_in_words" : convert_amount_to_words(pages[indexOfPateOfTotals][indexOfTotals +4][-1]),
            "Chargeable" : "",
            "amount_charged_in_words" : pages[indexOfPateOfTotals][indexOfTotals][0][pages[indexOfPateOfTotals][indexOfTotals][0].find(":")+3: pages[indexOfPateOfTotals][indexOfTotals][0].find("ONLY")+4]
        }