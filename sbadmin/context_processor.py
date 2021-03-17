from _version import __version__


def get_release(request):
    return {'release': __version__}
