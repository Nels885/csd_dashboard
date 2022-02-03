def batch_pdf_data(model):
    reman_reference, part_name = "N/A", "N/A"
    try:
        if model.ecu_ref_base:
            reman_reference = model.ecu_ref_base.reman_reference
            part_name = model.ecu_ref_base.ecu_type.technical_data[:20]
        else:
            reman_reference = model.sem_ref_base.reman_reference
            part_name = model.sem_ref_base.sem_type.first().name_part[:20]
    except AttributeError:
        pass
    finally:
        return reman_reference, part_name
