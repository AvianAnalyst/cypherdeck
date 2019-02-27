from fbs_runtime.application_context import ApplicationContext
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import *
from fbs_runtime.application_context import ApplicationContext
import random
import pickle
import pathlib
import sys


class AppContext(ApplicationContext):           # 1. Subclass ApplicationContext
    def run(self):                              # 2. Implement run()
        window = make_window()
        version = self.build_settings['version']
        window.setWindowTitle("Cypher-Deck v" + version)
        window.resize(250, 150)
        window.show()
        ui = make_ui(window)
        deck = make_deck()
        deck.draw(ui)
        ui.draw.clicked.connect(lambda: on_draw_click(deck, ui))
        ui.reset_weights.clicked.connect(lambda: on_balance_click(deck))
        return self.app.exec_(), deck                # 3. End run() with this line


class UiMainWindow(object):
    def __init__(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(507, 652)
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.draw = QtWidgets.QPushButton(self.centralwidget)
        self.draw.setGeometry(QtCore.QRect(0, 570, 511, 31))
        self.draw.setObjectName("draw")
        self.description = QtWidgets.QTextBrowser(self.centralwidget)
        self.description.setGeometry(QtCore.QRect(0, 20, 511, 551))
        self.description.setObjectName("description")
        self.reset_weights = QtWidgets.QPushButton(self.centralwidget)
        self.reset_weights.setGeometry(QtCore.QRect(0, 600, 511, 31))
        self.reset_weights.setObjectName("reset_weights")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(6, 0, 501, 20))
        self.title.setObjectName("title")
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 507, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        main_window.setMenuBar(self.menubar)
        self.actionAdd_Card = QtWidgets.QAction(main_window)
        self.actionAdd_Card.setObjectName("actionAdd_Card")
        self.actionRemove_Card = QtWidgets.QAction(main_window)
        self.actionRemove_Card.setObjectName("actionRemove_Card")
        self.menuFile.addAction(self.actionAdd_Card)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionRemove_Card)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.draw.setText(_translate("main_window", "Draw"))
        self.reset_weights.setText(_translate("main_window", "Reset Balance"))
        self.title.setText(_translate("main_window", "TextLabel"))
        self.menuFile.setTitle(_translate("main_window", "File"))
        self.actionAdd_Card.setText(_translate("main_window", "Add Card"))
        self.actionRemove_Card.setText(_translate("main_window", "Remove Card"))


class Card:
    def __init__(self, level, title, description):
        self.level = level
        self.title = title
        self.description = description
        self.weight = 100

    def get_info(self, level=None):
        level = level or self.level
        if type(level) is int:
            title = 'Level ' + str(level) + ' ' + self.title
        else:
            title = self.level + self.title
        # print(self.weight)
        return title, self.description

    def calc_level(self):
        level = str(self.level)
        if len(level) == 9 or len(level) == 10:
            mod = int(level[6])
            biggest = int(level[8:])
            return mod * random.randint(1, biggest)
        elif len(level) == 11:
            mult = int(level[6])
            plus = int(level[10:])
            return mult * (random.randint(1, 6) + plus)
        else:
            mult = int(level[6])
            plus = int(level[12:])
            return mult * (random.randint(1, 10) + plus)

    def generate_strings(self):
        output = self.level
        return output


class Deck:
    def __init__(self, filename):
        save_location = pathlib.Path.home()
        self.save_location = save_location.joinpath('cypher.pk1')
        try:
            with open(self.save_location, 'rb') as file:
                self.cards = pickle.load(file)
        except:
            with open(filename, 'rb') as file:
                self.cards = pickle.load(file)
        self.total_weight = self.get_total_weight()

    def save(self):
        pickle.dump(self.cards, open(self.save_location, 'wb'))

    def draw(self, instance):
        pick = random.choices(self.cards, (card.weight for card in self.cards))
        pick = pick[0]
        level = pick.calc_level()
        title, description = pick.get_info(level)
        instance.title.setText(title)
        instance.description.setText(description)
        pick.weight /= 2
        self.total_weight -= pick.weight
        if self.total_weight < 10:  # Might need to change when we balance weights
            self.add_weight()
        print('Card weight:', pick.weight)
        print('Total deck weight: ', self.total_weight)

    def get_total_weight(self):
        total = 0
        for i in self.cards:
            total += i.weight
        self.total_weight = total
        return total

    def balance(self):
        for i in self.cards:
            i.weight = 100
        print('Resetting weight.')
        self.get_total_weight()
        print('New deck total weight: ', self.total_weight)

    def add_weight(self):
        for i in self.cards:
            i.weight *= 100
        self.total_weight = self.get_total_weight()

    def get_count(self):
        return len(self.cards)


def main_setup():
    global app
    app = QApplication([])

    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def on_draw_click(deck, ui):
    deck.draw(ui)


def on_balance_click(deck):
    deck.balance()


def set_file_name():
    if getattr(sys, 'frozen', False):
        filename = pathlib.Path(sys.executable).resolve().parents[0]
        filename = filename.joinpath('cyphers.pk1')
    else:
        filename = pathlib.Path(__file__).resolve().parents[1]
        filename = filename.joinpath('resources/base/cyphers.pk1')
    return filename


def make_deck():
    filename = set_file_name()
    deck = Deck(filename)
    print(deck.total_weight)
    return deck


def make_window():
    main_setup()
    window = QMainWindow()
    return window


def make_ui(window):
    ui = UiMainWindow(window)
    return ui


if __name__ == '__main__':
    appctxt = AppContext()                      # 4. Instantiate the subclass
    exit_code, deck = appctxt.run()                   # 5. Invoke run()
    deck.save()
    sys.exit(exit_code)
