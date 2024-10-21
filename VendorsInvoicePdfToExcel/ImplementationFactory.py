from VendorsInvoicePdfToExcel.VendorImplementations.AmitAgarwal import AmitAgarwal
from VendorsInvoicePdfToExcel.VendorImplementations.SeemaGujral import SeemaGujral
from fastapi import HTTPException


class ImplementationFactory:
    def getImplementation(self, implementation, tables, text_data):
        implementation = str(implementation).lower().replace(' ',"")
        if  implementation == "amit_garwal":
            return AmitAgarwal(tables, text_data)
        elif implementation == "seema_gujral":
            return SeemaGujral(tables, text_data)
        else:
            raise HTTPException(status_code=404, detail="Item not found")