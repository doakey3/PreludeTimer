import time
import subprocess
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from timer import Timer


if os.name == 'nt': # windows
    from utils.get_active_windows_process import get_active_process
    from utils.windows_volume import get_volume
    from utils.windows_volume import set_volume
    from pyHook import HookManager


elif os.name == 'posix': # linux
    from utils.get_active_linux_process import get_active_process
    from utils.linux_volume import get_volume
    from utils.linux_volume import set_volume
    from pyxhook import HookManager


class ResizeThread(QtCore.QThread):
    reset_timer_signal = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        time.sleep(.02)
        self.reset_timer_signal.emit()


class PlayerGetterThread(QtCore.QThread):
    found_signal = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        time.sleep(.02)
        self.found_signal.emit()


class FadeThread(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.start_time = 8
        self.step = .1

    def run(self):
        self.curAudio = float(get_volume())
        self.reduction = self.curAudio/(self.start_time/self.step)
        while self.exiting == False:
            if int(self.curAudio - self.reduction) > 0:
                set_volume(int(self.curAudio-self.reduction))
                self.curAudio = self.curAudio-self.reduction
                time.sleep(self.step)
            else:
                set_volume(0)


class Master(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Master, self).__init__(parent)
        self.old_volume = get_volume()
        self.program_searching = False
        self.fading = False

        self.initUI()

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        ba = QtCore.QByteArray.fromBase64(icon_data)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(ba, 'PNG')
        icon = QtGui.QIcon()
        icon.addPixmap(pixmap)
        self.setWindowIcon(icon)

        self.load_settings()

        xspacer = QtWidgets.QSpacerItem(10, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        big_xspacer = QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.pretext_layout = QtWidgets.QHBoxLayout()

        self.pretext_label = QtWidgets.QLabel("Pretext:")
        self.pretext_input = QtWidgets.QLineEdit(self.settings["pretext"])
        self.pretext_input.textChanged.connect(self.set_pretext)

        self.gotime_label = QtWidgets.QLabel("Go Time:")
        self.hour_input = QtWidgets.QComboBox()
        hours = ['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
        self.hour_input.insertItems(0, hours)
        self.hour_input.setCurrentIndex(hours.index(self.settings['gotime'].split(':')[0]))
        self.hour_input.currentIndexChanged.connect(self.set_gotime)
        self.colon_label = QtWidgets.QLabel(":")
        self.colon_label.setFixedWidth(3)
        self.minute_input = QtWidgets.QComboBox()
        minutes = ['59', '58', '57', '56', '55', '54', '53', '52', '51', '50', '49', '48', '47', '46', '45', '44', '43', '42', '41', '40', '39', '38', '37', '36', '35', '34', '33', '32', '31', '30', '29', '28', '27', '26', '25', '24', '23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
        self.minute_input.insertItems(0, minutes)
        self.minute_input.setCurrentIndex(minutes.index(self.settings['gotime'].split(':')[1]))
        self.minute_input.currentIndexChanged.connect(self.set_gotime)

        self.pretext_layout.addWidget(self.pretext_label)
        self.pretext_layout.addWidget(self.pretext_input)
        self.pretext_layout.addWidget(self.gotime_label)
        self.pretext_layout.addWidget(self.hour_input)
        self.pretext_layout.addWidget(self.colon_label)
        self.pretext_layout.addWidget(self.minute_input)
        self.pretext_layout.addItem(xspacer)

        self.v_layout.addLayout(self.pretext_layout)

        self.settings_layout = QtWidgets.QHBoxLayout()

        self.font_size_label = QtWidgets.QLabel("Font Size:")
        font_sizes = ["20", "24", "28", "30", "34", "38", "40", "44",
                      "48", "52", "56", "60", "64", "68", "72"]
        self.font_size_combobox = QtWidgets.QComboBox()
        self.font_size_combobox.insertItems(0, font_sizes)
        self.font_size_combobox.setCurrentIndex(font_sizes.index(self.settings['fontsize']))
        self.font_size_combobox.currentIndexChanged.connect(self.set_font)

        self.font_type_label = QtWidgets.QLabel("Font Type:")
        self.font_type_combobox = QtWidgets.QFontComboBox()
        self.font_type_combobox.setCurrentFont(QtGui.QFont(self.settings['fonttype']))
        self.font_type_combobox.currentIndexChanged.connect(self.set_font)
        self.font_type_combobox.setFixedWidth(128)

        self.fg_color_label = QtWidgets.QLabel("Fg:")
        self.fg_color_button = QtWidgets.QPushButton()
        self.fg_color_button.setFixedWidth(32)
        self.fg_color_button.clicked.connect(self.choose_fg_color)
        self.fg_color_button.setStyleSheet("background-color: " + self.settings['fgcolor'] + ';')
        self.fg_dialog = QtWidgets.QColorDialog()

        self.bg_color_label = QtWidgets.QLabel("Bg:")
        self.bg_color_button = QtWidgets.QPushButton()
        self.bg_color_button.setFixedWidth(32)
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        self.bg_color_button.setStyleSheet("background-color: " + self.settings['bgcolor'] + ';')
        self.bg_dialog = QtWidgets.QColorDialog()

        self.settings_layout.addWidget(self.font_size_label)
        self.settings_layout.addWidget(self.font_size_combobox)
        self.settings_layout.addItem(xspacer)
        self.settings_layout.addWidget(self.font_type_label)
        self.settings_layout.addWidget(self.font_type_combobox)
        self.settings_layout.addItem(xspacer)
        self.settings_layout.addWidget(self.fg_color_label)
        self.settings_layout.addWidget(self.fg_color_button)
        self.settings_layout.addWidget(self.bg_color_label)
        self.settings_layout.addWidget(self.bg_color_button)

        self.settings_layout.addItem(big_xspacer)

        self.v_layout.addLayout(self.settings_layout)

        self.fade_layout = QtWidgets.QHBoxLayout()
        self.fade_label = QtWidgets.QLabel("Fade Audio and Close Player:")
        self.fade_checkbox = QtWidgets.QCheckBox()
        self.fade_checkbox.setChecked(bool(self.settings['fadeaudio']))
        self.fade_checkbox.setEnabled(False)
        self.close_label = QtWidgets.QLabel("Player:")
        self.close_button = QtWidgets.QPushButton("")
        self.close_button.setFixedWidth(200)
        self.close_button.clicked.connect(self.start_program_search)

        self.fade_layout.addWidget(self.fade_label)
        self.fade_layout.addWidget(self.fade_checkbox)
        self.fade_layout.addItem(xspacer)
        self.fade_layout.addWidget(self.close_label)
        self.fade_layout.addWidget(self.close_button)
        self.fade_layout.addItem(big_xspacer)

        self.v_layout.addLayout(self.fade_layout)

        self.toggle_timer_button = QtWidgets.QPushButton("Toggle Timer")
        self.toggle_timer_button.clicked.connect(self.toggle_timer)
        self.v_layout.addWidget(self.toggle_timer_button)

        self.hookman = HookManager()
        self.hookman.HookMouse()

        if os.name == 'posix':
            self.hookman.buttonpressevent = self.mousedown
            self.hookman.start()
        elif os.name == 'nt':
            self.hookman.MouseLeftDown = self.mousedown

        self.timer = Timer(app)
        self.timer.prefix = self.pretext_input.text()
        self.timer.gotime = self.hour_input.currentText() + ':' + self.minute_input.currentText() + ':00'
        font = self.font_type_combobox.currentText()
        size = int(self.font_size_combobox.currentText())
        self.timer.label.setFont(QtGui.QFont(font, size, QtGui.QFont.Bold))
        self.timer.label.setStyleSheet("color: " + self.settings['fgcolor'] + ';')
        self.timer.setStyleSheet("background-color: " + self.settings['bgcolor'] + ';')
        self.timer.above_ten_signal.connect(self.get_volume)
        self.timer.below_ten_signal.connect(self.start_fade_thread)
        self.timer.zero_signal.connect(self.reset_volume)

        self.resize_thread = ResizeThread()
        self.resize_thread.reset_timer_signal.connect(self.resize_timer)

        self.fade_thread = FadeThread()
        self.player_getter = PlayerGetterThread()
        self.player_getter.found_signal.connect(self.set_player)

    def start_program_search(self):
        self.program_searching = True
        self.close_button.setText("Click Player Window")

    def mousedown(self, event):
        if self.program_searching:
            self.player_getter.start()

        if os.name == 'nt':
            return True

    def set_player(self):
        program = get_active_process()
        self.close_button.setText(program)
        self.program_searching = False
        self.fade_checkbox.setEnabled(True)

    def set_gotime(self, event):
        self.timer.gotime = self.hour_input.currentText() + ':' + self.minute_input.currentText() + ':00'
        self.timer.update_time()

    def set_pretext(self, event):
        self.timer.prefix = self.pretext_input.text()
        self.timer.update_time()
        self.resize_thread.start()

    def set_font(self, event):
        font = self.font_type_combobox.currentText()
        size = int(self.font_size_combobox.currentText())
        self.timer.label.setFont(QtGui.QFont(font, size, QtGui.QFont.Bold))
        self.resize_thread.start()

    def resize_timer(self):
        self.timer.resize(0, 0)

    def choose_fg_color(self, event):
        self.setEnabled(False)
        color = self.fg_dialog.getColor(QtGui.QColor(self.settings['fgcolor']))
        if color.isValid():
            self.fg_color_button.setStyleSheet("background-color: " + color.name() + ";")
            self.settings['fgcolor'] = color.name()
            self.timer.label.setStyleSheet("color: " + self.settings['fgcolor'] + ';')
        self.setEnabled(True)

    def choose_bg_color(self, event):
        self.setEnabled(False)
        color = self.bg_dialog.getColor(QtGui.QColor(self.settings['bgcolor']))
        if color.isValid():
            self.bg_color_button.setStyleSheet("background-color: " + color.name() + ";")
            self.settings['bgcolor'] = color.name()
            self.timer.setStyleSheet("background-color: " + self.settings['bgcolor'] + ';')
        self.setEnabled(True)

    def save_settings(self):
        parts = [
            "pretext: " + self.pretext_input.text(),
            "gotime: " + self.hour_input.currentText() + ':' + self.minute_input.currentText(),
            "fontsize: " + self.font_size_combobox.currentText(),
            "fonttype: " + self.font_type_combobox.currentText(),
            "fgcolor: " + self.settings['fgcolor'],
            "bgcolor: " + self.settings['bgcolor'],
            "fadeaudio: " + str(self.fade_checkbox.isChecked()),
            "player: " + str(self.close_button.text())
        ]
        with open("pt_settings.ini", "w") as f:
            f.write('\n'.join(parts))

    def load_settings(self):
        self.settings = {
            "pretext": "Lecture Start:",
            "gotime": "12:00",
            "fontsize": "24",
            "fonttype": "Arial",
            "fgcolor": "black",
            "bgcolor": "white",
            "fadeaudio": "True",
            "player": "vlc"
        }
        try:
            with open("pt_settings.ini", 'r') as f:
                text = f.read()
                lines = text.split('\n')
            for line in lines:
                key = line.split(': ')[0].strip()
                val = line.split(': ')[-1].strip()
                self.settings[key] = val

        except FileNotFoundError:
            pass

    def toggle_timer(self, event):
        if self.timer.isVisible():
            self.timer.hide()
        else:
            self.timer.show()

    def get_volume(self):
        self.old_volume = get_volume()
        if self.fading:
            self.fade_thread.exiting = True
            self.fading = False

    def start_fade_thread(self):
        if self.timer.isVisible() and self.fading == False and self.fade_checkbox.isChecked() and self.close_button.text().strip() != '':
            self.fade_thread.exiting = False
            self.fade_thread.start()
            self.fading = True

    def reset_volume(self):
        if self.fade_checkbox.isChecked() and self.timer.isVisible() and self.close_button.text().strip() != '':
            self.fading = False
            self.fade_thread.exiting = True

            player = self.close_button.text()
            if player.strip() != '':
                if os.name == 'posix':
                    subprocess.call(['killall', player])
                elif os.name == "nt":
                    no_window = 0x08000000
                    subprocess.call('taskkill /F /IM ' + player, creationflags=no_window)
            set_volume(self.old_volume)

    def closeEvent(self, event):
        self.save_settings()
        self.timer.close()
        if os.name == 'nt':
            self.hookman.UnhookMouse()

if __name__ == "__main__":
    import sys
    icon_data = bytes("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Om5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczppcHRjRXh0PSJodHRwOi8vaXB0Yy5vcmcvc3RkL0lwdGM0eG1wRXh0LzIwMDgtMDItMjkvIgogICAgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iCiAgICB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIgogICAgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiCiAgICB4bWxuczpwbHVzPSJodHRwOi8vbnMudXNlcGx1cy5vcmcvbGRmL3htcC8xLjAvIgogICAgeG1sbnM6R0lNUD0iaHR0cDovL3d3dy5naW1wLm9yZy94bXAvIgogICAgeG1sbnM6ZGM9Imh0dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIgogICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOkVCQzNEM0Y4QjkxNTExRTQ4REY2QTc3N0IwNzJGRkE0IgogICB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjJlZGQxMmE1LWYzMTctNDMwYS1iNWNlLWNlYmYzNWVlYTRhNyIKICAgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjk2MDNkMDI4LTg0NjItNDA3Yi1hZDY1LWE0ODljMTliNTliMiIKICAgR0lNUDpBUEk9IjIuMCIKICAgR0lNUDpQbGF0Zm9ybT0iTGludXgiCiAgIEdJTVA6VGltZVN0YW1wPSIxNTQ0NTY0OTE5NTkzNjc0IgogICBHSU1QOlZlcnNpb249IjIuMTAuOCIKICAgZGM6Rm9ybWF0PSJpbWFnZS9wbmciCiAgIHhtcDpDcmVhdG9yVG9vbD0iR0lNUCAyLjEwIj4KICAgPGlwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICA8aXB0Y0V4dDpMb2NhdGlvblNob3duPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25TaG93bj4KICAgPGlwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICA8aXB0Y0V4dDpSZWdpc3RyeUlkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6UmVnaXN0cnlJZD4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NGM4YWU3OWQtOWQyZC00MWM4LWJmMGEtMzk3NzgxNGMwYzQxIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKExpbnV4KSIKICAgICAgc3RFdnQ6d2hlbj0iLTA2OjAwIi8+CiAgICA8L3JkZjpTZXE+CiAgIDwveG1wTU06SGlzdG9yeT4KICAgPHhtcE1NOkRlcml2ZWRGcm9tCiAgICBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkVCQzNEM0Y2QjkxNTExRTQ4REY2QTc3N0IwNzJGRkE0IgogICAgc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpFQkMzRDNGNUI5MTUxMUU0OERGNkE3NzdCMDcyRkZBNCIvPgogICA8cGx1czpJbWFnZVN1cHBsaWVyPgogICAgPHJkZjpTZXEvPgogICA8L3BsdXM6SW1hZ2VTdXBwbGllcj4KICAgPHBsdXM6SW1hZ2VDcmVhdG9yPgogICAgPHJkZjpTZXEvPgogICA8L3BsdXM6SW1hZ2VDcmVhdG9yPgogICA8cGx1czpDb3B5cmlnaHRPd25lcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkNvcHlyaWdodE93bmVyPgogICA8cGx1czpMaWNlbnNvcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkxpY2Vuc29yPgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+e1m2ngAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAAuIwAALiMBeKU/dgAAAAd0SU1FB+IMCxUwJ+UImCoAAAh8SURBVFjDlVd7UFTXGf+dsxcWXCxIQQSCCxZ1QUQDiCgCo+QhL8WIWcdmMpCMoCnRaTWlmlZqHQ1RU6MYY8ZGg6aDj8aIj+BoNLUK0e6OHRW04hOF8KiyQHB3uY9z+gfcm0WWxHwzZ2b33O983+9870MYY5AkCa5EKQWlFJIkgRACSZIgCAI45+jt7YW3tzd0Oh0opVAUBaIoQpZleHl5AYD2jTGGrKyshb29vXzNmjWHUlJSGOcclFLIstynjDEGp9M5YKkC1f/d3d1wOByw2+3o6OiA0+mEJElQwff09MBms2n8sixDURTk5OTkGwwGSafTscmTJ1cVFhYGqLIdDgccDgcIYwyiKLq1gIpSFEV4eHigoqLCUFVVFd3T0zO5s7PTX6/X+zLGOgwGw3fBwcFXzGbzraysLJFzjiVLlsQdPnz4Uk9Pj8A5ByEEoaGhd6ZNmzavsrLymmb1n7JAbW0tzc7OTouNja0MCAjoBMABcEIId/1NCOFhYWEPExIStubn50ddunSJzpgxo0yn0w3gDQwMbJ8zZ06cqutHAZjN5kkmk+kM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", encoding='utf-8')
    app = QtWidgets.QApplication(sys.argv)
    prelude_timer = Master()
    prelude_timer.show()
    sys.exit(app.exec_())
