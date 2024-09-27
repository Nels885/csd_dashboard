from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.django.decorators import disable_for_loaddata
from .models import CorvetProduct, Corvet, Multimedia, Ecu, CorvetOption
from squalaetp.models import Xelon, Sivin


@receiver(post_save, sender=Corvet)
@disable_for_loaddata
def post_save_corvet(sender, created, instance, **kwargs):
    default = {}
    if instance.electronique_14x.isdigit():
        default.update({"btel": Multimedia.objects.filter(comp_ref__startswith=instance.electronique_14x).first()})
    if instance.electronique_1m2.isdigit():
        default.update({"ivi": Multimedia.objects.filter(comp_ref__startswith=instance.electronique_1m2).first()})
    if instance.electronique_14f.isdigit():
        default.update({"radio": Multimedia.objects.filter(comp_ref__startswith=instance.electronique_14f).first()})
    if instance.electronique_14b.isdigit():
        default.update({"bsi": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14b, type='BSI').first()})
    if instance.electronique_1k4.isdigit():
        default.update({"vsm1": Ecu.objects.filter(comp_ref__startswith=instance.electronique_1k4, type='VSM1').first()})
    if instance.electronique_14l.isdigit():
        default.update({"emf": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14l, type='EMF').first()})
    if instance.electronique_14a.isdigit():
        default.update({"cmm": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14a, type='CMM').first()})
    if instance.electronique_16b.isdigit():
        default.update({"bsm": Ecu.objects.filter(comp_ref__startswith=instance.electronique_16b, type='BSM').first()})
    if instance.electronique_16p.isdigit():
        default.update({"hdc": Ecu.objects.filter(comp_ref__startswith=instance.electronique_16p, type='HDC').first()})
    if instance.electronique_14k.isdigit():
        default.update({"cmb": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14k, type='CMB').first()})
    if instance.electronique_19z.isdigit():
        default.update({"fmux": Ecu.objects.filter(comp_ref__startswith=instance.electronique_19z, type='FMUX').first()})
    if instance.electronique_19h.isdigit():
        default.update({"mds": Ecu.objects.filter(comp_ref__startswith=instance.electronique_19h, type='MDS').first()})
    if instance.electronique_12y.isdigit():
        default.update({"cvm2": Ecu.objects.filter(comp_ref__startswith=instance.electronique_12y, type='CVM2').first()})
    if instance.electronique_11m.isdigit():
        default.update({"vmf": Ecu.objects.filter(comp_ref__startswith=instance.electronique_11m, type='VMF').first()})
    if instance.electronique_11q.isdigit():
        default.update({"dmtx": Ecu.objects.filter(comp_ref__startswith=instance.electronique_11q, type='DMTX').first()})
    if instance.electronique_11n.isdigit():
        default.update({"bpga": Ecu.objects.filter(comp_ref__startswith=instance.electronique_11n, type='BPGA').first()})
    if instance.electronique_14r.isdigit():
        default.update({"aas": Ecu.objects.filter(comp_ref__startswith=instance.electronique_14r, type='AAS').first()})
    CorvetProduct.objects.update_or_create(corvet=instance, defaults=default)
    Xelon.objects.filter(vin=instance.vin).update(corvet=instance)
    Sivin.objects.filter(codif_vin=instance.vin).update(corvet=instance)
    if created:
        CorvetOption.objects.get_or_create(corvet=instance)


@receiver(post_save, sender=Multimedia)
@disable_for_loaddata
def post_save_multimedia(sender, created, instance, **kwargs):
    CorvetProduct.objects.filter(corvet__electronique_14x__exact=instance.comp_ref).update(btel=instance.pk)
    CorvetProduct.objects.filter(corvet__electronique_14f__exact=instance.comp_ref).update(radio=instance.pk)
    CorvetProduct.objects.filter(corvet__electronique_1m2__exact=instance.comp_ref).update(ivi=instance.pk)


@receiver(post_save, sender=Ecu)
@disable_for_loaddata
def post_save_ecu(sender, created, instance, **kwargs):
    if instance.type == "BSI":
        CorvetProduct.objects.filter(corvet__electronique_14b__startswith=instance.comp_ref).update(bsi=instance.pk)
    if instance.type == "VSM1":
        CorvetProduct.objects.filter(corvet__electronique_1k4__startswith=instance.comp_ref).update(vsm1=instance.pk)
    if instance.type == "BSM":
        CorvetProduct.objects.filter(corvet__electronique_16b__startswith=instance.comp_ref).update(bsm=instance.pk)
    if instance.type == "CMB":
        CorvetProduct.objects.filter(corvet__electronique_14k__startswith=instance.comp_ref).update(cmb=instance.pk)
    if instance.type == "CMM":
        CorvetProduct.objects.filter(corvet__electronique_14a__startswith=instance.comp_ref).update(cmm=instance.pk)
    if instance.type == "EMF":
        CorvetProduct.objects.filter(corvet__electronique_14l__startswith=instance.comp_ref).update(emf=instance.pk)
    if instance.type == "FMUX":
        CorvetProduct.objects.filter(corvet__electronique_19z__startswith=instance.comp_ref).update(fmux=instance.pk)
    if instance.type == "HDC":
        CorvetProduct.objects.filter(corvet__electronique_16p__startswith=instance.comp_ref).update(hdc=instance.pk)
    if instance.type == "MDS":
        CorvetProduct.objects.filter(corvet__electronique_19h__startswith=instance.comp_ref).update(mds=instance.pk)
    if instance.type == "CVM2":
        CorvetProduct.objects.filter(corvet__electronique_12y__startswith=instance.comp_ref).update(cvm2=instance.pk)
    if instance.type == "VMF":
        CorvetProduct.objects.filter(corvet__electronique_11m__startswith=instance.comp_ref).update(vmf=instance.pk)
    if instance.type == "DMTX":
        CorvetProduct.objects.filter(corvet__electronique_11q__startswith=instance.comp_ref).update(dmtx=instance.pk)
    if instance.type == "BPGA":
        CorvetProduct.objects.filter(corvet__electronique_11n__startswith=instance.comp_ref).update(bpga=instance.pk)
    if instance.type == "AAS":
        CorvetProduct.objects.filter(corvet__electronique_14r__startswith=instance.comp_ref).update(aas=instance.pk)
