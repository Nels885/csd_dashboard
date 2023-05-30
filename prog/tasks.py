import websockets
from sbadmin import celery_app
from django.core.files.storage import default_storage

from prog.models import MbedFirmware


@celery_app.task
def send_firmware_task(ws_uri, fw_name, **kwargs):
    print(fw_name)
    try:
        selected_firmware = MbedFirmware.objects.get(name=fw_name)
        with websockets.connect(ws_uri) as wsocket:
            print("Wsocket Connected")
            print("Sending firmware", selected_firmware.name, selected_firmware.version, "to ", ws_uri)
            wsocket.send("filename:" + selected_firmware.name)
            wsocket.send("deleteFile")
            with default_storage.open(str(selected_firmware.filepath), "rb") as f:
                while True:
                    file_data = f.read()
                    if not file_data:
                        wsocket.send("EOF")
                        f.close()
                        break
                    wsocket.send(file_data)
        msg = "OK"
    except MbedFirmware.DoesNotExist:
        msg = "Not found"
    return msg
