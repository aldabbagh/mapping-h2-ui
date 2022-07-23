import sys
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import *


class Window(QTabWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("H2 mapping UI")
        self.setGeometry(500, 200, 500, 500)

        # create the tabs and load the uis
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.addTab(self.tab1, "single run")
        self.addTab(self.tab2, "monte carlo simulation")
        self.tab1ui()
        self.tab2ui()

    def tab1ui(self):
        grid = QGridLayout()

        # create labels for the coordinates, latitude and longitude
        # as well as input-boxes for latitude and longitude values
        coord_label = QLabel("coordinates :")
        long_label = QLabel("longitude :")
        lat_label = QLabel("latitude :")
        long_lineedit = QLineEdit()
        lat_lineedit = QLineEdit()

        # creates the year label and a combo box with the options of choosing 2020, 2030, 2040, 2050
        year_label = QLabel("year :")
        year_combo = QComboBox()
        year_combo.addItems(["2020", "2030", "2040", "2050"])

        # creates the yearly hydrogen demand label and a spinbox that takes values between 1 and 1 million
        # the value can be changed in steps of 10 via the arrows
        hhdemand_label = QLabel("yearly hydrogen demand :")
        hhdemand_spinbox = QDoubleSpinBox()
        hhdemand_spinbox.setRange(0, 1000000)
        hhdemand_spinbox.setSingleStep(10)

        # creates a checkbox to decide whether to allow pipelines as transport medium or not
        pipe_checkbox = QCheckBox()
        pipe_checkbox.setText("allow pipelines")

        # creates a checkbox to decide whether to allow central conversion facilities
        conversion_checkbox = QCheckBox()
        conversion_checkbox.setText("allow central conversion")

        # creates label and input box for
        maxpipe_label = QLabel("maximum pipeline length :")
        maxpipe_spinbox = QSpinBox()
        maxpipe_spinbox.setRange(0, 20000)
        maxpipe_spinbox.setSingleStep(10)

        # creates a button to start the model run
        run_button = QPushButton("run model")

        # put longitude and latitude labels into horizontal layouts together with their lineedits
        long_hbox = QHBoxLayout()
        long_hbox.addWidget(long_label)
        long_hbox.addWidget(long_lineedit)

        lat_hbox = QHBoxLayout()
        lat_hbox.addWidget(lat_label)
        lat_hbox.addWidget(lat_lineedit)

        # force the two checkboxes into vertical layout
        allow_vbox = QVBoxLayout()
        allow_vbox.addWidget(pipe_checkbox)
        allow_vbox.addWidget((conversion_checkbox))

        # arranges all widgets in a grid
        grid.addWidget(coord_label, 0, 0)
        grid.addLayout(long_hbox, 0, 1)
        grid.addLayout(lat_hbox, 1, 1)
        grid.addWidget(year_label, 3, 0)
        grid.addWidget(year_combo, 3, 1)
        grid.addWidget(hhdemand_label, 4, 0)
        grid.addWidget(hhdemand_spinbox, 4, 1)
        grid.addLayout(allow_vbox, 5, 1)
        grid.addWidget(maxpipe_label, 6, 0)
        grid.addWidget(maxpipe_spinbox, 6, 1)
        grid.addWidget(run_button, 7, 3)

        self.tab1.setLayout(grid)

    def tab2ui(self):
        grid = QGridLayout()

        # create labels for the coordinates, latitude and longitude
        # as well as input-boxes for latitude and longitude values
        coord_label = QLabel("coordinates :")
        long_label = QLabel("longitude :")
        lat_label = QLabel("latitude :")
        long_lineedit = QLineEdit()
        lat_lineedit = QLineEdit()

        # creates the year label and a combo box with the options of choosing 2020, 2030, 2040, 2050
        year_label = QLabel("year :")
        year_combo = QComboBox()
        year_combo.addItems(["2020", "2030", "2040", "2050"])

        # creates the yearly hydrogen demand label and a spinbox that takes values between 1 and 1 million
        # the value can be changed in steps of 10 via the arrows
        hhdemand_label = QLabel("yearly hydrogen demand :")
        hhdemand_spinbox = QSpinBox()
        hhdemand_spinbox.setRange(0, 1000000)
        hhdemand_spinbox.setSingleStep(10)

        # creates a checkbox to decide whether to allow pipelines as transport medium or not
        pipe_checkbox = QCheckBox()
        pipe_checkbox.setText("allow pipelines")

        # creates a checkbox to decide whether to allow central conversion facilities
        conversion_checkbox = QCheckBox()
        conversion_checkbox.setText("allow central conversion")

        # creates label and input box for
        maxpipe_label = QLabel("maximum pipeline length :")
        maxpipe_spinbox = QSpinBox()
        maxpipe_spinbox.setRange(0, 20000)
        maxpipe_spinbox.setSingleStep(10)

        # create label and lineedit to put in iterations
        iter_label = QLabel("number of iterations")
        iter_lineedit = QLineEdit()

        # create combobox with electrolyzer options
        electro_label = QLabel("electrolyzer type :")
        electro_combo = QComboBox()
        electro_combo.addItems(["soe", "alkaline", "pem"])

        # creates a button to start the model run
        run_button = QPushButton("run model")

        # put longitude and latitude labels into horizontal layouts together with their lineedits
        long_hbox = QHBoxLayout()
        long_hbox.addWidget(long_label, )
        long_hbox.addWidget(long_lineedit)

        lat_hbox = QHBoxLayout()
        lat_hbox.addWidget(lat_label)
        lat_hbox.addWidget(lat_lineedit)

        # force the two checkboxes into vertical layout
        allow_vbox = QVBoxLayout()
        allow_vbox.addWidget(pipe_checkbox)
        allow_vbox.addWidget((conversion_checkbox))

        # arranges all widgets in a grid
        grid.addWidget(coord_label, 0, 0)
        grid.addLayout(long_hbox, 0, 1)
        grid.addLayout(lat_hbox, 1, 1)
        grid.addWidget(year_label, 3, 0)
        grid.addWidget(year_combo, 3, 1)
        grid.addWidget(hhdemand_label, 4, 0)
        grid.addWidget(hhdemand_spinbox, 4, 1)
        grid.addLayout(allow_vbox, 5, 1)
        grid.addWidget(maxpipe_label, 6, 0)
        grid.addWidget(maxpipe_spinbox, 6, 1)
        grid.addWidget(iter_label, 7, 0)
        grid.addWidget(iter_lineedit, 7, 1)
        grid.addWidget(electro_label, 8, 0)
        grid.addWidget(electro_combo, 8, 1)
        grid.addWidget(run_button, 8, 3)

        self.tab2.setLayout(grid)


app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())