import io
import os
import geopandas as gpd
import shapefile as shp  # Requires the pyshp package
import openrouteservice
from openrouteservice import convert
import folium
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import *
from print_results import *

sys.path.append("/shapefile_to_network/main/convertor")
sys.path.append("/shapefile_to_network/main/shortest_paths")

from shapefile_to_network.main.convertor.GraphSimplify import GraphSimplify
from shapefile_to_network.main.convertor.GraphConvertor import GraphConvertor
from shapefile_to_network.main.shortest_paths.ShortestPath import ShortestPath
from shapefile_to_network.main.metrics.Centrality import Centrality

from shapely import speedups
speedups.disable()

# this application opens a dialog in which a file from results can be selected
class fileselection(QWidget):
    def __init__(self, parent=None):
        super(fileselection, self).__init__(parent)

        self.setGeometry(800, 500, 200, 100)
        self.layout = QVBoxLayout()
        self.b = QPushButton("select a .csv-file")
        self.map_button = QPushButton("display map")
        self.layout.addWidget(self.b)
        self.layout.addWidget(self.map_button)
        self.b.clicked.connect(self.filedialog)
        self.map_button.clicked.connect(self.display_map)
        self.setWindowTitle("data selection demo")
        self.setLayout(self.layout)
        self.df = pd.DataFrame()

    def filedialog(self):
        d = QFileDialog()
        relpathtoresults = os.path.join(os.path.dirname(__file__), r'Results')
        activefile = QFileDialog.getOpenFileName(d, "select csv", relpathtoresults)

        # getOpenFilename somehow returns a tuple, therefore we only access the first element
        df = pd.read_csv(activefile[0])
        pd.DataFrame.info(df)
        self.df = df

    def display_map(self):
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

        # Call graph_convertor function to convert the input shapefile into road network and save the newly created shapefile
        # into specifed output_dir along with list of nodes and edges in .csv files
        network = graph_convertor_obj.graph_convertor()

        edges = gpd.read_file(input_file)
        nodes = gpd.read_file('Data/shipping/nodes/New Shape/nodes.shp')

        sf = shp.Reader('Data/shipping/shipping_routes/shipping_routes.shp')

        df_port_index = pd.read_csv('Data/port_index.csv', index_col=0)
        df_ports = pd.read_csv('Data/path/ports.csv')

        port_coords = self.create_port_coordinates(df_ports)

        start_plant_tuple = (self.cheapest_source)
        end_plant_tuple = (self.end_tuple)

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
        self.layout.addWidget(w)
        w.resize(640, 480)
        w.show()


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


def main():
    app = QApplication(sys.argv)
    w = fileselection()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

