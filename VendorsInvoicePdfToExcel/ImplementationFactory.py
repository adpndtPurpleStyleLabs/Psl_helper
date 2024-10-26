from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
from VendorsInvoicePdfToExcel.VendorImplementations.Kalighata import Kalighata
from fastapi import HTTPException

from VendorsInvoicePdfToExcel.VendorImplementations.SheetalBatra import SheetalBatra

class ImplementationFactory:
    def getImplementation(self, implementation, tables, text_data, table_by_tabula):
        implementation = str(implementation).lower().replace(' ',"")
        if  implementation == "amit_agarwal":
            return AmitAgarwal(tables, text_data)
        elif implementation == "seema_gujral":
            return SeemaGujral(tables, text_data)
        elif implementation == "kalighata":
            return Kalighata(tables, text_data, table_by_tabula)
        elif implementation == "sheetal_batra":
            return SheetalBatra(tables, text_data, table_by_tabula)
        elif implementation == "lashkaraa":
            return Lashkaraa(tables, text_data, table_by_tabula)
        else:
            raise HTTPException(status_code=404, detail="Item not found")