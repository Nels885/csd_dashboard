from channels.generic.websocket import WebsocketConsumer


class FirmwareUpdate(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("Websocket Connected")

    def receive(self, text_data=None, bytes_data=None):
        print("Message received :", text_data)
        self.send(text_data)

    def send(self, text_data=None, bytes_data=None, close=False):
        print("Message sent :", text_data)

    def disconnect(self, code):
        print("Websocket Disconnected")
