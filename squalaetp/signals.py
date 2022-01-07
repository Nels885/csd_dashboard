import re
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Sivin, Xelon, ProductCategory
from psa.models import Corvet, Ecu, Multimedia
from utils.django.validators import comp_ref_isvalid


def product_update(instance):
    corvet, product = instance.corvet, instance.product
    if corvet and product:
        ecu_dict = {
            "NAV": corvet.electronique_14x, "RAD": corvet.electronique_14f,
            "EMF": corvet.electronique_14l, "CMB": corvet.electronique_14k, "BSI": corvet.electronique_14b,
            "CMM": corvet.electronique_14a, "HDC": corvet.electronique_16p, "BSM": corvet.electronique_16b
        }
        for corvet_type, comp_ref in ecu_dict.items():
            if product.corvet_type == corvet_type and comp_ref_isvalid(comp_ref):
                if product.corvet_type in ["NAV", "RAD"]:
                    obj, created = Multimedia.objects.get_or_create(
                        hw_reference=comp_ref,
                        defaults={'xelon_name': instance.modele_produit, 'type': product.corvet_type})
                else:
                    obj, created = Ecu.objects.get_or_create(
                        comp_ref=comp_ref,
                        defaults={'xelon_name': instance.modele_produit, 'type': product.corvet_type}
                    )
                if not created:
                    obj.xelon_name = instance.modele_produit
                    obj.save()
                break


@receiver(pre_save, sender=Sivin)
def pre_save_sivin(sender, instance, **kwargs):
    try:
        if re.match(r'^[VWZ][FLR0]\w{15}$', str(instance.codif_vin)):
            instance.corvet = Corvet.objects.get(vin=instance.codif_vin)
    except Corvet.DoesNotExist as err:
        print(f"DoesNotExist: {instance} => {err}")


@receiver(pre_save, sender=Xelon)
def pre_save_xelon(sender, instance, **kwargs):
    try:
        if re.match(r'^[VWZ][FLR0]\w{15}$', str(instance.vin)):
            instance.corvet = Corvet.objects.get(vin=instance.vin)
            instance.vin_error = False
        if instance.modele_produit:
            instance.product, created = ProductCategory.objects.get_or_create(product_model=instance.modele_produit)
        product_update(instance)
    except Corvet.DoesNotExist:
        instance.corvet = None
