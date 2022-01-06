from django.db import models


class SemRefBase(models.Model):
    reman_reference = models.CharField("référence REMAN", max_length=10, unique=True)
    map_data = models.CharField("map data", max_length=100, blank=True)
    oe_reference = models.CharField("product part", max_length=8, blank=True)
    pf_code = models.CharField("PF code", max_length=10, blank=True)
    asm = models.CharField("ASM", max_length=12, blank=True)
    hw = models.CharField("HW", max_length=12, blank=True)

