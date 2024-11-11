from VendorsInvoicePdfToExcel.helper import indexOfContainsInList
import re

class LinenBloomMen:
    def __init__(self, tables, text):
        self.tables = tables
        self.text = text
        self.gstRate = ""

    def getVendorInfo(self):
        firstPage = self.tables[1]
        return {
            "vendor_name": firstPage[0][0].split("\n")[0],
            "vendor_address": firstPage[0][0].split("\n")[1] + " " + firstPage[0][0].split("\n")[2] + " " +
                              firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "State")],
            "vendor_mob": "",
            "vendor_gst": firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "GST")],
            "vendor_email": firstPage[0][0].split("\n")[indexOfContainsInList(firstPage[0][0].split("\n"), "Mail")]
        }

    def getInvoiceInfo(self):
        firstPage = self.tables[1]
        return {
            "invoice_number": firstPage[0][indexOfContainsInList(firstPage[0], "Invoice")].split("\n")[-1],
            "invoice_date":
                self.text[1].split("\n")[indexOfContainsInList(self.text[1].split("\n"), "M/o")].split("M/o")[-1],
        }

    def getReceiverInfo(self):
        firstPage = self.tables[1]
        receiverInfo = firstPage[0][0].split("\n")
        receiverInfo = receiverInfo[indexOfContainsInList(receiverInfo, "Ship ")+1: indexOfContainsInList(receiverInfo, "Bill ")]
        return {
            "receiver_name": receiverInfo[0],
            "receiver_address": receiverInfo[1] + " " +receiverInfo[2] + " " +  receiverInfo[indexOfContainsInList(receiverInfo, "State")].split(",")[0].split(":")[-1],
            "receiver_gst":receiverInfo[indexOfContainsInList(receiverInfo, "GSTIN")].split(":")[-1],
        }

    def getBillingInfo(self):
        firstPage = self.tables[1]
        billInfo = firstPage[0][0].split("\n")
        billInfo = billInfo[
                       indexOfContainsInList(billInfo, "Bill ") + 1:]

        return {
            "billto_name": billInfo[0],
            "billto_address": billInfo[1] + " " +billInfo[2] ,
            "billto_gst": billInfo[indexOfContainsInList(billInfo, "GSTIN")].split(":")[-1],
            "place_of_supply": billInfo[indexOfContainsInList(billInfo, "State")].split(",")[0].split(":")[-1]
        }

    def getItemInfo(self):
        allPages = self.tables
        lenOfPages = len(allPages)
        firstPage = self.tables[1]
        products = []
        lastPage = allPages[lenOfPages]

        total_tax = {
            "IGST": 0,
            "SGST": 0,
            "CGST": 0,
        }
        for paneNo, aPage in enumerate(self.tables.values()):
            if len(aPage[indexOfContainsInList(aPage, "Sl")+1]) <5:
                # check if page contains products
                continue

            indexOfHeader = indexOfContainsInList(aPage, "Sl")
            indexOfSrNo = indexOfContainsInList(aPage[indexOfHeader], "Sl")
            indexOfDescription = indexOfContainsInList(aPage[indexOfHeader], "Descrip")
            indexOfHsnCode = indexOfContainsInList(aPage[indexOfHeader], "HSN")
            indexOFQty = indexOfContainsInList(aPage[indexOfHeader], "Quantity")
            indexRateWithTax = indexOfContainsInList(aPage[indexOfHeader], "Incl. of")
            indexOfRate = indexOfContainsInList(aPage[indexOfHeader], "Rate") + 1
            indexOfPer = indexOfContainsInList(aPage[indexOfHeader], "per")
            indexOfAmount = indexOfContainsInList(aPage[indexOfHeader], "Amount")
            goodsIndex = indexOfHeader+1
            noOfGoodInPage = len(aPage[indexOfHeader+1][0].split("\n"))
            for i in range(noOfGoodInPage):
                aProductResult = {}
                aProductResult["vendor_code"] = ""
                aProductResult["po_no"] = ""

                try :
                    rateWithTax = re.findall(r'\d+',
                                             aPage[goodsIndex][indexRateWithTax].split("\n")[i].replace(",", ""))
                    rateWithTax = int(rateWithTax[0]) if rateWithTax else None
                    rateWithOutTax = re.findall(r'\d+', aPage[goodsIndex][indexOfRate].split("\n")[i].replace(",", ""))
                    rateWithOutTax = int(rateWithOutTax[0]) if rateWithOutTax else None
                    aProductResult["vendor_code"] = aPage[goodsIndex][indexOfDescription].split("\n")[(i * 3) + 1]
                    aProductResult["po_no"] = \
                    aPage[goodsIndex][indexOfDescription].split("\n")[(i * 3) + 2].split("Po")[-1]

                except Exception as e:
                    print(e)

                aProductResult["index"] = aPage[goodsIndex][indexOfSrNo].split("\n")[i]
                aProductResult["HSN/SAC"] = aPage[goodsIndex][indexOfHsnCode].split("\n")[i]
                aProductResult["Qty"] = aPage[goodsIndex][indexOFQty].split("\n")[i]
                aProductResult["Rate"] = aPage[goodsIndex][indexOfRate].split("\n")[i]
                aProductResult["Per"] = aPage[goodsIndex][indexOfPer].split("\n")[i]
                aProductResult["mrp"] = aPage[goodsIndex][indexOfRate].split("\n")[i]
                aProductResult["Amount"] = rateWithTax
                aProductResult["gst_type"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1], "GST")]
                aProductResult["gst_rate"] = int(((rateWithTax-rateWithOutTax)/rateWithOutTax)*100)
                aProductResult["tax_applied"] = rateWithTax-rateWithOutTax
                aProductResult["po_cost"] = rateWithTax
                aProductResult["or_po_no"] =""
                aProductResult["debit_note_no"] = ""

                if aProductResult["gst_type"] == "IGST":
                    total_tax["IGST"] = total_tax["IGST"] + rateWithTax-rateWithOutTax
                elif aProductResult["gst_type"] == "SGST":
                    total_tax["SGST"] = total_tax["SGST"] + rateWithTax-rateWithOutTax
                elif aProductResult["gst_type"] == "CGST":
                    total_tax["CGST"] = total_tax["CGST"] + rateWithTax-rateWithOutTax

                products.append(aProductResult)
        self.gstRate = products[0]["gst_rate"]
        return products, total_tax


    def getGstInformation(self):
        lastPage = self.tables[len(self.tables)]
        return {
            "gst_type": lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1][indexOfContainsInList(lastPage[indexOfContainsInList(lastPage, "Amount Ch")+1], "GST")],
            "gst_rate":  self.gstRate
        }

    def getVendorBankInfo(self):
        lastPage = self.tables[len(self.tables)]
        bankDetails = lastPage[indexOfContainsInList(lastPage, "Bank De")][0].split("\n")
        return {
            "bank_name": bankDetails[indexOfContainsInList(bankDetails, "Bank Name")].split(" ")[2].replace(":",""),
            "account_number": bankDetails[indexOfContainsInList(bankDetails, "Bank Name")].split(" ")[-1],
            "ifs_code": bankDetails[indexOfContainsInList(bankDetails, "IFS")].split(":")[-1],
        }

    def getItemTotalInfo(self):
        returnData = {}
        lastPage = self.tables[len(self.tables)]
        returnData["total_pcs"] = lastPage[indexOfContainsInList(lastPage, "Total")][3]
        returnData["total_amount_after_tax"] = lastPage[indexOfContainsInList(lastPage, "Total")][-1].split(" ")[-1]
        returnData["total_b4_tax"] = lastPage[indexOfContainsInList(lastPage, "OUTPUT")+1][0].split("\n")[0]
        returnData["total_tax"] = lastPage[indexOfContainsInList(lastPage, "OUTPUT")+1][0].split("\n")[-1]
        returnData["tax_rate"] = self.gstRate
        returnData["total_tax_percentage"] =  self.gstRate
        returnData["tax_amount_in_words"] = lastPage[indexOfContainsInList(lastPage, "Tax Amount (in")][0].split("\n")[0].split(":")[-1]
        returnData["amount_charged_in_words"] = lastPage[indexOfContainsInList(lastPage, "Amount Ch")][0].split("\n")[-1]

        return returnData