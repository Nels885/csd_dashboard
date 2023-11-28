from websockets.sync.client import connect
from sbadmin import celery_app
from django.core.files.storage import default_storage

from prog.models import MbedFirmware


@celery_app.task(bind=True)
def send_firmware_task(self, raspi_url, fw_name, target):
    ws_uri = "ws://" + raspi_url + ":8080/updateMbed"
    msg = {"msg": "Succès : Connexion au raspberry avec succès !"}
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
    except MbedFirmware.DoesNotExist:
        msg = {"msg": "Not found", "tags": "warning"}
    except TimeoutError:
        msg = {"msg": "Connection timed out : connexion au raspberry impossible !", "tags": "warning"}
    except ConnectionRefusedError:
        msg = {"msg": "Connection refused : connexion au raspberry refusée !", "tags": "warning"}
    return msg
