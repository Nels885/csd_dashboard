def defaults_dict(model, row, *args):
    fields = [f.name for f in model._meta.local_fields if f.name not in args]
    defaults = dict(
        (key, value) for key, value in row.items() if key in fields
    )
    return defaults
