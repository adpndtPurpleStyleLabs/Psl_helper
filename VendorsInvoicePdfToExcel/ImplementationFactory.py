from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.CoutureByNiharika import CoutureByNiharika
from VendorsInvoicePdfToExcel.VendorImplementations.Espana import Espana
from VendorsInvoicePdfToExcel.VendorImplementations.Fatiz import Fatiz
from VendorsInvoicePdfToExcel.VendorImplementations.KasbahClothing import KasbahClothing
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.MrunaliniRao import MrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.PaulmiAndharsh import PaulmiAndHarsh
from VendorsInvoicePdfToExcel.VendorImplementations.RnFashion import RnFashion
from VendorsInvoicePdfToExcel.VendorImplementations.SaakshaAndKinni import SaakshaAndKinni
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
from VendorsInvoicePdfToExcel.VendorImplementations.Kalighata import Kalighata
from VendorsInvoicePdfToExcel.VendorImplementations.LinenBloomMen import LinenBloomMen
from VendorsInvoicePdfToExcel.VendorImplementations.Samohan import Samohan
from VendorsInvoicePdfToExcel.VendorImplementations.Masaba import Masaba
from VendorsInvoicePdfToExcel.VendorImplementations.Ruhaan import Ruhaan
from VendorsInvoicePdfToExcel.VendorImplementations.Riyaasat import Riyaasat
from VendorsInvoicePdfToExcel.VendorImplementations.MonkAndMei import MonkAndMei
from VendorsInvoicePdfToExcel.VendorImplementations.Amyra import Amyra
from fastapi import HTTPException

from VendorsInvoicePdfToExcel.VendorImplementations.SheetalBatra import SheetalBatra
from VendorsInvoicePdfToExcel.VendorImplementations.SkbRetailPvtLtd import SkbRetailPvtLtd


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
        elif implementation == "masaba":
            return Masaba(tables, text_data, table_by_tabula)
        elif implementation == "saaksha_and_kinni":
            return SaakshaAndKinni(tables, text_data, table_by_tabula)
        elif implementation == "ruhaan":
            return Ruhaan(tables, text_data, table_by_tabula)
        elif implementation == "riyaasat":
            return Riyaasat(tables, text_data, table_by_tabula)
        elif implementation == "monk_and_mei":
            return MonkAndMei(tables, text_data, table_by_tabula)
        elif implementation == "espana":
            return Espana(tables, text_data, table_by_tabula)
        elif implementation == "kasbah_clothing":
            return KasbahClothing(tables, text_data, table_by_tabula)
        elif implementation == "fatiz":
            return Fatiz(tables, text_data, table_by_tabula)
        elif implementation == "amyra":
            return Amyra(tables, text_data, table_by_tabula)
        elif implementation == "skb_retail_pvt_ltd":
            return SkbRetailPvtLtd(tables, text_data, table_by_tabula)
        elif implementation == "rn_fashion":
            return RnFashion(tables, text_data, table_by_tabula)
        elif implementation == "mrunalini_rao":
            return MrunaliniRao(tables, text_data, table_by_tabula)
        elif implementation == "couture_by_niharika":
            return CoutureByNiharika(tables, text_data, table_by_tabula)
        else:
            raise HTTPException(status_code=404, detail="Item not found")