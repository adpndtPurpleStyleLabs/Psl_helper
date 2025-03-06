from VendorsInvoicePdfToExcel.helper import indexOfContainsInList, convert_to_ddmmyy
from VendorsInvoicePdfToExcel.helper import convert_amount_to_words
from VendorsInvoicePdfToExcel.helper import find_nth_occurrence_of, get_list_containing

class RnFashion:
    def __init__(self, tables, text_data, table_by_tabula):
        self.tables = tables
        self.text_data = text_data
        self.table_by_tabula = table_by_tabula
        self.totalPcs = 0

    def getVendorInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "vendor_name": firstPageText[indexOfContainsInList(firstPageText, "R. N")],
            "vendor_address": ", ".join(firstPageText[0:3]),
            "vendor_mob": "N/A",
            "vendor_gst": firstPageText[indexOfContainsInList(firstPageText, "GST")].split(":")[-1],
            "vendor_email": "N/A"
        }

    def getInvoiceInfo(self):
        firstPageText = self.text_data[1].split("\n")
        return {
            "invoice_number": firstPageText[indexOfContainsInList(firstPageText, "INV N")].split(":")[-2].strip().split(" ")[0],
            "invoice_date": convert_to_ddmmyy(firstPageText[indexOfContainsInList(firstPageText, "Date")].split(" ")[-1])
        }

    def getReceiverInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfo = firstPageText[indexOfContainsInList(firstPageText, "Bill to party")+1:indexOfContainsInList(firstPageText, "description")]
        name_info = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split(":")[indexOfContainsInList(receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split(":"), "PSL")][:]
        address_info = receiverInfo[indexOfContainsInList(receiverInfo, "Address")].split(":")[1]
        return {
            "receiver_name":name_info[:name_info.find("TED ")+3],
            "receiver_address":address_info[:address_info.find("Ve")]+  " " + receiverInfo[indexOfContainsInList(receiverInfo, "Address")+1] +  " " + receiverInfo[indexOfContainsInList(receiverInfo, "Address")+2],
            "receiver_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].replace(":", "").split(" ")[2]
        }

    def getBillingInfo(self):
        firstPageText = self.text_data[1].split("\n")
        receiverInfo = firstPageText[
                       indexOfContainsInList(firstPageText, "Bill to party") + 1:indexOfContainsInList(firstPageText,
                                                                                                       "description")]
        name_info = receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split(":")[
                        indexOfContainsInList(receiverInfo[indexOfContainsInList(receiverInfo, "PSL")].split(":"),
                                              "PSL")][:]
        address_info = receiverInfo[indexOfContainsInList(receiverInfo, "Address")].split(":")[1]

        return {
            "billto_name": name_info[:name_info.find("TED ")+3],
            "billto_address":address_info[:address_info.find("Ve")]+  " " + receiverInfo[indexOfContainsInList(receiverInfo, "Address")+1] +  " " + receiverInfo[indexOfContainsInList(receiverInfo, "Address")+2],
            "place_of_supply": receiverInfo[indexOfContainsInList(receiverInfo, "State")].replace(":", "").split(" ")[2],
            "billto_gst": receiverInfo[indexOfContainsInList(receiverInfo, "GST")].replace(":", "").split(" ")[2]
        }

    def getItemInfo(self):
        pages = self.tables
        firstPage = self.tables[1]

        taxableList = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Amount (in"):indexOfContainsInList(self.text_data[1].split("\n"), "total amount (")]
        totals_list =taxableList[indexOfContainsInList(taxableList, "total")-1].split(" ")

        total_tax = {
            "IGST": float(totals_list[find_nth_occurrence_of(totals_list, "%",3) +1].replace(",", "").strip()),
            "SGST": float(totals_list[find_nth_occurrence_of(totals_list, "%",2) +1].replace(",", "").strip()),
            "CGST": float(totals_list[find_nth_occurrence_of(totals_list, "%",1) +1].replace(",", "").strip())
        }

        gstType = ""
        if total_tax["IGST"] > 0 :
            gstType += "_IGST"

        if total_tax["SGST"] > 0 :
            gstType += "_SGST"

        if total_tax["CGST"] > 0 :
            gstType += "_CGST"

        gstType = gstType.lstrip("_")

        products = []
        indexOfHeader =indexOfContainsInList(self.tables[1], "Qty")
        indexOfSr = indexOfContainsInList(firstPage[indexOfHeader], "S\nL")
        indexOfItemname = indexOfContainsInList(firstPage[indexOfHeader], "Description")
        indexOfHsn = indexOfContainsInList(firstPage[indexOfHeader], "HSN")
        indexOfQty = indexOfContainsInList(firstPage[indexOfHeader], "Qty")
        indexOfPer = indexOfContainsInList(firstPage[indexOfHeader], "Unit")
        indexOfPrice = indexOfContainsInList(firstPage[indexOfHeader], "Price")
        indexOfTaxAmount = indexOfContainsInList(firstPage[indexOfHeader], "Tax\nAmount")
        indexOfAmt =find_nth_occurrence_of(firstPage[indexOfHeader], "Amount", 2)
        indexOfTaxRate = indexOfContainsInList(firstPage[indexOfHeader], "Tax\nRate")
        indexOfMrp = indexOfContainsInList(firstPage[indexOfHeader], "MRP")
        poInfo = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "PO No")].split(":")[-1].strip()

        lenOfHeader = len(firstPage[indexOfHeader])
        reverseIndexOfAmt = indexOfAmt - lenOfHeader
        reverseindexOfTaxRate = indexOfTaxRate - lenOfHeader
        reverseindexOfTaxAmount = indexOfTaxAmount - lenOfHeader
        reverseindexOfPrice = indexOfPrice - lenOfHeader +1
        reverseindexOfPer = indexOfPer - lenOfHeader+1
        reverseindexOfHsn = indexOfHsn - lenOfHeader+1
        reverseIndexOfMrp = indexOfMrp - lenOfHeader+1
        count =0
        for itemIndex, item in enumerate(self.text_data [1].split("\n")[indexOfContainsInList(self.text_data [1].split("\n"), "Description")+2:]):
            itemList = item.split(" ")
            if indexOfContainsInList(itemList, "total") != -1:
                break
            if itemList.__len__() < 3:
                continue
            aProductResult = {}
            aProductResult["po_no"] = poInfo.replace(" ", "").split(",")[count]
            aProductResult["index"] = itemList[indexOfSr]
            aProductResult["HSN/SAC"] = itemList[reverseindexOfHsn]
            aProductResult["Qty"] = itemList[indexOfQty - indexOfAmt]
            aProductResult["Rate"] =  float(itemList[reverseindexOfPrice].replace(",","").replace(" ",""))
            aProductResult["mrp"] =  float(itemList[reverseIndexOfMrp].replace(",","").replace(" ",""))
            aProductResult["Amount"] = float(itemList[reverseIndexOfAmt].replace(",","").replace(" ",""))
            aProductResult["gst_rate"] = float(itemList[reverseindexOfTaxRate].replace("%","").replace(" ",""))
            aProductResult["Per"] =  itemList[reverseindexOfPer]
            aProductResult["gst_type"] = gstType
            aProductResult["tax_applied"] = float(itemList[reverseindexOfTaxAmount].replace(",",""))
            products.append(aProductResult)
            count +=1

        return products, total_tax

    def getVendorBankInfo(self):
        pages = self.text_data
        lastPage = pages[len(pages)]
        bankInfo = lastPage.split("\n")[indexOfContainsInList(lastPage.split("\n"), "BANNK"):]
        return {
            "bank_name": bankInfo[indexOfContainsInList(bankInfo, "BANK NAME")].split("-")[-1].strip() + " " + bankInfo[indexOfContainsInList(bankInfo, "BRANCH -")].split("BRANCH -")[-1].strip(),
            "account_number": bankInfo[indexOfContainsInList(bankInfo, "AC NO")].split("-")[-1].strip(),
            "ifs_code": bankInfo[indexOfContainsInList(bankInfo, "IFSC")].split("-")[-1].strip(),
        }

    def getItemTotalInfo(self):
        lastPage  =self.tables[len(self.text_data)]
        totals_list = self.text_data[1].split("\n")[indexOfContainsInList(self.text_data[1].split("\n"), "Amount (in"):indexOfContainsInList(self.text_data[1].split("\n"), "total amount (")]
        amountBeforeTax = float(get_list_containing(totals_list, "total").split(" ")[1].replace(",", "").strip())
        taxAmount = float(get_list_containing(totals_list, "total").split(" ")[-1].replace(",", "").strip())
        totalAmount =  taxAmount+ amountBeforeTax

        gstPercentageList = totals_list[indexOfContainsInList(totals_list, "total") - 1].split(" ")

        total_tax = {
            "IGST": float(gstPercentageList[find_nth_occurrence_of(gstPercentageList, "%", 3) ].replace("%", "").strip()),
            "SGST": float(gstPercentageList[find_nth_occurrence_of(gstPercentageList, "%", 2) ].replace("%", "").strip()),
            "CGST": float(gstPercentageList[find_nth_occurrence_of(gstPercentageList, "%", 1) ].replace("%", "").strip())
        }

        returnData = {}

        if total_tax["IGST"] > 0:
            returnData["tax_rate"]  = total_tax["IGST"]
        else:
            returnData["tax_rate"] = total_tax["SGST"] + total_tax["CGST"]

        returnData["tax_amount_in_words"] = convert_amount_to_words(taxAmount)
        returnData["amount_charged_in_words"] = convert_amount_to_words(totalAmount)
        returnData["total_pcs"] = self.totalPcs
        returnData["total_amount_after_tax"] = totalAmount
        returnData["total_b4_tax"] = amountBeforeTax
        returnData["total_tax"] = taxAmount
        returnData["total_tax_percentage"] = returnData["tax_rate"]
        return returnData