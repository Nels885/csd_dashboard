import json

from websockets.sync.client import connect
from sbadmin import celery_app
from django.core.files.storage import default_storage

from prog.models import MbedFirmware


@celery_app.task(bind=True)
def send_firmware_task(self, raspi_url, fw_name, target):
    ws_uri = "ws://" + raspi_url + ":8080/mbed-update/"
    msg = {"msg": "Succès : Connexion au raspberry avec succès !"}
    try:
        query = MbedFirmware.objects.get(name=fw_name)
        data = {"target": target, "filename": query.name, "filesize": query.filepath.size, "version": query.version}
        with connect(str(ws_uri)) as wsocket:
            wsocket.send(json.dumps(data))
            # wsocket.send(f"target: {target}")
            # wsocket.send(f"filename: {query.name}")
            # wsocket.send(f"filesize: {query.filepath.size}")
            # wsocket.send(f"version: {query.version}")
            with default_storage.open(query.filepath.path, "rb") as f:
                file_data = f.read()
                wsocket.send(file_data)
            wsocket.send("EOF")
    except MbedFirmware.DoesNotExist:
        msg = {"msg": "Not found", "tags": "warning"}
    except TimeoutError:
        msg = {"msg": "Connection timed out : connexion au raspberry impossible !", "tags": "warning"}
    except ConnectionRefusedError:
        msg = {"msg": "Connection refused : connexion au raspberry refusée !", "tags": "warning"}
    return msg
