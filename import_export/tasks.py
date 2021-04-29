import os.path

from sbadmin import celery_app
from openpyxl import Workbook

from .utils import extract_corvet, extract_ecu, extract_reman
from utils.file.export_task import ExportCorvetTask


""" source: https://github.com/ebysofyan/django-celery-progress-sample """


class ExportCorvetIntoExcelTask(ExportCorvetTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'xlsx')
        product = kwargs.pop('product', 'bsi')
        vin_list = kwargs.pop('vin_list', None)
        if vin_list is None:
            filename = f"{product}_{self.date.strftime('%y-%m-%d_%H-%M')}"
            self.header, self.fields, values_list = extract_corvet(product)
        else:
            filename = f"ecu_{self.date.strftime('%y-%m-%d_%H-%M')}"
            self.header, self.fields, values_list = extract_ecu(vin_list)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export CORVET",
            "data": {
                "outfile": destination_path
            }
        }


class ExportRemanIntoExcelTask(ExportCorvetTask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        path = self.copy_and_get_copied_path()
        excel_type = kwargs.pop('excel_type', 'xlsx')
        model = kwargs.pop('table', 'bsi')
        filename = f"{model}_{self.date.strftime('%y-%m-%d_%H-%M')}"
        self.header, self.fields, values_list = extract_reman(model)
        destination_path = os.path.join(path, f"{filename}.{excel_type}")
        workbook = Workbook()
        workbook = self.create_workbook(workbook, self.header, values_list)
        workbook.save(filename=destination_path)
        return {
            "detail": "Successfully export REMAN",
            "data": {
                "outfile": destination_path
            }
        }


@celery_app.task(bind=True, base=ExportCorvetIntoExcelTask)
def export_corvet_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)


@celery_app.task(bind=True, base=ExportRemanIntoExcelTask)
def export_reman_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
