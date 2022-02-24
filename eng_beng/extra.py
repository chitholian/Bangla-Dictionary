import os
import shutil


class TTSEngine:
    ESPEAK = "Espeak"
    ESPEAK_NG = "Espeak-Ng"
    FLITE = "Flite"
    FESTIVAL = "Festival"

    def __init__(self):
        super().__init__()
        self.engines = self.detect_tts_engines()
        self.ok = len(self.engines) > 0
        if self.ok:
            self.engine = self.engines[0]
        else:
            self.engine = None

    def speak_text(self, text):
        if self.engine is None:
            return
        elif self.engine == self.ESPEAK:
            os.system("espeak \"{}\" &".format(text))
        elif self.engine == self.ESPEAK_NG:
            os.system("espeak-ng \"{}\" &".format(text))
        elif self.engine == self.FLITE:
            os.system("flite -t \"{}\" &".format(text))
        elif self.engine == self.FESTIVAL:
            os.system("echo \"{}\" | festival --tts &".format(text))

    @staticmethod
    def detect_tts_engines():
        engines = []
        if shutil.which("espeak"):
            engines.append(TTSEngine.ESPEAK)
        if shutil.which("espeak-ng"):
            engines.append(TTSEngine.ESPEAK_NG)
        if shutil.which("flite"):
            engines.append(TTSEngine.FLITE)
        if shutil.which("festival"):
            engines.append(TTSEngine.FESTIVAL)
        return engines
