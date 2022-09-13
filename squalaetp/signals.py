import re
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Sivin, Xelon, XelonTemporary, ProductCategory
from psa.models import Corvet, Ecu, Multimedia
from utils.django.validators import comp_ref_isvalid, VIN_PSA_REGEX
from utils.django.decorators import disable_for_loaddata


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
                        comp_ref=comp_ref,
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
@disable_for_loaddata
def pre_save_sivin(sender, instance, **kwargs):
    try:
        if not instance.corvet and re.match(VIN_PSA_REGEX, str(instance.codif_vin)):
            instance.corvet = Corvet.objects.get(vin=instance.codif_vin)
    except Corvet.DoesNotExist:
        instance.corvet = None


@receiver(pre_save, sender=Xelon)
@disable_for_loaddata
def pre_save_xelon(sender, instance, **kwargs):
    try:
        if re.match(VIN_PSA_REGEX, str(instance.vin)):
            instance.corvet = Corvet.objects.get(vin=instance.vin)
            instance.vin_error = False
    except Corvet.DoesNotExist:
        instance.corvet = None
    finally:
        if instance.modele_produit:
            instance.product, created = ProductCategory.objects.get_or_create(product_model=instance.modele_produit)
            if "ZONECE" in instance.lieu_de_stockage:
                instance.product.category = "ETUDE"
                instance.product.save()
            product_update(instance)
        if instance.date_expedition_attendue and isinstance(instance.date_expedition_attendue, timezone.datetime):
            try:
                instance.delai_expedition_attendue = (timezone.now().date() - instance.date_expedition_attendue).days
            except TypeError:
                instance.delai_expedition_attendue = (timezone.now() - instance.date_expedition_attendue).days


@receiver(pre_save, sender=XelonTemporary)
@disable_for_loaddata
def pre_save_xelon_temporary(sender, instance, **kwargs):
    try:
        if re.match(VIN_PSA_REGEX, str(instance.vin)):
            instance.corvet = Corvet.objects.get(vin=instance.vin)
    except Corvet.DoesNotExist:
        instance.corvet = None
