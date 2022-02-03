from django.db import models


class SemType(models.Model):
    asm_reference = models.CharField("ASM", max_length=12, unique=True)
    hw_reference = models.CharField("HW", max_length=12)
    technical_data = models.CharField("modèle produit", max_length=50, default="SEM")
    supplier_oe = models.CharField("fabriquant", max_length=50, default="PARROT")

    def __str__(self):
        return "ASM_{} - HW_{}".format(self.asm_reference, self.hw_reference)


class SemModel(models.Model):
    pf_code_oe = models.CharField("PF code OE", max_length=10, unique=True)
    pi_code_oe = models.CharField("PI code OE", max_length=10)
    sam_oe = models.CharField("Production part", max_length=12, blank=True)
    vehicle = models.CharField("Vehicule", max_length=50, blank=True)
    core_part = models.CharField("Core part", max_length=50, blank=True)
    fan = models.CharField('FAN', max_length=100, blank=True)
    rear_bolt = models.CharField('REAR BOLT', max_length=100, blank=True)
    hw_oe = models.CharField("HW P/N", max_length=12, blank=True)
    ecu_type = models.ForeignKey("SemType", on_delete=models.SET_NULL, null=True, blank=True)

    def __iter__(self):
        for field in self._meta.fields:
            yield field.verbose_name.capitalize(), field.value_to_string(self)

    def __str__(self):
        return "PF_code_{} - ASM_OE_{}".format(self.pf_code_oe, self.sam_oe)


class SemRefBase(models.Model):
    reman_reference = models.CharField("référence REMAN", max_length=10, unique=True)
    brand = models.CharField("Marque", max_length=50, blank=True)
    map_data = models.CharField("map data", max_length=100, blank=True)
    product_part = models.CharField("product part", max_length=8, blank=True)
    pf_code = models.CharField("PF code REMAN", max_length=10, blank=True)
    ecu_type = models.ForeignKey("SemType", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.reman_reference
