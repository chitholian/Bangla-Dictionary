from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from eng_beng.functions import resource_path


class GuiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.inputLine = QLineEdit()
        self.inputLine.setPlaceholderText("Enter some text...")
        self.clearBtn = QPushButton(
            QIcon(resource_path('assets/clear.svg')), '')
        self.clearBtn.setToolTip("Clear input")
        self.speakBtn = QPushButton(QIcon.fromTheme('player-volume'), '')
        self.speakBtn.setToolTip("Speak the text")
        self.outputBox = QTextBrowser()
        self.outputBox.setOpenExternalLinks(True)
        self.monitorClipCheck = QCheckBox()
        self.monitorClipCheck.setText("Monitor Clipboard")
        self.autoSpeakCheck = QCheckBox()
        self.autoSpeakCheck.setText("Auto Speak")
        self.keepAboveCheck = QCheckBox()
        self.keepAboveCheck.setText("Keep Window Above")

        self.exitAction = QAction(
            QIcon(resource_path('assets/quit.png')), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')

        self.aboutAction = QAction('&App Info', self)

        self.set_up_gui()

    def set_up_gui(self):
        menu_bar = self.menuBar()
        menu = menu_bar.addMenu("File")
        menu.addAction(self.exitAction)
        menu = menu_bar.addMenu("About")
        menu.addAction(self.aboutAction)

        body = QWidget(self)

        layout = QVBoxLayout()
        body.setLayout(layout)

        h_box = QHBoxLayout()
        layout.addLayout(h_box)
        h_box.addWidget(self.inputLine)
        # h_box.addWidget(self.speakBtn)
        h_box.addWidget(self.clearBtn)

        layout.addWidget(self.outputBox)

        h_box = QHBoxLayout()
        layout.addLayout(h_box)
        h_box.addWidget(self.monitorClipCheck)
        h_box.addStretch()
        h_box.addWidget(self.keepAboveCheck)
        # h_box.addWidget(self.autoSpeakCheck)

        self.setCentralWidget(body)
        self.resize(400, 640)
