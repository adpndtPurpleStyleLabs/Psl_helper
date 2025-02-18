from VendorsInvoicePdfToExcel.VendorImplementations.AbkasaDesignerApparelsPvtLtd import AbkasaDesignerApparelsPvtLtd
from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.AmitArrora import AmitArrora
from VendorsInvoicePdfToExcel.VendorImplementations.AmrtiDawani import AmrtiDawani
from VendorsInvoicePdfToExcel.VendorImplementations.AneeshAgarwaal import AneeshAgarwaal
from VendorsInvoicePdfToExcel.VendorImplementations.AnushreeReddyWorld import AnushreeReddyWorld
from VendorsInvoicePdfToExcel.VendorImplementations.Artimen import Artimen
from VendorsInvoicePdfToExcel.VendorImplementations.BasilLeaf import BasilLeaf
from VendorsInvoicePdfToExcel.VendorImplementations.ChaashniByMaansiAndKetan import ChaashniByMaansiAndKetan
from VendorsInvoicePdfToExcel.VendorImplementations.CharuAndVasundhara import CharuAndVasundhara
from VendorsInvoicePdfToExcel.VendorImplementations.CoutureByNiharika import CoutureByNiharika
from VendorsInvoicePdfToExcel.VendorImplementations.DollyJ import DollyJ
from VendorsInvoicePdfToExcel.VendorImplementations.Espana import Espana
from VendorsInvoicePdfToExcel.VendorImplementations.Fatiz import Fatiz
from VendorsInvoicePdfToExcel.VendorImplementations.KasbahClothing import KasbahClothing
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.MrunaliniRao import MrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.PaulmiAndHarsh import PaulmiAndHarsh
from VendorsInvoicePdfToExcel.VendorImplementations.RnFashion import RnFashion
from VendorsInvoicePdfToExcel.VendorImplementations.SaakshaAndKinni import SaakshaAndKinni
from VendorsInvoicePdfToExcel.VendorImplementations.SahilAnejaCouture import SahilAnejaCouture
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
        elif implementation == "dolly_j":
            return DollyJ(tables, text_data, table_by_tabula)
        elif implementation == "anushree_reddy_world":
            return AnushreeReddyWorld(tables, text_data, table_by_tabula)
        elif implementation == "sahil_aneja_couture":
            return SahilAnejaCouture(tables, text_data, table_by_tabula)
        elif implementation == "abkasa_designer_apparels_pvt_ltd":
            return AbkasaDesignerApparelsPvtLtd(tables, text_data, table_by_tabula)
        elif implementation == "aneesh_agarwaal":
            return AneeshAgarwaal(tables, text_data, table_by_tabula)
        elif implementation == "amit_arrora":
            return AmitArrora(tables, text_data, table_by_tabula)
        elif implementation == "amrti_dawani":
            return AmrtiDawani(tables, text_data, table_by_tabula)
        elif implementation == "chaashni_by_maansi_and_ketan":
            return ChaashniByMaansiAndKetan(tables, text_data, table_by_tabula)
        elif implementation == "artimen":
            return Artimen(tables, text_data, table_by_tabula)
        elif implementation == "basil_leaf":
            return BasilLeaf(tables, text_data, table_by_tabula)
        elif implementation == "charu_and_asundhara":
            return CharuAndVasundhara(tables, text_data, table_by_tabula)
        else:
            raise HTTPException(status_code=404, detail="Item not found")