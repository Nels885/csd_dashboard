import re
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Sivin, Xelon, ProductCategory
from psa.models import Corvet, Ecu, Multimedia


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
    #         product = instance.product
    #         if product and product.corvet_type in ["NAV", "RAD"]:
    #             if product.corvet_type == "NAV":
    #                 comp_ref = instance.corvet.electronique_14x
    #             else:
    #                 comp_ref = instance.corvet.electronique_14f
    #             if comp_ref.isdigit():
    #                 Multimedia.objects.get_or_create(
    #                     hw_reference=comp_ref,
    #                     defaults={'xelon_name': instance.modele_produit, 'type': product.corvet_type})
    #         if product and product.corvet_type in ["EMF", "CMB", "BSI", "CMM", "HDC", "BSM"]:
    #             comp_ref = None
    #             if product.corvet_type == "EMF":
    #                 comp_ref = instance.corvet.electronique_14l
    #             elif product.corvet_type == "CMB":
    #                 comp_ref = instance.corvet.electronique_14k
    #             elif product.corvet_type == "BSI":
    #                 comp_ref = instance.corvet.electronique_14b
    #             elif product.corvet_type == "CMM":
    #                 comp_ref = instance.corvet.electronique_14a
    #             elif product.corvet_type == "HDC":
    #                 comp_ref = instance.corvet.electronique_16p
    #             elif product.corvet_type == "BSM":
    #                 comp_ref = instance.corvet.electronique_16b
    #             if comp_ref and comp_ref.isdigit():
    #                 Ecu.objects.get_or_create(
    #                     comp_ref=comp_ref,
    #                     defaults={'xelon_name': instance.modele_produit, 'type': product.corvet_type}
    #                 )
    # except ProductCategory.DoesNotExist:
    #     instance.product = None
    except Corvet.DoesNotExist:
        instance.corvet = None
