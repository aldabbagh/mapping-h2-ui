import sys
import ui_library
import ParameterSet
import mc_main
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import math
import DisplayMap


class UiWindow(QMainWindow):
    def __init__(self):
        super(UiWindow, self).__init__()
        self.setWindowTitle("H2 mapping UI")
        self.setGeometry(500, 200, 600, 400)

        self.window = QWidget()

        self.grid = QGridLayout()

        # create groupbox for the coordinates, labels for latitude and longitude
        # as well as input-boxes for latitude and longitude values
        self.coord_groupbox = QGroupBox("coordinates")
        self.coord_groupbox.setStyleSheet("QGroupBox { border-style: solid; border-width: 0.5px; "
                                          "border-radius: 5px; "
                                          "padding-top: 10px; padding-bottom: 3px } ")

        self.coord_groupbox_layout = QVBoxLayout()
        self.coord_groupbox.setLayout(self.coord_groupbox_layout)

        self.long_label = QLabel("longitude :")
        self.lat_label = QLabel("latitude :")
        self.long_lineedit = QLineEdit()
        self.lat_lineedit = QLineEdit()

        # put longitude and latitude labels into horizontal layouts together with their lineedits
        self.long_hbox = QHBoxLayout()
        self.long_hbox.addWidget(self.long_label)
        self.long_hbox.addWidget(self.long_lineedit)

        self.lat_hbox = QHBoxLayout()
        self.lat_hbox.addWidget(self.lat_label)
        self.lat_hbox.addWidget(self.lat_lineedit)

        self.coord_groupbox_layout.addLayout(self.lat_hbox)
        self.coord_groupbox_layout.addLayout(self.long_hbox)

        # creates the year groupbox and a combo box with the options of choosing 2020, 2030, 2040, 2050
        self.year_groupbox = QGroupBox("year")
        self.year_groupbox.setStyleSheet("QGroupBox { border-style: solid; border-width: 0.5px; "
                                         "border-radius: 5px; padding-top: 10px; padding-bottom: 3px }")
        self.year_groupbox_layout = QVBoxLayout()
        self.year_combo = QComboBox()
        self.year_combo.addItems(["2020", "2030", "2040", "2050"])
        self.year_groupbox_layout.addWidget(self.year_combo)
        self.year_groupbox.setLayout(self.year_groupbox_layout)

        # create a groupbox for demand and central conversion
        self.demand_conversion_groupbox = QGroupBox()
        self.demand_conversion_groupbox.setStyleSheet("QGroupBox { border-style: solid; border-width: 0.5px; "
                                                      "border-radius: 5px; padding-top: 10px; padding-bottom: 3px }")
        self.demand_conversion_groupbox_layout = QVBoxLayout()
        self.demand_conversion_groupbox.setLayout(self.demand_conversion_groupbox_layout)

        # creates the yearly hydrogen demand label and a spinbox that takes values between 1 and 1 million
        # the value can be changed in steps of 10 via the arrows; arrange it in a HBox layout with the label
        self.hhdemand_label = QLabel("yearly hydrogen demand (in kilotons) :")
        self.hhdemand_spinbox = QDoubleSpinBox()
        self.hhdemand_spinbox.setRange(0, 1000000)
        self.hhdemand_spinbox.setSingleStep(10)
        self.hhdemand_layout = QHBoxLayout()
        self.hhdemand_layout.addWidget(self.hhdemand_label)
        self.hhdemand_layout.addWidget(self.hhdemand_spinbox)

        # create combobox with electrolyzer options
        self.electro_label = QLabel("electrolyzer type :")
        self.electro_combo = QComboBox()
        self.electro_combo.addItems(["soe", "alkaline", "pem"])

        # put label and combo box into a layout
        self.electro_layout = QHBoxLayout()
        self.electro_layout.addWidget(self.electro_label)
        self.electro_layout.addWidget(self.electro_combo)

        # creates a checkbox to decide whether to allow central conversion facilities
        self.conversion_checkbox = QCheckBox("allow central conversion")

        self.demand_conversion_groupbox_layout.addLayout(self.hhdemand_layout)
        self.demand_conversion_groupbox_layout.addLayout(self.electro_layout)
        self.demand_conversion_groupbox_layout.addWidget(self.conversion_checkbox)

        # create a groupbox for the pipeline related widgets
        self.pipe_groupbox = QGroupBox("pipelines")
        self.pipe_groupbox.setStyleSheet("QGroupBox { border-style: solid; border-width: 0.5px; "
                                         "border-radius: 5px; padding-top: 10px } ")
        self.pipe_groupbox_layout = QVBoxLayout()

        # creates a checkbox to decide whether to allow pipelines as transport medium or not
        self.pipe_checkbox = QCheckBox("allow pipelines")

        # creates label and input box for
        self.maxpipe_label = QLabel("maximum pipeline length :")
        self.maxpipe_spinbox = QSpinBox()
        self.maxpipe_spinbox.setRange(0, 20000)
        self.maxpipe_spinbox.setSingleStep(10)
        self.maxpipe_layout = QHBoxLayout()
        self.maxpipe_layout.addWidget(self.maxpipe_label)
        self.maxpipe_layout.addWidget(self.maxpipe_spinbox)

        self.pipe_groupbox_layout.addWidget(self.pipe_checkbox)
        self.pipe_groupbox_layout.addLayout(self.maxpipe_layout)
        self.pipe_groupbox.setLayout(self.pipe_groupbox_layout)

        # groupbox to contain the monte carlo widgets
        self.mc_widgets_groupbox = QGroupBox("monte-carlo-simulation")
        self.mc_widgets_groupbox.setStyleSheet("QGroupBox { border-style: solid; border-width: 0.5px; "
                                               "border-radius: 5px; padding-top: 10px } ")
        self.mc_widgets_groupbox_layout = QVBoxLayout()

        # creates a checkbox with the option to toggle between single run and monte carlo sim
        self.mc_checkbox = QCheckBox()
        self.mc_checkbox.setText("run as monte-carlo-simulation")

        # creates optional parameter inputs for monte carlo sim
        # create label and lineedit to put in iterations
        self.iter_label = QLabel("iterations: ")
        self.iter_lineedit = QLineEdit()
        self.iter_lineedit.setPlaceholderText("Enter the number of iterations")

        # put labels and corresponding widgets into sub-layouts
        self.iter_layout = QHBoxLayout()
        self.iter_layout.addWidget(self.iter_label)
        self.iter_layout.addWidget(self.iter_lineedit)

        self.mc_widgets_groupbox_layout.addWidget(self.mc_checkbox)
        self.mc_widgets_groupbox_layout.addLayout(self.iter_layout)
        self.mc_widgets_groupbox.setLayout(self.mc_widgets_groupbox_layout)

        # create a label to display some results
        self.results_textbox = QTextEdit()
        self.results_textbox.setReadOnly(True)
        self.results_textbox.setAcceptRichText(True)
        self.results_textbox.setStyleSheet("QTextEdit { border-style: solid; border-width: 0.5px; "
                                           "border-radius: 5px; background-color: Azure  } ")

        # creates a button to start the model run and to open the sidebar for mapping of results
        self.run_button = QPushButton("run model")
        self.map_dialog_button = QPushButton("open map sidebar")

        # arranges all widgets in a grid
        self.grid.addWidget(self.coord_groupbox, 0, 0)
        self.grid.addWidget(self.mc_widgets_groupbox, 0, 1)
        self.grid.addWidget(self.demand_conversion_groupbox, 1, 0)
        self.grid.addWidget(self.results_textbox, 1, 1)
        self.grid.addWidget(self.pipe_groupbox, 2, 0)
        self.grid.addWidget(self.year_groupbox, 3, 0)
        self.grid.addWidget(self.run_button, 4, 1)
        self.grid.addWidget(self.map_dialog_button, 5,1)

        self.window.setLayout(self.grid)

        # hide optional widgets by default at the start of the program
        self.iter_label.hide()
        self.iter_lineedit.hide()
        self.maxpipe_label.hide()
        self.maxpipe_spinbox.hide()

        # because the class is a QMainWindow object we set the UI as the central widget
        self.setCentralWidget(self.window)

        # connecting the toggling of the monte carlo checkbox to slot, extending the parameter inputs
        self.mc_checkbox.stateChanged.connect(self.on_mc_checkbox)

        # connecting the toggling of the pipeline checkbox to slot
        self.pipe_checkbox.stateChanged.connect(self.on_pipeline_checkbox)

        # instance of parameterSet
        self.parameter_set = ParameterSet.ParameterSet()

        self.computing = ui_library.Computing(self.parameter_set)
        self.mc_computing = mc_main.MonteCarloComputing(self.parameter_set)

        # on run button press set parameter values equal to the current contents of their respective widgets
        # and start the run (passing over the parameter values)
        self.run_button.clicked.connect(self.set_long)
        self.run_button.clicked.connect(self.set_lat)
        self.run_button.clicked.connect(self.set_demand)
        self.run_button.clicked.connect(self.set_year)
        self.run_button.clicked.connect(self.set_allow_centralised)
        self.run_button.clicked.connect(self.set_allow_pipeline)
        self.run_button.clicked.connect(self.set_max_pipe_dist)
        self.run_button.clicked.connect(self.set_elec_type)
        self.run_button.clicked.connect(self.single_or_mc)

        # when map dialog button is pressed add a docked widget that allows displaying a map
        self.map_dialog_button.clicked.connect(self.load_new_mapwidget)

    def on_mc_checkbox(self):
        if self.mc_checkbox.isChecked():
            self.iter_label.show()
            self.iter_lineedit.show()

        else:
            self.iter_label.hide()
            self.iter_lineedit.hide()

    def on_pipeline_checkbox(self):
        if self.pipe_checkbox.isChecked():
            self.maxpipe_label.show()
            self.maxpipe_spinbox.show()
        else:
            self.maxpipe_label.hide()
            self.maxpipe_spinbox.hide()

    def single_or_mc(self):
        if self.mc_checkbox.isChecked():
            self.set_iterations()
            # total_cost, generation_cost, solar_cost, wind_cost = self.mc_computing.run_mc_model()
            cheapest_location_df = self.mc_computing.run_mc_model()
            self.results_textbox.setText("Latitude: " + str(cheapest_location_df.iloc[0]['Latitude']))
            self.results_textbox.append("Longitude: " + str(cheapest_location_df.iloc[0]['Longitude']))
            self.results_textbox.append("Electricity production: " + str(cheapest_location_df.iloc[0]['Cheaper source']))
            self.results_textbox.append("total cost per kg H2: " + str(
                self.round_half_up(cheapest_location_df.iloc[0]['Total Cost per kg H2'], decimals=2)) + "€")
            self.results_textbox.append("complete results of the monte-carlo-simulation \nhave been stored in the "
                                         "Results/mc folder")
        else:
            min_cost, mindex, cheapest_source, cheapest_medium, cheapest_elec, final_path = self.computing.run_single_model()
            rounded_cost = self.round_half_up(min_cost, 2)
            self.results_textbox.setText(str(rounded_cost) + "€/kg")
            self.results_textbox.append("Index: " + str(mindex))
            self.results_textbox.append("Cheapest source location: " + str(cheapest_source))
            self.results_textbox.append("Cheapest transport medium: " + str(cheapest_medium))
            self.results_textbox.append("Cheaper electricity: " + str(cheapest_elec))
            self.results_textbox.append("Transport method: " + str(final_path))
            self.results_textbox.append("the complete results have been saved to the Results folder")

    # setter functions for all parameters
    def set_long(self):
        longitude = float(self.long_lineedit.text())
        print("The longitude was set to:" + str(longitude))
        self.parameter_set.longitude = longitude

    def set_lat(self):
        latitude = float(self.lat_lineedit.text())
        print("The latitude was set to:" + str(latitude))
        self.parameter_set.latitude = latitude

    def set_demand(self):
        demand = int(self.hhdemand_spinbox.value())
        print("The yearly demand was set to:" + str(demand))
        self.parameter_set.demand = demand

    def set_year(self):
        year = int(self.year_combo.currentText())
        print("The year was set to:" + str(year))
        self.parameter_set.year = year

    def set_allow_centralised(self):
        centralised = self.conversion_checkbox.isChecked()
        print("Centralised conversion is allowed: " + "true" if centralised else "Centralised conversion is allowed: "
                                                                                 "false")
        self.parameter_set.centralised = centralised

    def set_allow_pipeline(self):
        pipeline = self.pipe_checkbox.isChecked()
        print("Pipelines are allowed: " + str(pipeline))
        self.parameter_set.pipeline = pipeline

    def set_max_pipe_dist(self):
        maxdist = self.maxpipe_spinbox.value()
        print("The maximum pipeline distance was set to:" + str(maxdist))
        self.parameter_set.max_dist = maxdist

    def set_iterations(self):
        iterations = int(self.iter_lineedit.text())
        print("The number of iterations was set to: " + str(iterations))
        self.parameter_set.iterations = iterations

    def set_elec_type(self):
        electrolyzer_type = self.electro_combo.currentText()
        print("The electrolyzer type was set to: " + electrolyzer_type)
        self.parameter_set.electrolyzer_type = electrolyzer_type

    def load_new_mapwidget(self):
        self.display_map = QDockWidget("Load up a map")
        self.file_dialogue = DisplayMap.fileselection()
        self.file_dialogue_layout = QHBoxLayout()
        self.file_dialogue.setLayout(self.file_dialogue_layout)
        self.display_map.setWidget(self.file_dialogue)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.display_map)

    @staticmethod
    def round_half_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier + 0.5) / multiplier


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UiWindow()
    ui.show()

    sys.exit(app.exec())
