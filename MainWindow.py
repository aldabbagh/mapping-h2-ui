import sys
import ui_library
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtWidgets import *


class UiWindow(QMainWindow):
    def __init__(self):
        super(UiWindow, self).__init__()
        self.setWindowTitle("H2 mapping UI")
        self.setGeometry(500, 200, 600, 400)

        self.window = QWidget()

        self.grid = QGridLayout()

        # create labels for the coordinates, latitude and longitude
        # as well as input-boxes for latitude and longitude values
        self.coord_label = QLabel("coordinates :")
        self.long_label = QLabel("longitude :")
        self.lat_label = QLabel("latitude :")
        self.long_lineedit = QLineEdit()
        self.lat_lineedit = QLineEdit()

        # creates the year label and a combo box with the options of choosing 2020, 2030, 2040, 2050
        self.year_label = QLabel("year :")
        self.year_combo = QComboBox()
        self.year_combo.addItems(["2020", "2030", "2040", "2050"])

        # creates the yearly hydrogen demand label and a spinbox that takes values between 1 and 1 million
        # the value can be changed in steps of 10 via the arrows
        self.hhdemand_label = QLabel("yearly hydrogen demand :")
        self.hhdemand_spinbox = QDoubleSpinBox()
        self.hhdemand_spinbox.setRange(0, 1000000)
        self.hhdemand_spinbox.setSingleStep(10)

        # creates a checkbox to decide whether to allow pipelines as transport medium or not
        self.pipe_checkbox = QCheckBox()
        self.pipe_checkbox.setText("allow pipelines")

        # creates a checkbox to decide whether to allow central conversion facilities
        self.conversion_checkbox = QCheckBox()
        self.conversion_checkbox.setText("allow central conversion")

        # creates label and input box for
        self.maxpipe_label = QLabel("maximum pipeline length :")
        self.maxpipe_spinbox = QSpinBox()
        self.maxpipe_spinbox.setRange(0, 20000)
        self.maxpipe_spinbox.setSingleStep(10)

        # creates a checkbox with the option to toggle between single run and monte carlo sim
        self.mc_checkbox = QCheckBox()
        self.mc_checkbox.setText("run as monte-carlo-simulation")

        # creates optional parameter inputs for monte carlo sim
        # create label and lineedit to put in iterations
        self.iter_label = QLabel("number of iterations")
        self.iter_lineedit = QLineEdit()

        # create combobox with electrolyzer options
        self.electro_label = QLabel("electrolyzer type :")
        self.electro_combo = QComboBox()
        self.electro_combo.addItems(["soe", "alkaline", "pem"])

        # put labels and corresponding widgets into sub-layouts
        self.iter_layout = QHBoxLayout()
        self.iter_layout.addWidget(self.iter_label)
        self.iter_layout.addWidget(self.iter_lineedit)

        self.electro_layout = QHBoxLayout()
        self.electro_layout.addWidget(self.electro_label)
        self.electro_layout.addWidget(self.electro_combo)

        self.sublayout = QVBoxLayout()
        self.sublayout.addLayout(self.iter_layout)
        self.sublayout.addLayout(self.electro_layout)

        # creates a button to start the model run
        self.run_button = QPushButton("run model")

        # put longitude and latitude labels into horizontal layouts together with their lineedits
        self.long_hbox = QHBoxLayout()
        self.long_hbox.addWidget(self.long_label)
        self.long_hbox.addWidget(self.long_lineedit)

        self.lat_hbox = QHBoxLayout()
        self.lat_hbox.addWidget(self.lat_label)
        self.lat_hbox.addWidget(self.lat_lineedit)

        # force the two checkboxes into vertical layout
        self.allow_vbox = QVBoxLayout()
        self.allow_vbox.addWidget(self.pipe_checkbox)
        self.allow_vbox.addWidget(self.conversion_checkbox)

        # arranges all widgets in a grid
        self.grid.addWidget(self.coord_label, 0, 0)
        self.grid.addLayout(self.long_hbox, 0, 1)
        self.grid.addLayout(self.lat_hbox, 1, 1)
        self.grid.addWidget(self.year_label, 3, 0)
        self.grid.addWidget(self.year_combo, 3, 1)
        self.grid.addWidget(self.hhdemand_label, 4, 0)
        self.grid.addWidget(self.hhdemand_spinbox, 4, 1)
        self.grid.addLayout(self.allow_vbox, 5, 1)
        self.grid.addWidget(self.maxpipe_label, 6, 0)
        self.grid.addWidget(self.maxpipe_spinbox, 6, 1)
        self.grid.addWidget(self.mc_checkbox, 7, 1)
        self.grid.addLayout(self.sublayout, 8, 1)
        self.grid.addWidget(self.run_button, 9, 3)

        self.window.setLayout(self.grid)

        self.iter_label.hide()
        self.iter_lineedit.hide()
        self.electro_label.hide()
        self.electro_combo.hide()

        self.setCentralWidget(self.window)

        # connecting the toggling of the monte carlo checkbox to slot, extending the parameter inputs
        self.mc_checkbox.stateChanged.connect(self.on_mc_checkbox)

    def on_mc_checkbox(self):
        if self.mc_checkbox.isChecked():
            self.iter_label.show()
            self.iter_lineedit.show()
            self.electro_label.show()
            self.electro_combo.show()

        else:
            self.iter_label.hide()
            self.iter_lineedit.hide()
            self.electro_label.hide()
            self.electro_combo.hide()


app = QApplication(sys.argv)
ui = UiWindow()
ui.show()

sys.exit(app.exec())