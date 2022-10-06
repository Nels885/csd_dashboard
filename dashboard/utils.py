from utils.django.urls import reverse

from squalaetp.models import Xelon, Sivin
from psa.models import Corvet


def global_search(query, select):
    if query and select:
        sivins = Sivin.search(query)
        if sivins:
            query = sivins.first().codif_vin
        xelons = Xelon.search(query)
        corvets = Corvet.search(query)
        if xelons and select == 'atelier':
            if len(xelons) > 1:
                return reverse('squalaetp:xelon', get={'filter': query})
            return reverse('squalaetp:detail', kwargs={'pk': xelons.first().pk})
        elif corvets:
            if len(corvets) > 1:
                return reverse('psa:corvet', get={'filter': query})
            return reverse('psa:corvet_detail', kwargs={'pk': corvets.first().pk})
        elif sivins:
            return reverse('squalaetp:sivin_detail', kwargs={'immat': sivins.first().immat_siv})

    # if query and select:
    #     if Sivin.search(query):
    #         query = Sivin.search(query).first().codif_vin
    #     if query and select == 'atelier':
    #         files = Xelon.search(query)
    #         if files:
    #             messages.success(request, _(f'Success: The reseach for {query} was successful.'))
    #             if len(files) > 1:
    #                 return redirect(reverse('squalaetp:xelon', get={'filter': query}))
    #             return redirect('squalaetp:detail', pk=files.first().pk)
    #     elif query and select == 'sivin':
    #         sivins = Sivin.search(query)
    #         if sivins:
    #             return redirect('squalaetp:sivin_detail', immat=sivins.first().immat_siv)
    #     corvets = Corvet.search(query)
    #     if corvets:
    #         messages.success(request, _(f'Success: The reseach for {query} was successful.'))
    #         if len(corvets) > 1:
    #             return redirect(reverse('psa:corvet', get={'filter': query}))
    #         return redirect('psa:corvet_detail', pk=corvets.first().pk)

    return None
