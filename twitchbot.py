from PySide2.QtCore import QCoreApplication, qApp, QTimer
from PySide2.QtNetwork import QTcpSocket, QAbstractSocket
import sys


class TwitchBot(QTcpSocket):
    SERVER = "irc.chat.twitch.tv"
    PORT = 6667
    BOT_NAME = "mthnzbkBot"
    PASSWORD = "oauth:47abc39v1xyflk35cm8wly2ek8fn01"
    CHANNELS = {"macabreartgames": {"ready": False, "first_msg_list": ["macabreartgames", "streamelements"]},
                #"benceemerik": {"ready": False, "first_msg_list": ["benceemerik", "streamelements", "streamlabs", "nightbot"]},
                #"wildgenie": {"ready": False, "first_msg_list": ["wildgenie", "wildgeniebot", "streamelements",
                                                                 #"streamlabs"]},
                #"randomman_eq": {"ready": False, "first_msg_list": ["randomman_eq"]}
    }


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
            self.write(bytes(f"PASS {self.PASSWORD} \r\n", "utf-8"))
            self.write(bytes(f"NICK {self.BOT_NAME} \r\n", "utf-8"))
            # self.write(bytes("CAP REQ :twitch.tv/membership\r\n", "utf-8"))
            # self.write(bytes("CAP REQ :twitch.tv/tags\r\n", "utf-8"))
            # self.write(bytes("CAP REQ :twitch.tv/commands\r\n", "utf-8"))
            for channel in self.CHANNELS.keys():
                print(channel)
                self.write(bytes(f"JOIN #{channel} \r\n", "utf-8"))


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
        data = str(self.read(1024), "utf-8")
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
            print(name)

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
        s = bytes(f"PRIVMSG #{channel} :{message} \r\n", "utf-8")
        self.write(s)
        print(s)


app = QCoreApplication([])
bot = TwitchBot()

app.exec_()