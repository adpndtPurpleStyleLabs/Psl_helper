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
from VendorsInvoicePdfToExcel.VendorImplementations.CosaNostraa import CosaNostraa
from VendorsInvoicePdfToExcel.VendorImplementations.CoutureByNiharika import CoutureByNiharika
from VendorsInvoicePdfToExcel.VendorImplementations.Crimzon import Crimzon
from VendorsInvoicePdfToExcel.VendorImplementations.DollyJ import DollyJ
from VendorsInvoicePdfToExcel.VendorImplementations.Espana import Espana
from VendorsInvoicePdfToExcel.VendorImplementations.Fatiz import Fatiz
from VendorsInvoicePdfToExcel.VendorImplementations.IkshitaChoudhary import IkshitaChoudhary
from VendorsInvoicePdfToExcel.VendorImplementations.IshaGuptaTayal import IshaGuptaTayal
from VendorsInvoicePdfToExcel.VendorImplementations.JoulesByRadhika import JoulesByRadhika
from VendorsInvoicePdfToExcel.VendorImplementations.Kalista import Kalista
from VendorsInvoicePdfToExcel.VendorImplementations.KasbahClothing import KasbahClothing
from VendorsInvoicePdfToExcel.VendorImplementations.KharaKapas import KharaKapas
from VendorsInvoicePdfToExcel.VendorImplementations.KkarmaAccessories import KkarmaAccessories
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.MrunaliniRao import MrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.PaulmiAndHarsh import PaulmiAndHarsh
from VendorsInvoicePdfToExcel.VendorImplementations.Prisho import Prisho
from VendorsInvoicePdfToExcel.VendorImplementations.ReneeLabel import ReneeLabel
from VendorsInvoicePdfToExcel.VendorImplementations.RnFashion import RnFashion
from VendorsInvoicePdfToExcel.VendorImplementations.SaakshaAndKinni import SaakshaAndKinni
from VendorsInvoicePdfToExcel.VendorImplementations.SahilAnejaCouture import SahilAnejaCouture
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
# from VendorsInvoicePdfToExcel.VendorImplementations.Kalighata import Kalighata
from VendorsInvoicePdfToExcel.VendorImplementations.LinenBloomMen import LinenBloomMen
from VendorsInvoicePdfToExcel.VendorImplementations.Samohan import Samohan
from VendorsInvoicePdfToExcel.VendorImplementations.Masaba import Masaba
from VendorsInvoicePdfToExcel.VendorImplementations.Ruhaan import Ruhaan
from VendorsInvoicePdfToExcel.VendorImplementations.Riyaasat import Riyaasat
from VendorsInvoicePdfToExcel.VendorImplementations.MonkAndMei import MonkAndMei
from VendorsInvoicePdfToExcel.VendorImplementations.Amyra import Amyra
from VendorsInvoicePdfToExcel.VendorImplementations.Ruhaan_CUST import Ruhaan_CUST
from fastapi import HTTPException

from VendorsInvoicePdfToExcel.VendorImplementations.SheetalBatra import SheetalBatra
from VendorsInvoicePdfToExcel.VendorImplementations.SkbRetailPvtLtd import SkbRetailPvtLtd


class ImplementationFactory:
    def getImplementation(self, implementation, tables, text_data, table_by_tabula):
        self.implementations = {
            "amit_agarwal": AmitAgarwal,
            "seema_gujral": SeemaGujral,
            "sheetal_batra": SheetalBatra,
            "lashkaraa": Lashkaraa,
            "paulmi_and_harsh": PaulmiAndHarsh,
            "linen_bloom_men": LinenBloomMen,
            "sammohan": Samohan,
            "masaba": Masaba,
            "saaksha_and_kinni": SaakshaAndKinni,
            "ruhaan_international_private_limited_OR": Ruhaan,
            "riyaasat": Riyaasat,
            "monk_and_mei": MonkAndMei,
            "espana": Espana,
            "kasbah_clothing": KasbahClothing,
            "fatiz": Fatiz,
            "amyra": Amyra,
            "skb_retail_india_private_limited": SkbRetailPvtLtd,
            "r._n._fashion": RnFashion,
            "mrunalini_rao": MrunaliniRao,
            "couture_by_niharika": CoutureByNiharika,
            "dolly_j": DollyJ,
            "anushree_reddy_world_llp": AnushreeReddyWorld,
            "sahil_aneja_couture": SahilAnejaCouture,
            "abkasa_designer_apparels_pvt_ltd": AbkasaDesignerApparelsPvtLtd,
            "aneesh_agarwaal": AneeshAgarwaal,
            "amit_arrora": AmitArrora,
            "amrti_dawani": AmrtiDawani,
            "chaashni_by_maansi_and_ketan": ChaashniByMaansiAndKetan,
            "artimen": Artimen,
            "basil_leaf": BasilLeaf,
            "charu_and_asundhara": CharuAndVasundhara,
            "cosa_nostraa": CosaNostraa,
            "crimzon": Crimzon,
            "ikshita_choudhary": IkshitaChoudhary,
            "isha_gupta_tayal": IshaGuptaTayal,
            "joules_by_radhika": JoulesByRadhika,
            "khara_kapas": KharaKapas,
            "kalista": Kalista,
            "kkarma_accessories": KkarmaAccessories,
            "prisho": Prisho,
            "renee_label": ReneeLabel,
            "ruhaan_international_private_limited": Ruhaan_CUST
        }

        implementation = str(implementation).strip().lower().replace(' ', "_")
        implementation_class = self.implementations.get(implementation)

        if implementation_class:
            # Instantiate with required arguments
            return implementation_class(tables, text_data,
                                        table_by_tabula) if "table_by_tabula" in implementation_class.__init__.__code__.co_varnames else implementation_class(
                tables, text_data)

        raise HTTPException(status_code=404, detail="Item not found")

