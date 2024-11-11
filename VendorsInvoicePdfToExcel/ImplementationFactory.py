from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.PaulmiAndharsh import PaulmiAndHarsh
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
from VendorsInvoicePdfToExcel.VendorImplementations.Kalighata import Kalighata
from VendorsInvoicePdfToExcel.VendorImplementations.LinenBloomMen import LinenBloomMen
from VendorsInvoicePdfToExcel.VendorImplementations.Samohan import Samohan
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
        elif implementation == "paulmi_and_harsh":
            return PaulmiAndHarsh(tables, text_data, table_by_tabula)
        elif implementation == "linen_bloom_men":
            return LinenBloomMen(tables, text_data)
        elif implementation == "sammohan":
            return Samohan(tables, text_data)
        else:
            raise HTTPException(status_code=404, detail="Item not found")