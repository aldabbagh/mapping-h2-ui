import io
import sys, os
from pathlib import Path
import geopandas as gpd
import shapefile as shp
import plotly
import openrouteservice
from openrouteservice import convert
import folium
import timeit
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import *
from print_results import *
sys.path.append("/shapefile_to_network/main/convertor")
sys.path.append("/shapefile_to_network/main/shortest_paths")
from shapefile_to_network.main.convertor.GraphConvertor import GraphConvertor
from shapefile_to_network.main.shortest_paths.ShortestPath import ShortestPath
from shapely import speedups

speedups.disable()


class Visualizing(QWidget):
    """this application opens a dialog in which a file from results can be selected"""
    def __init__(self, parent=None):
        super(Visualizing, self).__init__(parent)

        self.setGeometry(800, 500, 200, 100)
        window_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane {"
                                "border: 1px solid black;"
                                "background: MintCream }"
                                
                                "QTabWidget::tab-bar:top {"
                                "top: 1px }"    
                                
                                "QTabWidget::tab-bar:bottom {"
                                "bottom: 1px }"

                                "QTabWidget::tab-bar:left {"
                                "right: 1px }"

                                "QTabWidget::tab-bar:right {"
                                "left: 1px} "
 
                                "QTabBar::tab {"
                                "border: 1px solid black }"

                                "QTabBar::tab:selected {"
                                "background: DarkSeaGreen }"

                                "QTabBar::tab:!selected {"
                                "background: LightSteelBlue }"

                                "QTabBar::tab:!selected:hover {"
                                "background: #999 }"

                                "QTabBar::tab:top:!selected {"
                                "margin-top: 3px }"

                                "QTabBar::tab:bottom:!selected {"
                                "margin-bottom: 3px }"

                                "QTabBar::tab:top, QTabBar::tab:bottom {"
                                "min-width: 8ex;"
                                "margin-right: -1px;"
                                "padding: 5px 10px 5px 10px }"

                                "QTabBar::tab:top:selected {"
                                "border-bottom-color: none }"

                                "QTabBar::tab:bottom:selected {"
                                "border-top-color: none }"

                                "QTabBar::tab:top:last, QTabBar::tab:bottom:last,"
                                "QTabBar::tab:top:only-one, QTabBar::tab:bottom:only-one {"
                                "margin-right: 0 }"

                                "QTabBar::tab:left:!selected {"
                                "margin-right: 3px }"

                                "QTabBar::tab:right:!selected {"
                                "margin-left: 3px }"

                                "QTabBar::tab:left, QTabBar::tab:right {"
                                "min-height: 8ex;"
                                "margin-bottom: -1px;"
                                "padding: 10px 5px 10px 5px }"

                                "QTabBar::tab:left:selected {"
                                "border-left-color: none }"

                                "QTabBar::tab:right:selected {"
                                "border-right-color: none }"

                                "QTabBar::tab:left:last, QTabBar::tab:right:last,"
                                "QTabBar::tab:left:only-one, QTabBar::tab:right:only-one {"
                                "margin-bottom: 0}")


        self.tab1 = QWidget()
        self.tab2 = QWidget()

        # this ComboBox has to be
        self.world_heatmap_result_metric_combo = QComboBox()
        self.world_heatmap_result_metric_combo.addItems(['Total Cost per kg H2', 'Gen. cost per kg H2',
                                                         'Transport Cost per kg H2', 'Cheapest Medium'])
        self.tab1ui()
        self.tab2ui()

        self.tabs.addTab(self.tab1, "single run")
        self.tabs.addTab(self.tab2, "Monte-Carlo Sim.")

        self.setWindowTitle("Data Visualisation")
        self.df = pd.DataFrame()
        self.mc_df = pd.DataFrame()

        window_layout.addWidget(self.tabs)
        self.setLayout(window_layout)


    def tab1ui(self):
        self.tab1_layout = QVBoxLayout()
        b = QPushButton("select a .csv-file")
        map_button = QPushButton("display route on world map")
        world_heatmap_button = QPushButton("display H2-price on world map")

        world_heatmap_result_metric_label = QLabel(" Plot the following result metric :")

        world_heatmap_result_metric_combo_layout = QHBoxLayout()
        world_heatmap_result_metric_combo_layout.addWidget(world_heatmap_result_metric_label)
        world_heatmap_result_metric_combo_layout.addWidget(self.world_heatmap_result_metric_combo)

        self.tab1_layout.addWidget(b)
        self.tab1_layout.addWidget(map_button)
        self.tab1_layout.addLayout(world_heatmap_result_metric_combo_layout)
        self.tab1_layout.addWidget(world_heatmap_button)

        b.clicked.connect(self.filedialog)
        map_button.clicked.connect(self.display_map)
        world_heatmap_button.clicked.connect(self.plot_world_results_single_run)

        self.tab1.setLayout(self.tab1_layout)
        self.tab1.setStyleSheet(
            "QPushButton {background-color: DarkSeaGreen}"
            "QComboBox {background-color: DarkSeaGreen;"
            "padding: 2px 1px 2px 5px }"
        )

    def tab2ui(self):
        self.tab2_layout = QVBoxLayout()
        b = QPushButton("select a .csv-file")
        world_heatmap_button = QPushButton("display mean of H2-price for all locations")
        self.tab2_layout.addWidget(b)
        self.tab2_layout.addWidget(world_heatmap_button)

        b.clicked.connect(self.mc_filedialog)
        world_heatmap_button.clicked.connect(self.plot_world_results_mc)

        self.tab2.setLayout(self.tab2_layout)

        self.tab2.setStyleSheet(
            "QPushButton {background-color: DarkSeaGreen}"
        )

    def filedialog(self):
        """A file dialog is created where it's possible to select a file in the 'Results' folder."""
        d = QFileDialog()
        active_file = QFileDialog.getOpenFileName(d, "select csv")

        if active_file[0] == '':
            pass
        else:
            # getOpenFilename somehow returns a tuple, therefore we only access the first element
            df = pd.read_csv(active_file[0])
            pd.DataFrame.info(df)
            self.df = df

    def mc_filedialog(self):
        mc_d = QFileDialog()

        active_file = QFileDialog.getOpenFileName(mc_d, "select csv")

        if active_file[0] == '':
            pass
        else:
            df = pd.read_csv(active_file[0], header=None)
            pd.DataFrame.info(df)
            self.mc_df = df

    def display_map(self):
        """This Method can display the resulting transport route for the cheapest production location.
        Every combination of transport methods can be displayed. Trucking between two points is
        computed via openrouteservice. A pipeline is visualised by a straight line, since they're
        hypothetical in this model. Transport by ship can happen along a shipping network derived
        from real shipping paths obtained from tracking vessels."""

        # finds the place of the cheapest cost and stores its location as a tuple
        # stores the desired location as a tuple (location is the same for all rows of the df)
        min_cost = min(self.df['Total Cost per kg H2'])
        mindex = self.df.index.values[self.df['Total Cost per kg H2'] == min_cost]
        mindex = mindex[0]
        self.cheapest_source = (self.df['Latitude'][mindex], self.df['Longitude'][mindex])
        self.end_tuple = (self.df['End Plant Latitude'][mindex], self.df['End Plant Longitude'][mindex])
        transport_mode = self.df['Transport Mode'][mindex]

        # Create GraphConvertor object by passing the path of input shapefile and the output directory
        input_file = 'Data/shipping/shipping_routes/shipping_routes.shp'
        output_dir = 'Data/shipping/nodes'

        graph_convertor_obj = GraphConvertor(input_file, output_dir)

        # Call graph_convertor function to convert the input shapefile into road network and
        # save the newly created shapefile into specifed output_dir along with list of nodes and edges in .csv files
        network = graph_convertor_obj.graph_convertor()

        edges = gpd.read_file(input_file)
        nodes = gpd.read_file('Data/shipping/nodes/New Shape/nodes.shp')

        sf = shp.Reader('Data/shipping/shipping_routes/shipping_routes.shp')

        df_port_index = pd.read_csv('Data/port_index.csv', index_col=0)
        df_ports = pd.read_csv('Data/path/ports.csv')

        port_coords = self.create_port_coordinates(df_ports)

        start_plant_tuple = self.cheapest_source
        end_plant_tuple = self.end_tuple

        start_plant_tuple = start_plant_tuple[::-1]
        end_plant_tuple = end_plant_tuple[::-1]

        coords = (start_plant_tuple, end_plant_tuple)

        if "Ship" not in transport_mode:
            # no transport by ship -> either by truck or by pipeline

            if "Truck" in transport_mode:
                client = openrouteservice.Client(key='5b3ce3597851110001cf62487a8aff99152f40b9abb404dbb3a74056')

                res = client.directions(coords, radiuses=[5000, 5000])
                geometry = client.directions(coords, radiuses=[5000, 5000])['routes'][0]['geometry']
                decoded = convert.decode_polyline(geometry)

                distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
                duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"

                m = folium.Map(location=start_plant_tuple[::-1], zoom_start=2, control_scale=True,
                               tiles="cartodbpositron", zoom_control=False)
                folium.GeoJson(data=decoded).add_to(m)

                folium.Marker(
                    location=list(coords[0][::-1]),
                    popup="Start point",
                    icon=folium.Icon(icon='map-marker', color="red"),
                ).add_to(m)

                folium.Marker(
                    location=list(coords[1][::-1]),
                    popup="End point",
                    icon=folium.Icon(icon='map-marker', color="black"),
                ).add_to(m)
            else:
                m = folium.Map(location=start_plant_tuple[::-1], zoom_start=2, control_scale=True,
                               tiles="cartodbpositron", zoom_control=False)
                folium.Marker(
                    location=list(coords[0][::-1]),
                    popup="Start pipe",
                    icon=folium.Icon(icon='map-marker', color="lightgreen"),
                ).add_to(m)

                folium.Marker(
                    location=list(coords[1][::-1]),
                    popup="End pipe",
                    icon=folium.Icon(icon='map-marker', color="cadetblue"),
                ).add_to(m)

                pipe_full = [[start_plant_tuple[1], start_plant_tuple[0]],
                             [end_plant_tuple[1], end_plant_tuple[0]]]
                my_PolyLine = folium.PolyLine(locations=pipe_full, weight=3, color='purple')
                m.add_child(my_PolyLine)

        elif "Truck Ship" in transport_mode:
            # Find the closest port to the start point
            distance, index = spatial.KDTree(port_coords).query(start_plant_tuple)  # Needs [long, lat]
            start_port_code = df_ports.at[index, 'Unnamed: 0']
            print('Start Port Code: ' + str(start_port_code))
            start_port_tuple = port_coords[index][::-1]  # Outputs [long, lat]
            print('Start Port Tuple: ' + str(start_port_tuple))

            # Find the closest port to the end point
            distance, index = spatial.KDTree(port_coords).query(end_plant_tuple)  # Needs [long, lat]
            end_port_code = df_ports.at[index, 'Unnamed: 0']
            print('End Port Code: ' + str(end_port_code))
            end_port_tuple = port_coords[index][::-1]  # Outputs [long, lat]
            print('End Port Tuple: ' + str(end_port_tuple))

            # display route from production location to start port
            start_plant_to_port = (start_plant_tuple, start_port_tuple[::-1])
            client = openrouteservice.Client(key='5b3ce3597851110001cf62487a8aff99152f40b9abb404dbb3a74056')

            res = client.directions(start_plant_to_port, radiuses=[5000, 5000])
            geometry = client.directions(start_plant_to_port, radiuses=[5000, 5000])['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)

            distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
                round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
            duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
                round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"

            m = folium.Map(location=start_plant_tuple[::-1], zoom_start=2, control_scale=True,
                           tiles="cartodbpositron", zoom_control=False)
            folium.GeoJson(data=decoded).add_to(m)

            folium.Marker(
                location=list(start_plant_to_port[0][::-1]),
                popup="Start point",
                icon=folium.Icon(icon='map-marker', color="red"),
            ).add_to(m)

            folium.Marker(
                location=list(start_plant_to_port[1][::-1]),
                popup="End point",
                icon=folium.Icon(icon='map-marker', color="black"),
            ).add_to(m)

            # Create ShortestPath object by passing all required parameters listed below
            g = network
            alpha = 0.1
            graph_buffer = 300
            point_buffer = 1
            break_point = 1  # Upper limit to save computation time

            # start timer
            start = timeit.default_timer()

            shortest_path_obj = ShortestPath(g, alpha, graph_buffer, point_buffer, break_point)

            # Run alpha_times_shortestpath function to calculate number of paths which are alpha times the shortest path
            start_tuple_port = start_port_tuple
            end_tuple_port = end_port_tuple

            shortest_paths, buffered_graph = shortest_path_obj.find_shortest_paths(start_tuple_port, end_tuple_port)

            shortest_dis = min(shortest_paths.keys())
            print('shortest distance: ' + str(shortest_dis))
            shortest_path = shortest_paths[shortest_dis]
            new_start_coord = shortest_path[0]
            print('new start coord: ' + str(new_start_coord))
            new_end_coord = shortest_path[len(shortest_path) - 1]
            print('new end coord: ' + str(new_end_coord))

            # stop timer
            stop = timeit.default_timer()

            print('Computation Time for shortest path: ', stop - start)

            # create dataframe to plot shortest path
            df = pd.DataFrame(shortest_path)
            lat = df[0]
            lon = df[1]

            # store all relevant coordinates for the shipping route inside coords_ship
            coords_ship = [start_tuple_port]
            for i in range(len(lon)):
                coords_ship.append([lat[i], lon[i]])
            coords_ship.append(end_tuple_port)

            # plot shipping route as a line on the map
            ship_route = [coords_ship]
            ship_PolyLine = folium.PolyLine(locations=ship_route, weight=3, color='seagreen')
            m.add_child(ship_PolyLine)

            if 'Pipe' in transport_mode:
                folium.Marker(
                    location=end_tuple_port[::-1],
                    popup="Start pipe",
                    icon=folium.Icon(icon='map-marker', color="lightgreen"),
                ).add_to(m)

                folium.Marker(
                    location=end_plant_tuple[::-1],
                    popup="End pipe",
                    icon=folium.Icon(icon='map-marker', color="cadetblue"),
                ).add_to(m)

                pipe_full = [end_tuple_port, end_plant_tuple]
                pipe_PolyLine = folium.PolyLine(locations=pipe_full, weight=3, color='purple')
                m.add_child(pipe_PolyLine)
            else:
                client = openrouteservice.Client(key='5b3ce3597851110001cf62487a8aff99152f40b9abb404dbb3a74056')
                end_port_to_end_plant = [end_tuple_port[::-1], end_plant_tuple]

                res = client.directions(end_port_to_end_plant, radiuses=[5000, 5000])
                geometry2 = client.directions(end_port_to_end_plant, radiuses=[5000, 5000])['routes'][0]['geometry']
                decoded2 = convert.decode_polyline(geometry2)

                distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
                duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"

                folium.GeoJson(data=decoded2).add_to(m)

                folium.Marker(
                    location=list(end_port_to_end_plant[0][::-1]),
                    popup="Start point",
                    icon=folium.Icon(icon='map-marker', color="red"),
                ).add_to(m)

                folium.Marker(
                    location=list(end_port_to_end_plant[1][::-1]),
                    popup="End point",
                    icon=folium.Icon(icon='map-marker', color="black"),
                ).add_to(m)

        elif 'Pipe Ship' in transport_mode:
            # Find the closest port to the start point
            distance, index = spatial.KDTree(port_coords).query(start_plant_tuple)  # Needs [long, lat]
            start_port_code = df_ports.at[index, 'Unnamed: 0']
            print('Start Port Code: ' + str(start_port_code))
            start_port_tuple = port_coords[index][::-1]  # Outputs [long, lat]
            print('Start Port Tuple: ' + str(start_port_tuple))

            # Find the closest port to the end point
            distance, index = spatial.KDTree(port_coords).query(end_plant_tuple)  # Needs [long, lat]
            end_port_code = df_ports.at[index, 'Unnamed: 0']
            print('End Port Code: ' + str(end_port_code))
            end_port_tuple = port_coords[index][::-1]  # Outputs [long, lat]
            print('End Port Tuple: ' + str(end_port_tuple))

            # display route from production location to start port
            start_plant_to_port = (start_plant_tuple, start_port_tuple[::-1])

            m = folium.Map(location=start_plant_tuple[::-1], zoom_start=2, control_scale=True,
                           tiles="cartodbpositron", zoom_control=False)

            folium.Marker(
                location=list(start_plant_to_port[0][::-1]),
                popup="Start point",
                icon=folium.Icon(icon='map-marker', color="red"),
            ).add_to(m)

            folium.Marker(
                location=list(start_plant_to_port[1][::-1]),
                popup="End point",
                icon=folium.Icon(icon='map-marker', color="black"),
            ).add_to(m)

            pipe_to_port = [start_plant_tuple[::-1], start_port_tuple]
            pipe_PolyLine = folium.PolyLine(locations=pipe_to_port, weight=3, color='purple')
            m.add_child(pipe_PolyLine)

            # Create ShortestPath object by passing all required parameters listed below
            g = network
            alpha = 0.1
            graph_buffer = 300
            point_buffer = 1
            break_point = 1  # Upper limit to save computation time

            # start timer
            start = timeit.default_timer()

            shortest_path_obj = ShortestPath(g, alpha, graph_buffer, point_buffer, break_point)

            # Run alpha_times_shortestpath function to calculate number of paths which are alpha times the shortest path
            start_tuple_port = start_port_tuple
            end_tuple_port = end_port_tuple

            shortest_paths, buffered_graph = shortest_path_obj.find_shortest_paths(start_tuple_port, end_tuple_port)

            shortest_dis = min(shortest_paths.keys())
            print('shortest distance: ' + str(shortest_dis))
            shortest_path = shortest_paths[shortest_dis]
            new_start_coord = shortest_path[0]
            print('new start coord: ' + str(new_start_coord))
            new_end_coord = shortest_path[len(shortest_path) - 1]
            print('new end coord: ' + str(new_end_coord))

            # stop timer
            stop = timeit.default_timer()

            print('Computation Time for shortest path: ', stop - start)

            # create dataframe to plot shortest path
            df = pd.DataFrame(shortest_path)
            lat = df[0]
            lon = df[1]

            # store all relevant coordinates for the shipping route inside coords_ship
            coords_ship = [start_tuple_port]
            for i in range(len(lon)):
                coords_ship.append([lat[i], lon[i]])
            coords_ship.append(end_tuple_port)

            # plot shipping route as a line on the map
            ship_route = [coords_ship]
            ship_PolyLine = folium.PolyLine(locations=ship_route, weight=3, color='seagreen')
            m.add_child(ship_PolyLine)

            if 'Truck' in transport_mode:
                client = openrouteservice.Client(key='5b3ce3597851110001cf62487a8aff99152f40b9abb404dbb3a74056')
                end_port_to_end_plant = [end_tuple_port[::-1], end_plant_tuple]

                res = client.directions(end_port_to_end_plant, radiuses=[5000, 5000])
                geometry2 = client.directions(end_port_to_end_plant, radiuses=[5000, 5000])['routes'][0]['geometry']
                decoded2 = convert.decode_polyline(geometry2)

                distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['distance'] / 1000, 1)) + " Km </strong>" + "</h4></b>"
                duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>" + str(
                    round(res['routes'][0]['summary']['duration'] / 60, 1)) + " Mins. </strong>" + "</h4></b>"

                folium.GeoJson(data=decoded2).add_to(m)

                folium.Marker(
                    location=list(end_port_to_end_plant[0][::-1]),
                    popup="Start point",
                    icon=folium.Icon(icon='map-marker', color="red"),
                ).add_to(m)

                folium.Marker(
                    location=list(end_port_to_end_plant[1][::-1]),
                    popup="End point",
                    icon=folium.Icon(icon='map-marker', color="black"),
                ).add_to(m)
            else:
                folium.Marker(
                    location=end_tuple_port,
                    popup="Start pipe",
                    icon=folium.Icon(icon='map-marker', color="lightgreen"),
                ).add_to(m)

                folium.Marker(
                    location=end_plant_tuple[::-1],
                    popup="End pipe",
                    icon=folium.Icon(icon='map-marker', color="cadetblue"),
                ).add_to(m)

                pipe_full = [end_tuple_port, end_plant_tuple[::-1]]
                pipe_PolyLine = folium.PolyLine(locations=pipe_full, weight=3, color='purple')
                m.add_child(pipe_PolyLine)

        data = io.BytesIO()
        m.save(data, close_file=False)

        w = QWebEngineView()
        w.setHtml(data.getvalue().decode())
        self.tab1_layout.addWidget(w)
        w.resize(640, 480)
        w.show()

    def plot_world_results_single_run(self):
        """Plots world map showing various cost metrics for producing H2."""
        data = self.df
        desired_metric = self.world_heatmap_result_metric_combo.currentText()

        if desired_metric == 'Cheapest Medium':
            total = range(len(data))
            for i in total:
                if data.iloc[i, 28] == 'LOHC':
                    data.iloc[i, 28] = 1
                if data.iloc[i, 28] == 'NH3':
                    data.iloc[i, 28] = 2
                if data.iloc[i, 28] == 'H2 Liq':
                    data.iloc[i, 28] = 3
                if data.iloc[i, 28] == 'H2 Gas':
                    data.iloc[i, 28] = 4

            color_schemes = [
                ['#890000', '#890000', '#5c0000'],
                ['#1d79ad', '#1d79ad', '#1d79ad'],
                ['#4f5a90', '#374798', '#30375a'],
                ['#fff4b1', '#ffed86', '#ffdb00']
            ]

            colorscale = self.generate_Discrete_ColourScale(color_schemes)

            x = data.iloc[:, 28]

            fig = go.Figure(data=go.Scattergeo(
                lat=data.loc[:, 'Latitude'],
                lon=data.loc[:, 'Longitude'],
                mode='markers',
                text=x,
                marker=dict(
                    color=x,
                    size=3,
                    colorscale=colorscale,
                )))

            fig.update_layout(
                geo=dict(
                    showland=True,
                    landcolor="rgb(212, 212, 212)",
                    subunitcolor="rgb(255, 255, 255)",
                    countrycolor="rgb(255, 255, 255)",
                    showlakes=True,
                    lakecolor="rgb(255, 255, 255)",
                    showsubunits=True,
                    showcountries=True,
                    projection=dict(
                        type='natural earth'
                    ),
                ),
                title='Cheapest transport medium by location',
                font_color='black',
                font_size=15,
                font_family='Times New Roman',

            )
            html = '<html><body>'
            html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
            html += '</body></html>'

            plot_widget = QWebEngineView()
            plot_widget.setHtml(html)
            self.tab1_layout.addWidget(plot_widget)
            plot_widget.resize(800, 600)
            plot_widget.show()

        else:
            fig = go.Figure(data=go.Scattergeo(
                lat=data.loc[:, 'Latitude'],
                lon=data.loc[:, 'Longitude'],
                mode='markers',
                text=round(data.loc[:, desired_metric], 2),
                marker=dict(
                    color=data.loc[:, desired_metric],
                    size=3,
                    colorscale='Portland',
                    # reversescale = True,
                    colorbar=dict(
                        title=dict(
                                side="right"),
                        outlinecolor="rgba(68, 68, 68, 0)",
                        ticks="outside",
                        showticksuffix="last",
                        dtick=1),

                ),
            ))

            fig.update_layout(
                geo=dict(
                    # scope='europe',
                    showland=True,
                    landcolor="rgb(212, 212, 212)",
                    subunitcolor="rgb(255, 255, 255)",
                    countrycolor="rgb(255, 255, 255)",
                    showlakes=True,
                    lakecolor="rgb(255, 255, 255)",
                    showsubunits=True,
                    showcountries=True,
                    projection=dict(
                        type='natural earth'
                    ),
                ),
                font_color='black',
                font_size=15,
                font_family='Times New Roman'
            )
            fig.add_annotation(x=1.05, y=-0.08,
                               text="Black locations represent transport routes that could not be calculated",
                               showarrow=False)
            fig.add_annotation(x=1, y=0.977,
                               text=desired_metric,
                               font=dict(
                                   size=18),
                               showarrow=False)

            html = '<html><body>'
            html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
            html += '</body></html>'

            plot_widget = QWebEngineView()
            plot_widget.setHtml(html)
            self.tab1_layout.addWidget(plot_widget)
            plot_widget.resize(800, 600)
            plot_widget.show()

    def plot_world_results_mc(self):

        list_locations = pd.read_csv("Data/locationslist.csv")
        data = self.mc_df.mean()
        dataframes = [list_locations[['Latitude', 'Longitude']], data]

        x = pd.concat(dataframes, axis=1)

        fig = go.Figure(data=go.Scattergeo(
            lat=x.loc[:, 'Latitude'],
            lon=x.loc[:, 'Longitude'],
            mode='markers',
            text=round(x.iloc[:, 2], 2),
            marker=dict(
                color=x.iloc[:, 2],
                size=3,
                colorscale='Portland',
                # reversescale = True,
                colorbar=dict(
                    titleside="right",
                    outlinecolor="rgba(68, 68, 68, 0)",
                    ticks="outside",
                    showticksuffix="last",
                    dtick=1)
            ),
        ))

        fig.update_layout(
            geo=dict(
                # scope='europe',
                showland=True,
                landcolor="rgb(212, 212, 212)",
                subunitcolor="rgb(255, 255, 255)",
                countrycolor="rgb(255, 255, 255)",
                showlakes=True,
                lakecolor="rgb(255, 255, 255)",
                showsubunits=True,
                showcountries=True,
                projection=dict(
                    type='natural earth'
                ),
            ),
            # title='Total cost per kg H2 (Eur) for H2 required in Cologne, Germany',
            font_color='black',
            font_size=15,
            font_family='Times New Roman'
        )
        fig.add_annotation(x=1.05, y=-0.08,
                           text="Black locations represent transport routes that could not be calculated",
                           showarrow=False)
        fig.add_annotation(x=1, y=0.977,
                           text="Cost",
                           font=dict(
                               size=18
                           ),
                           showarrow=False)

        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'

        plot_widget = QWebEngineView()
        plot_widget.setHtml(html)
        self.tab2_layout.addWidget(plot_widget)
        plot_widget.resize(800, 600)
        plot_widget.show()

    @staticmethod
    def create_port_coordinates(df_ports):
        """Creates a list of the port co-ordinates that can be used to find the nearest port to any point. Requires no
        input."""

        coords = df_ports['coords'].values.tolist()
        coords = [i.strip('()') for i in coords]
        coords = [i.strip("'),'") for i in coords]
        coords = [i.split(', ') for i in coords]

        coords2 = []
        for i in range(len(coords)):
            li = []
            for j in range(2):
                li.append(float(coords[i][j]))
            coords2.append(li)

        return coords2

    @staticmethod
    def generate_Discrete_ColourScale(colour_set):
        # colour set is a list of lists
        colour_output = []
        num_colours = len(colour_set)
        divisions = 1. / num_colours
        c_index = 0.
        # Loop over the colour set
        for cset in colour_set:
            num_subs = len(cset)
            sub_divisions = divisions / num_subs
            # Loop over the sub colours in this set
            for subcset in cset:
                colour_output.append((c_index, subcset))
                colour_output.append((c_index + sub_divisions -
                                      .001, subcset))
                c_index = c_index + sub_divisions
        colour_output[-1] = (1, colour_output[-1][1])
        return colour_output


def main():
    app = QApplication(sys.argv)
    w = Visualizing()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
