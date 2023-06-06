from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode import code128

from psa.templatetags.corvet_tags import get_corvet


class CorvetBarcode:
    NOP = 'N/A'

    def __init__(self, *args, **kwargs):
        self.xelonNumber = kwargs.get('xelon_number', self.NOP)
        self.xelonModel = kwargs.get('xelon_model', self.NOP)
        self.xelonVehicle = kwargs.get('xelon_vehicle', self.NOP)
        self.vin = kwargs.get('vin', self.NOP)
        self.brand = kwargs.get('brand', self.NOP)
        self.corvet = kwargs.get('corvet')
        if self.corvet:
            self.vin = self.corvet.vin
        self.hwRef = self.swRef = self.NOP

    def result(self):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p = self._footer(self._middle(self._header(self._title(p))))
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    def _title(self, p):
        if self.xelonNumber != self.NOP:
            p.setTitle(f"xelon_{self.xelonNumber}")
        elif self.vin != self.NOP:
            p.setTitle(f"vin_{self.vin}")
        else:
            p.setTitle("corvet_barcode")
        p.setLineWidth(4)
        return p

    def _header(self, p):
        p.setFont('Courier', 15)
        p.drawString(50, 700, "N° Xelon :")
        p.drawString(50, 600, "V.I.N. :")
        p.line(50, 535, 550, 535)

        p.setFont('Courier-Bold', 15)

        p.drawString(250, 700, str(self.xelonNumber))
        if self.xelonNumber != self.NOP:
            barcode = code128.Code128(str(self.xelonNumber), barWidth=0.5 * mm, barHeight=10 * mm)
            barcode.drawOn(p, 200, 660)
        p.drawString(250, 600, str(self.vin))
        if self.vin != self.NOP:
            barcode = code128.Code128(str(self.vin), barWidth=0.5 * mm, barHeight=10 * mm)
            barcode.drawOn(p, 170, 560)
        return p

    def _middle(self, p):
        p.setFont('Courier', 15)
        p.drawString(50, 500, "Marque :")
        p.drawString(50, 450, "Modèle véhicule :")
        p.drawString(50, 400, "Modèle produit :")
        p.line(50, 355, 550, 355)

        p.setFont('Courier-Bold', 15)
        if self.corvet:
            if self.corvet.donnee_marque_commerciale == "OP":
                vehicle = get_corvet(self.corvet.donnee_ligne_de_produit, "DON_LIN_PROD 0")
            else:
                vehicle = get_corvet(self.corvet.donnee_ligne_de_produit, "DON_LIN_PROD 1")
            p.drawString(250, 450, str(vehicle))
            p.drawString(250, 500, str(get_corvet(self.corvet.donnee_marque_commerciale, "DON_MAR_COMM")))
            if self.corvet.electronique_94x:
                media = self.corvet.prods.btel
                self.hwRef = self.corvet.electronique_14x
                self.swRef = self.corvet.electronique_94x
            else:
                media = self.corvet.prods.radio
                self.hwRef = self.corvet.electronique_14f
                self.swRef = self.corvet.electronique_94f
            try:
                p.drawString(250, 400, str(media.get_name_display()))
                if media.level:
                    p.drawString(400, 400, str(media.level))
            except AttributeError:
                p.drawString(250, 400, str(self.xelonModel))
        else:
            p.drawString(250, 450, str(self.xelonVehicle))
            p.drawString(250, 500, self.NOP)
            p.drawString(250, 400, str(self.xelonModel))
        return p

    def _footer(self, p):
        p.setFont('Courier', 15)
        p.line(50, 355, 550, 355)
        p.drawString(50, 300, "Réf. boitier :")
        p.drawString(50, 200, "Cal. CORVET :")

        p.setFont('Courier-Bold', 15)
        p.drawString(250, 300, str(self.hwRef))
        if self.hwRef != self.NOP:
            barcode = code128.Code128(str(self.hwRef), barWidth=0.5 * mm, barHeight=10 * mm)
            barcode.drawOn(p, 210, 260)
        p.drawString(250, 200, str(self.swRef))
        if self.swRef != self.NOP:
            barcode = code128.Code128(str(self.swRef), barWidth=0.5 * mm, barHeight=10 * mm)
            barcode.drawOn(p, 210, 160)
        return p
