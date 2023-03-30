from utils.django.urls import reverse

from squalaetp.models import Xelon, Sivin
from psa.models import Corvet
from reman.models import Repair


def global_search(query, select):
    if query and select:

        if select == 'reman':
            # Repair search
            repairs = Repair.search(query)
            if repairs:
                if len(repairs) > 1:
                    return reverse('reman:repair_table', get={'filter': query})
                return reverse('reman:detail_repair', kwargs={'pk': repairs.first().pk})

        # Sivins search
        sivins = Sivin.search(query)
        if sivins:
            query = sivins.first().codif_vin

        if select == 'repair':
            # Xelon search
            xelons = Xelon.search(query)
            if xelons:
                if len(xelons) > 1:
                    return reverse('squalaetp:xelon', get={'filter': query})
                return reverse('squalaetp:detail', kwargs={'pk': xelons.first().pk})

        # Corvet search
        corvets = Corvet.search(query)
        if corvets and select != 'sivin':
            if len(corvets) > 1:
                return reverse('psa:corvet', get={'filter': query})
            return reverse('psa:corvet_detail', kwargs={'pk': corvets.first().pk})
        if sivins:
            return reverse('squalaetp:sivin_detail', kwargs={'immat': sivins.first().immat_siv})
    return None
