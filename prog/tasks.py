from websockets.sync.client import connect
from sbadmin import celery_app
from django.core.files.storage import default_storage

from prog.models import MbedFirmware


@celery_app.task
def send_firmware_task(ws_uri, fw_name, target):
    msg = {"msg": "Error : could not send firmware", "tags": "danger"}
    try:
        selected_firmware = MbedFirmware.objects.get(name=fw_name)
        with connect(str(ws_uri)) as wsocket:
            wsocket.send("target:" + target)
            wsocket.send("filename:" + selected_firmware.name)
            wsocket.send("version:" + selected_firmware.version)
            with default_storage.open(str(selected_firmware.filepath), "rb") as f:
                while True:
                    file_data = f.read()
                    if not file_data:
                        wsocket.send("EOF")
                        f.close()
                        break
                    wsocket.send(file_data)
        msg = {"msg": "Succès : Envoi du firmware avec succès !"}
    except MbedFirmware.DoesNotExist:
        msg = {"msg": "Not found", "tags": "danger"}
    return msg
