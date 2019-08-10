from PySide2.QtCore import QCoreApplication, qApp, QTimer
from PySide2.QtNetwork import QTcpSocket, QAbstractSocket
import sys


class TwitchBot(QTcpSocket):
    SERVER = "irc.chat.twitch.tv"
    PORT = 6667
    BOT_NAME = "mthnzbkBot"
    PASSWORD = "oauth:i5pyfkzugeuma7i9h43pmcb9zbx8xo"
    CHANNELS = {"macabreartgames": {"ready": False, "first_msg_list": []},
                "mthnzbk": {"ready": False, "first_msg_list": []},
                "wildgenie": {"ready": False, "first_msg_list": []}}
    first_msg_list = []
    ready = False

    def __init__(self):
        super().__init__()
        self.connectHost()

    def connectHost(self):
        self.connectToHost(self.SERVER, self.PORT)

        self.connected.connect(self.connectServer)
        self.disconnected.connect(self.disconnectServer)
        self.error.connect(self.connectError)
        self.readyRead.connect(self.readServer)
        self.bytesWritten.connect(self.writeBytes)

        if self.waitForConnected(5000):
            s = f"PASS {self.PASSWORD} \r\n"
            self.writeData(s, len(s))
            s = f"NICK {self.BOT_NAME} \r\n"
            self.writeData(s, len(s))
            for channel in self.CHANNELS.keys():
                print(channel)
                s = f"JOIN #{channel} \r\n"
                self.writeData(s, len(s))


    def connectServer(self):
        print("Bağlantı sağlandı.")

    def disconnectServer(self):
        print("Bağlantı kapatıldı.")
        qApp.quit()
        sys.exit()

    def connectError(self, err):
        print(err)
        if err == QAbstractSocket.SocketError.SocketTimeoutError:
            print("Timeout error")

        elif err == QAbstractSocket.SocketError.RemoteHostClosedError:
            print("Sunucu bağlantıyı kapattı")

        elif err == QAbstractSocket.SocketError.HostNotFoundError:
            print("Sunucuya ulaşılamıyor.")
            timer = QTimer(self)
            timer.singleShot.connect(self.connectHost)
            timer.start()

    def writeBytes(self, wb):
        pass#print(wb)

    def readServer(self):
        data = str(self.read(1024), encoding="utf-8")
        print(data)
        if "End of /NAMES list" in data:
            ch = data.split("\r\n")[-2].split(" ")[3][1:]
            self.CHANNELS[ch]["ready"] = True

        if data.startswith("PING"):
            s = "PONG :tmi.twitch.tv\r\n"
            self.writeData(s, len(s))
            print(s)

        if "PRIVMSG" in data:
            ch = data.split(" ")[2][1:]
            name = data.split("!")[0][1:]

            if not name in self.CHANNELS[ch]["first_msg_list"]:
                self.firstMsgControl(data)
                self.CHANNELS[ch]["first_msg_list"].append(name)

            if "!slm" in data:
                self.sendMessage(ch, "Selam @" + data.split("!")[0][1:])

            if "!yargı" in data:
                self.sendMessage(ch, f"@{ch} başkan yargı dağıtıyor!..")


    def firstMsgControl(self, data):
        ch = data.split(" ")[2][1:]
        name = data.split("!")[0][1:]
        self.sendMessage(ch, "Hoş geldin @{}".format(name))


    def sendMessage(self, channel, message):
        s = bytes(f"PRIVMSG #{channel} :{message} \r\n", encoding="utf-8")
        self.write(s)
        print(s)

app = QCoreApplication([])
bot = TwitchBot()

app.exec_()