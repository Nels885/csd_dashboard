def get_header_fields(prod_list):
    header = [value_tuple[0] for value_tuple in prod_list]
    fields = [value_tuple[1] for value_tuple in prod_list]
    return header, fields
