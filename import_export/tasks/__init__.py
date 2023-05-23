from sbadmin import celery_app

from .export_reman import ExportRemanIntoExcelTask
from .export_psa import ExportCorvetIntoExcelTask
from .export_tools import ExportToolsIntoExcelTask, ExportSuptechIntoExcelTask


""" source: https://github.com/ebysofyan/django-celery-progress-sample """


@celery_app.task(bind=True, base=ExportCorvetIntoExcelTask)
def export_corvet_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)


@celery_app.task(bind=True, base=ExportRemanIntoExcelTask)
def export_reman_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)


@celery_app.task(bind=True, base=ExportToolsIntoExcelTask)
def export_tools_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)


@celery_app.task(bind=True, base=ExportSuptechIntoExcelTask)
def export_suptech_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
