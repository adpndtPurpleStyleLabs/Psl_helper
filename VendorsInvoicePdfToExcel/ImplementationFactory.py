from VendorsInvoicePdfToExcel.VendorImplementations.AbkasaDesignerApparelsPvtLtd import AbkasaDesignerApparelsPvtLtd
from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.AmitArrora import AmitArrora
from VendorsInvoicePdfToExcel.VendorImplementations.AmrtiDawani import AmrtiDawani
from VendorsInvoicePdfToExcel.VendorImplementations.AneeshAgarwaal import AneeshAgarwaal
from VendorsInvoicePdfToExcel.VendorImplementations.Artimen import Artimen
from VendorsInvoicePdfToExcel.VendorImplementations.BasilLeaf import BasilLeaf
from VendorsInvoicePdfToExcel.VendorImplementations.ChaashniByMaansiAndKetan import ChaashniByMaansiAndKetan
from VendorsInvoicePdfToExcel.VendorImplementations.CharuAndVasundhara import CharuAndVasundhara
from VendorsInvoicePdfToExcel.VendorImplementations.CosaNostraa import CosaNostraa
from VendorsInvoicePdfToExcel.VendorImplementations.CoutureByNiharika import CoutureByNiharika
from VendorsInvoicePdfToExcel.VendorImplementations.Crimzon import Crimzon
from VendorsInvoicePdfToExcel.VendorImplementations.DollyJ import DollyJ
from VendorsInvoicePdfToExcel.VendorImplementations.Fatiz import Fatiz
from VendorsInvoicePdfToExcel.VendorImplementations.IkshitaChoudhary import IkshitaChoudhary
from VendorsInvoicePdfToExcel.VendorImplementations.IshaGuptaTayal import IshaGuptaTayal
from VendorsInvoicePdfToExcel.VendorImplementations.JoulesByRadhika import JoulesByRadhika
from VendorsInvoicePdfToExcel.VendorImplementations.Kalista import Kalista
from VendorsInvoicePdfToExcel.VendorImplementations.KharaKapas import KharaKapas
from VendorsInvoicePdfToExcel.VendorImplementations.KkarmaAccessories import KkarmaAccessories
from VendorsInvoicePdfToExcel.VendorImplementations.Lashkaraa import Lashkaraa
from VendorsInvoicePdfToExcel.VendorImplementations.MrunaliniRao import MrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.PaulmiAndHarsh import PaulmiAndHarsh
from VendorsInvoicePdfToExcel.VendorImplementations.Prisho import Prisho
from VendorsInvoicePdfToExcel.VendorImplementations.ReneeLabel import ReneeLabel
from VendorsInvoicePdfToExcel.VendorImplementations.SaakshaAndKinni import SaakshaAndKinni
from VendorsInvoicePdfToExcel.VendorImplementations.SahilAnejaCouture import SahilAnejaCouture
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
from VendorsInvoicePdfToExcel.VendorImplementations.LinenBloomMen import LinenBloomMen
from VendorsInvoicePdfToExcel.VendorImplementations.Samohan import Samohan
from VendorsInvoicePdfToExcel.VendorImplementations.Masaba import Masaba
from VendorsInvoicePdfToExcel.VendorImplementations.Ruhaan import Ruhaan
from VendorsInvoicePdfToExcel.VendorImplementations.Riyaasat import Riyaasat
from VendorsInvoicePdfToExcel.VendorImplementations.MonkAndMei import MonkAndMei
from VendorsInvoicePdfToExcel.VendorImplementations.Amyra import Amyra
from VendorsInvoicePdfToExcel.VendorImplementations.Order.RnFashion import RnFashion as OrderRnFashion
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.RnFashion import RnFashion as OutrightRnFashion
from VendorsInvoicePdfToExcel.VendorImplementations.Order.Ruhaan import Ruhaan as OrderRuhaan
from VendorsInvoicePdfToExcel.VendorImplementations.Order.SkbRetailPvtLtd import SkbRetailPvtLtd as OrderSkbRetailPvtLtd
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.AnushreeReddyWorld import AnushreeReddyWorld as OutrightAnushreeReddyWorld
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.SeemaGujral import SeemaGujral as OutrightSeemaGujral
from VendorsInvoicePdfToExcel.VendorImplementations.Order.Espana import Espana as OrderEspana
from VendorsInvoicePdfToExcel.VendorImplementations.Order.KasbahClothing import KasbahClothing as OrderKasbahClothing
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.MrunaliniRao import MrunaliniRao as OutrightMrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.Order.Masaba import Masaba as OrderMasaba
from VendorsInvoicePdfToExcel.VendorImplementations.Order.AnushreeReddyWorld import AnushreeReddyWorld as OrderAnushreeReddyWorld
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.Ruhaan import Ruhaan as OutrightRuhaan
from VendorsInvoicePdfToExcel.VendorImplementations.Outright.Espana import Espana as OutrightEspana
from VendorsInvoicePdfToExcel.VendorImplementations.Order.MrunaliniRao import MrunaliniRao as OrderMrunaliniRao
from VendorsInvoicePdfToExcel.VendorImplementations.Order.SeemaGujral import SeemaGujral as OrderSeemaGujral

from fastapi import HTTPException

from VendorsInvoicePdfToExcel.VendorImplementations.SheetalBatra import SheetalBatra


class ImplementationFactory:
    def getImplementation(self, implementation, tables, text_data, table_by_tabula, poType):
        self.implementations = {
            "amit_agarwal": AmitAgarwal,
            # "seema_gujral_creations_llp": SeemaGujral,
            "sheetal_batra": SheetalBatra,
            # "lashkaraa": Lashkaraa,
            "paulmi_and_harsh": PaulmiAndHarsh,
            "linen_bloom_men": LinenBloomMen,
            "sammohan": Samohan,
            "saaksha_and_kinni": SaakshaAndKinni,
            "ruhaan_international_private_limited_OR": Ruhaan,
            "riyaasat": Riyaasat,
            "monk_and_mei": MonkAndMei,
            "fatiz": Fatiz,
            "amyra": Amyra,
            # "r_n_fashion": RnFashion,
            "mrunalini_rao_arts_and_design": MrunaliniRao,
            "couture_by_niharika": CoutureByNiharika,
            "dolly_j": DollyJ,
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

            # New Keys
            "anushree_reddy_world_llp_outright": OutrightAnushreeReddyWorld,
            "r_n_fashion_outright": OutrightRnFashion,
            "seema_gujral_creations_llp_outright": OutrightSeemaGujral,
            "mrunalini_rao_arts_and_design_outright": OutrightMrunaliniRao,
            "ruhaan_international_private_limited_outright" : OutrightRuhaan,
            "ms_espana_tex_outright": OutrightEspana,

            "ruhaan_international_private_limited_order": OrderRuhaan,
            "r_n_fashion_order": OrderRnFashion,
            "skb_retail_india_private_limited_order": OrderSkbRetailPvtLtd,
            "ms_espana_tex_order": OrderEspana,
            "kasbah_clothing_order": OrderKasbahClothing,
            "ms_house_of_masaba_lifestyle_private_limited_order": OrderMasaba,
            "anushree_reddy_world_llp_order" : OrderAnushreeReddyWorld,
            "mrunalini_rao_arts_and_design_order": OrderMrunaliniRao,
            "seema_gujral_creations_llp_order": OrderSeemaGujral
        }
        implementation = (str(implementation).strip().lower()
                          .replace(' ', "_")
                          .replace(".","")
                          .replace("/","")) +"_"+ poType.strip().lower()
        implementation_class = self.implementations.get(implementation)

        if implementation_class:
            return implementation_class(tables, text_data,
                                        table_by_tabula) if "table_by_tabula" in implementation_class.__init__.__code__.co_varnames else implementation_class(
                tables, text_data)

        raise HTTPException(status_code=404, detail="Item not found")

