from PyQt5 import QtCore, QtGui, QtWidgets
import time
import datetime


def get_current_screen(app, widget):
    screens = app.screens()
    for screen in screens:
        geometry = screen.geometry()
        if widget.x() >= geometry.left() and widget.x() < geometry.left() + geometry.width():
            if widget.y() >= geometry.top() and widget.y() < geometry.top() + geometry.height():
                current_screen = screen
                return current_screen


def strfdelta(tdelta, fmt):
    """
    example:

        print(strfdelta(tdelta, "{hours}:{minutes}:{seconds}"))

    """
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


class Ticker(QtCore.QThread):
    time_change = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Ticker, self).__init__(parent)

    def run(self):
        while True:
            self.time_change.emit()
            time.sleep(1)


class Timer(QtWidgets.QDialog):
    above_ten_signal = QtCore.pyqtSignal()
    below_ten_signal = QtCore.pyqtSignal()
    zero_signal = QtCore.pyqtSignal()

    def __init__(self, app, parent=None):
        super(Timer, self).__init__(parent)
        self.initUI()
        self.prefix = "Lecture Start:"
        self.gotime = "12:00:00"
        self.time_until = "10:00"
        self.app = app

    def initUI(self):
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.label.setText("Lecture Start: 12:00")
        self.label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.v_layout.addWidget(self.label)

        self.ticker = Ticker()
        self.ticker.time_change.connect(self.update_time)
        self.ticker.start()

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def keyPressEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        current_screen = get_current_screen(self.app, self)
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()

        elif event.key() == QtCore.Qt.Key_Up:
            self.move(self.x(), current_screen.geometry().top())
        elif event.key() == QtCore.Qt.Key_Down:
            self.move(self.x(), current_screen.geometry().bottom() - self.height())

            #delta = datetime.timedelta(
            #    hours=int(self.gotime.split(':')[0]),
            #    minutes=int(self.gotime.split(':')[1]),
            #    seconds=int(self.gotime.split(':')[2])
            #)
            #diff = delta - datetime.timedelta(seconds=0.5)
            #self.gotime = strfdelta(diff, "{hours}:{minutes}:{seconds}")
            #self.update_time()

        elif event.key() == QtCore.Qt.Key_Left:
            self.move(current_screen.geometry().left(), self.y())
        elif event.key() == QtCore.Qt.Key_Right:
            self.move(current_screen.geometry().right() - self.width(), self.y())

    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)

    def update_time(self):
        then = datetime.datetime.strptime(self.gotime, '%H:%M:%S')
        now = datetime.datetime.now()
        diff = then - now
        time_until = strfdelta(diff, "{minutes}:{seconds}")

        parts = time_until.split(':')
        for i in range(len(parts)):
            parts[i]  = parts[i].zfill(2)
        self.time_until = ':'.join(parts)

        if self.time_until == "00:00":
            self.zero_signal.emit()
            self.hide()
        elif self.time_until.split(':')[0] == '00' and int(self.time_until.split(':')[1]) < 11:
            self.below_ten_signal.emit()
        else:
            self.above_ten_signal.emit()

        self.label.setText((self.prefix + ' ' + self.time_until).strip())

    def closeEvent(self, event):
        self.ticker.terminate()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    timer = Timer(app)
    timer.show()
    sys.exit(app.exec_())
