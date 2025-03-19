from VendorsInvoicePdfToExcel.helper import get_list_containing,is_numeric
from VendorsInvoicePdfToExcel.helper import indexOfContainsInList

class SeemaGujral:
    def __init__(self, tables, text):
        self.tables = tables
        self.text = text
        self.taxableValue = 0
        self.totalTax = 0
        self.taxRate = 0

    def getVendorInfo(self):
        firstPage = self.tables[1]
        vendorInfo = get_list_containing(firstPage, "SEEMA GUJRAL CREATIONS LLP").split("\n")
        return {
            "vendor_name": vendorInfo[0],
            "vendor_address": ", ".join(vendorInfo[:indexOfContainsInList(vendorInfo,"MOB")]),
            "vendor_mob": get_list_containing(vendorInfo, "MOB").split("-")[-1].strip(),
            "vendor_gst":  get_list_containing(vendorInfo, "GSTIN").split(":")[-1].strip(),
            "vendor_email":  get_list_containing(vendorInfo, "Mail").split(":")[-1].strip()
        }

    def getInvoiceInfo(self):
        firstPage = self.text[1].split("\n")
        return {
            "invoice_number": get_list_containing(firstPage, "Invoice no").split("\n")[-1].strip(),
            "invoice_date": firstPage[indexOfContainsInList(firstPage, "Dated") + 1].split(" ")[-1]
        }

    def getReceiverInfo(self):
        firstPage = self.tables[1]
        receiverInfo = get_list_containing(firstPage, "Consignee (Ship to)").split("\n")
        return {
            "receiver_name": receiverInfo[indexOfContainsInList(receiverInfo, "PSL")],
            "receiver_address": ",".join(receiverInfo[indexOfContainsInList(receiverInfo, "PSL"):indexOfContainsInList(receiverInfo, "GSTIN")]),
            "receiver_gst": get_list_containing(receiverInfo, "GSTIN").split(":")[-1].strip(),
        }

    def getBillingInfo(self):
        firstPage = self.tables[1]
        billingInfo = get_list_containing(firstPage, "Buyer (Bill to)").split("\n")
        return {
            "billto_name": billingInfo[indexOfContainsInList(billingInfo, "PSL")],
            "billto_address": ",".join(billingInfo[indexOfContainsInList(billingInfo, "PSL"):indexOfContainsInList(billingInfo, "GST")]),
            "billto_gst":  get_list_containing(billingInfo, "GSTIN").split(":")[-1].strip(),
            "place_of_supply": get_list_containing(billingInfo, "Place of supply").split(":")[-1].strip(),
        }


    def getItemInfo(self):
        products = []

        gstType = []
        lastPage = self.tables[len(self.tables)]
        listOfTaxInfo = lastPage[indexOfContainsInList(lastPage, "Amount Chargeable (in")+1:indexOfContainsInList(lastPage, "Tax Amount (")]
        listOfTaxInfoHeader  =listOfTaxInfo[indexOfContainsInList(listOfTaxInfo, "Taxable")]
        self.taxableValue = float(listOfTaxInfo[-1][indexOfContainsInList(listOfTaxInfoHeader, "taxable")].split(" ")[-1].replace(",",""))
        self.totalTax = float(listOfTaxInfo[-1][-1].replace(",",""))
        self.taxRate = float(get_list_containing(listOfTaxInfo, "%").replace("%", ""))

        if indexOfContainsInList(listOfTaxInfoHeader, "IGST") != -1:
            gstType.append("IGST")
        elif indexOfContainsInList(listOfTaxInfoHeader, "SGST") != -1:
            gstType.append("SGST")
        elif indexOfContainsInList(listOfTaxInfoHeader, "CGST") != -1:
            gstType.append("CGST")

        gstType = "_".join(gstType)

        total_tax = {
            "IGST" : self.totalTax if gstType == "IGST" else 0,
            "SGST" : self.totalTax if gstType.__contains__("SGST") else 0,
            "CGST" : self.totalTax if gstType.__contains__("CGST") else 0,
        }

        listOfHeader = self.tables[1][indexOfContainsInList(self.tables[1], "Description")]
        indexOfSrNo = indexOfContainsInList(listOfHeader, "Sl")
        indexOfDescription = indexOfContainsInList(listOfHeader, "Description")
        indexOfHsn = indexOfContainsInList(listOfHeader, "Hsn")
        indexOfMrp = indexOfContainsInList(listOfHeader, "Mrp")
        indexOfQuantity = indexOfContainsInList(listOfHeader, "Quantity")
        indexOfRate = indexOfContainsInList(listOfHeader, "Rate")
        indexOfPer = indexOfContainsInList(listOfHeader, "Per")
        indexOfAmount = indexOfContainsInList(listOfHeader, "Amount")

        listOfProducts = []
        for paneNo, aPage in enumerate(self.text.values()):
           aPage = aPage.split("\n")
           if paneNo < len(self.tables)-1:
               listOfProducts.extend(aPage[indexOfContainsInList(aPage, "Description of Goods")+2 : indexOfContainsInList(aPage, "continued to page")])
           else:
               listOfProducts.extend(aPage[indexOfContainsInList(aPage, "Description of Goods")+2 : indexOfContainsInList(aPage, "GST charged @")])

        for index, aProductItem in enumerate(listOfProducts):
            listOfParticulars = aProductItem.split(" ")
            if len(listOfParticulars) < 4:
                continue

            if is_numeric(listOfParticulars[0]):
                aProductResult = {}
                aProductResult["index"] = listOfParticulars[0]
                aProductResult["HSN/SAC"] = listOfParticulars[indexOfHsn-len(listOfHeader)-1]
                aProductResult["Qty"] = " ".join(listOfParticulars[indexOfQuantity - len(listOfHeader) -1: indexOfQuantity - len(listOfHeader)+1])
                aProductResult["Rate"] = float(listOfParticulars[indexOfRate - len(listOfHeader)].strip().replace(",",""))
                aProductResult["Per"] = listOfParticulars[indexOfPer - len(listOfHeader)]
                aProductResult["mrp"] = aProductResult["Rate"]
                if indexOfMrp != -1:
                    aProductResult["mrp"] = float(listOfParticulars[indexOfMrp+1][:listOfParticulars[indexOfMrp+1].find("/")].replace(",",""))
                aProductResult["Amount"] = float(listOfParticulars[indexOfAmount - len(listOfHeader)].replace(",", "").strip())
                aProductResult["gst_type"] = gstType
                aProductResult["gst_rate"] =self.taxRate
                aProductResult["tax_applied"] = (self.taxRate * 0.01 * aProductResult["Rate"])
                poNo = ""
                for i in range(0, 3):
                    if poNo != "":
                        break
                    aItem = listOfProducts[index + i]

                    if aItem.find("ORDER NO") != -1:
                        poNo = aItem.replace(" ", "").split(".")[-1]
                        aProductResult["po_no"] = "OR-"+poNo
                    elif aItem.find("OR") != -1:
                        poNo = aItem.replace(" ", "")
                        aProductResult["po_no"] = poNo
                products.append(aProductResult)
        return products, total_tax

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        for atable in lastPage:
            for alist in atable:
                if str(alist).__contains__('Company’s Bank'):
                    return {
                        "bank_name": alist.split("\n")[indexOfContainsInList(alist.split("\n"), "Bank Name")],
                        "account_number": alist.split("\n")[indexOfContainsInList(alist.split("\n"), "A/c")],
                        "ifs_code": alist.split("\n")[indexOfContainsInList(alist.split("\n"), "IFS")],
                    }

    def getItemTotalInfo(self):
        returnData = {}
        lastPage = self.tables[len(self.tables)]

        returnData["amount_charged_in_words"] = get_list_containing(lastPage, "Amount Chargeable (in").split("\n")[-1]
        returnData["tax_amount_in_words"] = get_list_containing(get_list_containing(lastPage, "Tax Amount (").split("\n"), "Tax Amount (").split(":")[-1].strip()
        returnData["total_pcs"] = get_list_containing(lastPage[indexOfContainsInList(lastPage, "Amount Chargeable (in")-1], "pcs").strip()
        returnData["total_amount_after_tax"] = float(lastPage[indexOfContainsInList(lastPage, "Amount Chargeable (in") - 1][-1].split(" ")[-1].strip().replace(",",""))
        returnData["total_b4_tax"] = self.taxableValue
        returnData["total_tax"] = self.totalTax
        returnData["tax_rate"] = self.taxRate
        returnData["total_tax_percentage"] = self.taxRate

        return returnData
