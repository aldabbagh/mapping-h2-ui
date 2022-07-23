import sys

import pandas as pd
import numpy as np
from geo_path import *
from generation_costs import *
from print_results import *
from plot_results import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import timeit


class UiLogic(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("H2 mapping UI")
        self.setGeometry(500, 200, 500, 500)

        self.longitude = 0
        self.latitude = 0
        self.demand = 0
        self.year = 2020
        self.centralised = False
        self.pipeline = False
        self.max_dist = 0

        grid = QGridLayout()

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
        grid.addWidget(self.coord_label, 0, 0)
        grid.addLayout(self.long_hbox, 0, 1)
        grid.addLayout(self.lat_hbox, 1, 1)

        grid.addWidget(self.year_label, 3, 0)
        grid.addWidget(self.year_combo, 3, 1)
        grid.addWidget(self.hhdemand_label, 4, 0)
        grid.addWidget(self.hhdemand_spinbox, 4, 1)
        grid.addLayout(self.allow_vbox, 5, 1)
        grid.addWidget(self.maxpipe_label, 6, 0)
        grid.addWidget(self.maxpipe_spinbox, 6, 1)
        grid.addWidget(self.run_button, 7, 3)

        self.setLayout(grid)

        # call the set-functions anytime the editing of the lineedits is done
        self.long_lineedit.editingFinished.connect(self.set_long)
        self.lat_lineedit.editingFinished.connect(self.set_lat)

        # call set demand when the run button is pressed
        self.run_button.clicked.connect(self.set_demand)

        # call set_year everytime a different entry is chosen from the combo box
        self.run_button.clicked.connect(self.set_year)

        # update the centralised and pipeline bools when the run button is pressed
        self.run_button.clicked.connect(self.allow_centralised)
        self.run_button.clicked.connect(self.allow_pipeline)

        self.run_button.clicked.connect(self.set_max_pipe_dist)

        self.run_button.clicked.connect(run_single_model(self.longitude, self.latitude, self.demand,
                                                         self.year, self.centralised, self.pipeline,
                                                         self.max_dist))

    def set_long(self):
        longitude = float(self.long_lineedit.text())
        print("The longitude was set to:" + str(longitude))
        self.longitude = longitude

    def set_lat(self):
        latitude = float(self.lat_lineedit.text())
        print("The latitude was set to:" + str(latitude))
        self.latitude = latitude

    def set_demand(self):
        demand = self.hhdemand_spinbox.value()
        print("The yearly demand was set to:" + demand)
        self.demand = demand

    def set_year(self):
        year = int(self.year_combo.currentText())
        print("The year was set to:" + str(year))
        self.year = year

    def allow_centralised(self):
        centralised = self.conversion_checkbox.isChecked()
        print("Centralised conversion is allowed :" + "true" if centralised else "false" )
        self.centralised = centralised

    def allow_pipeline(self):
        pipeline = self.pipe_checkbox.isChecked()
        print("Pipelines are allowed :" + pipeline)
        self.pipeline = pipeline

    def set_max_pipe_dist(self):
        maxdist = self.maxpipe_spinbox.value()
        print("The maximum pipeline distance was set to:" + maxdist)
        self.max_dist = maxdist


def compute(end_tuple, h2_demand, year, centralised, pipeline, max_pipeline_dist):
    """Executes a single run of the complete model. Takes the desired end location [lat, long], the H2 demand (
    kt/yr), the year, if redistribution is centralised or not, if pipelines are allowed, and the maximum allowed
    pipeline distance (km) as input. Calculates the minimum of (transport + generation) cost for all possible start
    locations to determine the cheapest source of renewable H2. """

    df = pd.read_csv('Data/renewables.csv', index_col=0)

    # Calculate generation and transport costs
    print('Calculating generation costs...')
    df = generation_costs(df, h2_demand, year=year)
    print('Calculating transport costs...')
    df = transport_costs(df, end_tuple, h2_demand, centralised=centralised, pipeline=pipeline,
                         max_pipeline_dist=max_pipeline_dist)

    df['Total Yearly Cost'] = df['Yearly gen. cost'] + df['Yearly Transport Cost']
    df['Total Cost per kg H2'] = df['Gen. cost per kg H2'] + df['Transport Cost per kg H2']

    df.to_csv('Results/' + str(round(end_tuple[0])) + ',' + str(round(end_tuple[1])) + '.csv')

    return df


def run_single_model(latitude, longitude, demand, year, centralised, pipeline, max_dist):
    # Define parameters for the main model
    end_tuple = (latitude, longitude)  # [lat, long]
    h2_demand = demand  # [kt/yr]
    year = year
    centralised = centralised
    pipeline = pipeline
    max_pipeline_dist = max_dist

    # start timer
    start = timeit.default_timer()

    df = compute(end_tuple, h2_demand, year, centralised, pipeline, max_pipeline_dist)

    df.to_csv('Results/final_df.csv')

    # stop timer
    stop = timeit.default_timer()
    print('Total Time: ', stop - start)

    print_basic_results(df)

    get_path(df, end_tuple, centralised, pipeline)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = UiLogic()
    ui.show()
    sys.exit(app.exec())
