import json
import html

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *

from eng_beng import GuiMainWindow
from eng_beng.functions import extract_types, get_db_path


class MainWindow(GuiMainWindow):
    def __init__(self):
        super().__init__()
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(get_db_path())
        self.db.open()

        self.types = extract_types(self.db)

        self.en_completer = self.make_completer('en')
        self.bn_completer = self.make_completer('bn')
        self.current_completer = None

        self.set_up_slots()

        # Self Configs
        self.monitorClipBoard = True
        self.autoSpeak = self.tts.ok
        self.keepAbove = True
        self.last_clip_changed = 0

        self.init()

    def make_completer(self, lang, index=0):
        model = QSqlQueryModel(self)
        if lang == 'en':
            query = QSqlQuery("SELECT DISTINCT word FROM english", self.db)
        else:
            query = QSqlQuery("SELECT word FROM bangla UNION SELECT bangla as word FROM bn_en GROUP BY word", self.db)
        model.setQuery(query)
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionColumn(index)
        completer.setMaxVisibleItems(10)
        completer.activated.connect(self.on_completer_done)
        return completer

    def init(self):
        self.monitorClipCheck.setChecked(self.monitorClipBoard)
        self.autoSpeakCheck.setChecked(self.autoSpeak)
        self.keepAboveCheck.setChecked(self.keepAbove)

    def set_up_slots(self):
        self.inputLine.textChanged.connect(self.on_input_changed)
        self.inputLine.returnPressed.connect(self.on_input_submitted)
        self.clearBtn.clicked.connect(self.on_clear_input_clicked)
        self.ttsCombo.currentTextChanged.connect(self.on_tts_changed)
        self.speakBtn.clicked.connect(self.on_speak_btn_clicked)
        self.monitorClipCheck.stateChanged.connect(self.on_clip_monitor_check_changed)
        self.autoSpeakCheck.stateChanged.connect(self.on_auto_speak_check_changed)
        self.keepAboveCheck.stateChanged.connect(self.on_keep_above_check_changed)
        self.exitAction.triggered.connect(QApplication.quit)
        self.aboutAction.triggered.connect(self.show_about)

    def on_clear_input_clicked(self):
        self.inputLine.clear()
        self.inputLine.setFocus()

    def on_speak_btn_clicked(self):
        text = self.inputLine.text()
        if not text:
            return
        self.speak_now(text)

    def on_tts_changed(self, value):
        self.tts.engine = value

    def on_completer_done(self, value: str):
        self.translate_now(value)

    def on_input_submitted(self):
        text = self.inputLine.text()
        if len(text) > 0:
            self.translate_now(text.strip())

    def on_input_changed(self, value: str):
        is_eng = len(value) == len(value.encode())
        if is_eng and self.current_completer != self.en_completer:
            # print("Set English completer")
            self.inputLine.setCompleter(self.en_completer)
            self.current_completer = self.en_completer
        elif not is_eng and self.current_completer != self.bn_completer:
            # print("Set Bangla completer")
            self.inputLine.setCompleter(self.bn_completer)
            self.current_completer = self.bn_completer

    def on_clip_monitor_check_changed(self, value):
        monitor = value == Qt.CheckState.Checked
        if monitor:
            QApplication.clipboard().selectionChanged.connect(self.use_clipboard_selection)
            QApplication.clipboard().dataChanged.connect(self.use_clipboard_data)
        else:
            QApplication.clipboard().selectionChanged.disconnect(self.use_clipboard_selection)
            QApplication.clipboard().dataChanged.disconnect(self.use_clipboard_data)

    def on_auto_speak_check_changed(self, value):
        self.autoSpeak = value == Qt.CheckState.Checked

    def on_keep_above_check_changed(self, value):
        keep_above = value == Qt.CheckState.Checked
        if keep_above:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.CustomizeWindowHint)
        self.show()

    def use_clipboard_selection(self):
        data = QApplication.clipboard().text(QClipboard.Mode.Selection)
        text = data.strip(' \n\t\f-_,.\'"(){}[]`:;?!')
        if len(text) < 32 and self.inputLine.text() != text:
            self.translate_now(text)

    def use_clipboard_data(self):
        data = QApplication.clipboard().text(QClipboard.Mode.Clipboard)
        text = data.strip(' \n\t\f-_,.\'"(){}[]`:;?!')
        if len(text) < 32 and self.inputLine.text() != text:
            self.translate_now(text)

    def translate_now(self, text):
        if not text:
            return
        self.inputLine.setText(text)
        if self.autoSpeak:
            self.speak_now(text)
        is_eng = len(text) == len(text.encode())
        if is_eng:
            query = QSqlQuery("SELECT serial, word, extra, phonetic, antonyms, definitions, examples FROM bangla WHERE"
                              " serial IN (SELECT serial FROM english WHERE word LIKE ?)", self.db)
        else:
            query = QSqlQuery("SELECT serial, (SELECT word FROM english e WHERE e.serial = b.serial) as en, extra,"
                              " phonetic, antonyms, definitions, examples FROM bangla b WHERE b.word LIKE ?", self.db)
        query.bindValue(0, text)
        query.exec_()
        found = query.first()
        if not found and is_eng:
            self.show_not_found()
            return
        else:
            # Try query from bn_en table.
            more_en = ''
            if not is_eng:
                extra = QSqlQuery("SELECT english FROM bn_en WHERE bangla LIKE ?", self.db)
                extra.bindValue(0, text)
                extra.exec_()
                if extra.first():
                    words = extra.value(0)
                    if words:
                        words = list(json.loads(words))
                        more_en = ', '.join([w.capitalize() for w in words])
            if not found and not more_en:
                self.show_not_found()
                return
            elif not found:
                htm = f'<h2>{html.escape(more_en)}</h2>'
            else:
                more = f'<hr/>{html.escape(more_en)}' if more_en else ''
                htm = '<html><head><style>*{margin: 0}html{font-size:14px}</style></head><body>'
                htm += f"<h3>{html.escape(query.value(1))}</h3>{html.escape(query.value(3))}{more}<hr/>"

                ant = query.value(4)
                if ant:
                    words = ', '.join([w.capitalize() for w in list(json.loads(ant))])
                    htm += f'<h4 style="text-align:center">Antonyms</h4>{html.escape(words)}<hr/>'

                data = query.value(5)
                if data:
                    parts = list(json.loads(data))
                    lines = ''
                    for p in parts:
                        lines += f"<li>{html.escape(p.capitalize())}</li>"
                    if lines:
                        htm += f'<h4 style="text-align:center">Definitions</h4><ul>{lines}</ul><hr/>'

                types = query.value(2)
                if types:
                    lists = list(json.loads(types))
                    for i in lists:
                        type_id = i[0]
                        type_name = self.types[type_id]
                        q = QSqlQuery(f"SELECT * FROM bn_en WHERE serial IN ({','.join([str(j) for j in i[1:]])})",
                                      self.db)
                        q.exec_()
                        lines = ''
                        while q.next():
                            bn = q.value(1)
                            parts = list(json.loads(q.value(2)))
                            words = ', '.join([w.capitalize() for w in parts])
                            lines += f'<br/><em>{html.escape(bn)}</em><br>{html.escape(words)}<br/>'
                        htm += f'<h4 style="text-align:center">{html.escape(type_name)}</h4>{lines}<hr/>'
                example = query.value(6)
                if example:
                    htm += f'<h4 style="text-align:center">Example</h4>{html.escape(example.capitalize())}'
                htm += '</body>'
            self.outputBox.setHtml(htm)

    def show_not_found(self):
        self.outputBox.setHtml('<h4 style="color: red;text-align:center">Nothing Found!</h4>')

    def speak_now(self, text):
        self.tts.speak_text(text)

    def show_about(self):
        htm = f'''
        <div style="text-align: center">
            <h2>Bangla Dictionary</h2>
            <small>v1.1.0</small><br>
            <a href="https://github.com/chitholian/Bangla-Dictionary">
                https://github.com/chitholian/Bangla-Dictionary
            </a>
        </div>
        <p style="text-align: justified">
            This application helps translating words between <em>Bengali</em> and <em>English</em> languages.
            It also shows following extra things for many words:
            <ul>
                <li>Antonyms</li>
                <li>Synonyms</li>
                <li>Parts of speech</li>
                <li>Definitions</li>
                <li>Examples</li>
                <li>Phonetic of Bengali words</li>
            </ul>
            <p>
                ==> By default this application is configured to stay above other windows; it helps improved experience 
                of clipboard monitoring feature. Uncheck the "Keep window above" checkbox to turn it off.
            </p>
            <p>
                ==> Just keep this app running and copy some words (Ctrl+C) from anywhere of your device (e.g. from web
                 browser, PDF viewer etc.)
            </p>
            <p>
                ==> This app will monitor your clipboard and show translation as soon as you copy texts. It does not
                 require you to paste the selected word inside this app (although you can do so).
            </p>
            <p>
                ==> Linux (X11 Window System) provides access to clipboard selection. In that case you don't even need
                 to copy the text, just double click the word (or use mouse/touchpad) to select it. This app will
                  capture and show the translation.
            </p>
        </p>
        <div style="text-align: center">
            <h3 style="text-align: center">About Developer</h3>
            Name: <strong>Atikur Rahman Chitholian</strong><br>
            Session: <strong>2015-16</strong><br>
            Dept. of <strong>Computer Science and Engineering</strong><br>
            <strong>University of Chittagong, Bangladesh</strong>
        </div>
        '''
        self.outputBox.setHtml(htm)
