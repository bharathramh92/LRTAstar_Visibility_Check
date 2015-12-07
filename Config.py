import numpy as np
import matplotlib
from matplotlib.patches import Polygon as mPolygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib import animation



import matplotlib.animation as animation

from matplotlib.axes import Axes

import json
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
import copy
import sys


class Environment:

    def __init__(self, input_file, factor=1):
        self.plot_obstacles_polygon = []
        self.obs_list = []
        self.obs_polygon = MultiPolygon()
        self.initial_state, self.goal_state = [], []
        self.resolution = 0
        self.read_env_from_file(input_file)
        self.factor = factor


    def read_env_from_file(self, input_file):
        try:
            with open(input_file, mode='r', encoding='utf-8') as a_file:
                environment = json.loads(a_file.read())
        except FileNotFoundError:
            print("File not found for JSON")
            exit(1)
        except ValueError:
            print("Invalid JSON")
            exit(1)
        except Exception:
            print("Unable to process input file")
            exit(1)
        try:
            environment['resolution'] and environment['obstacles']
            environment['initial_state'] and environment['goal_state']
        except KeyError:
            print("Invalid Environment definition")
            exit(1)
        self.initial_state, self.goal_state = environment['initial_state'], environment['goal_state']
        self.resolution = environment['resolution']
        temp_polygon_list = []
        for obs in environment['obstacles']:
            if not obs.get('shape') and obs.get('property') and obs['property'].get('vertices'):
                print("Shape element not present for the obstacles")
                continue
            if obs['shape'] == 'polygon':
                # print("Polygon with vertices %s" %(np.array(obs['property']['vertices'])/100))
                polygon = mPolygon(np.array(obs['property']['vertices']))
                temp_polygon_list.append(Polygon(obs['property']['vertices']))
                self.plot_obstacles_polygon.append(polygon)
                self.obs_list.append(obs['property']['vertices'])
            else:
                print("Undefined shape")
                break
        self.obs_polygon = MultiPolygon(temp_polygon_list)

    def is_point_inside(self, xy):
        """
        :param xy: tuple with x coordinate as first element and y coordinate as second element
        :return: True if the point is inside the obstacles and False if it isn't
        """
        return Point(xy[0], xy[1]).within(self.obs_polygon)

    def is_line_inside(self, xy_start, xy_end):
        line = LineString([xy_start, xy_end])
        return self.obs_polygon.contains(line) or self.obs_polygon.touches(line) or self.obs_polygon.crosses(line)

    def draw_env(self, path, key_xy,k_value ):
        fig, ax = plt.subplots()
        # fig, ax = plt.axes()
        x_path, y_path = [], []

        for ls in path:
            x_path.append(key_xy(ls)[0])
            y_path.append(key_xy(ls)[1])


        colors = 100*np.random.rand(len(self.plot_obstacles_polygon))
        p = PatchCollection(self.plot_obstacles_polygon, cmap=matplotlib.cm.jet, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        plt.colorbar(p)
        print("x_path is " + str(x_path[0])+" "+str(x_path[1]))
        print("y_path is " + str(y_path))

        plt.plot([self.initial_state[0]], [self.initial_state[1]], 'bs', self.goal_state[0], self.goal_state[1], 'g^')
            # ,
                 # x_path, y_path, '')
        plt.axis([0, self.resolution, 0, self.resolution])

        # plt.plot(X_point,y_point)
        plt.arrow(x_path[0], y_path[0], x_path[1]-x_path[0], y_path[1]-y_path[0], fc="k", ec="k", head_width=1.55, head_length=1.1)


        plt.title("figure"+ str(k_value)+".png")

        fig.savefig("figure"+ str(k_value)+".png",format = 'png',dpi=fig.dpi)

        k_value+=1


    def get_apprx_visible_vertices(self, xy_robot):
        if self.is_point_inside(xy_robot):
            print("Invalid robot position")
            return None
        pool = copy.deepcopy(self.obs_list)
        pool.append([self.goal_state])
        visible_vertices, visible_lines = [], []

        for obj in pool:
            for vertex in obj:
                vertex = tuple(vertex)
                if vertex == xy_robot:
                    continue
                crosses, line = self.visibility_line(xy_robot, vertex)
                if not crosses:
                    visible_lines.append(line)
        visible_vertices.extend([x.xy[0][1], x.xy[1][1]] for x in visible_lines)
        return visible_vertices

    def get_actual_visible_vertices(self, xy_robot):
        if self.is_point_inside(xy_robot):
            print("Invalid robot position")
            return None
        pool = copy.deepcopy(self.obs_list)
        pool.append([self.goal_state])
        visible_vertices, line_robot_vertices = [], {}

        def line_slope(xy1, xy2):
            return (xy2[1] - xy1[1])/(xy2[0] - xy1[0]) if (xy2[0] - xy1[0]) != 0 else sys.maxsize

        for obj in pool:
            for vertex in obj:
                crosses, line = self.visibility_line(xy_robot, vertex)
                if not crosses:
                    if line_slope(xy_robot, vertex) in line_robot_vertices:
                        if line.length < line_robot_vertices[line_slope(xy_robot, vertex)].length:
                            line_robot_vertices[line_slope(xy_robot, vertex)] = line
                    else:
                        line_robot_vertices[line_slope(xy_robot, vertex)] = line
        visible_vertices.extend([x.xy[0][1], x.xy[1][1]] for x in line_robot_vertices.values())
        return visible_vertices

    def visibility_line(self, xy_start, xy_end):
        line = LineString([xy_start, xy_end])
        return self.obs_polygon.crosses(line) or self.obs_polygon.contains(line), line

    def __str__(self):
        return "Obstacle list: %s\nInitial State: %s\nGoal State: %s\nResolution: %d\n" \
               % ([cord.xy for cord in self.plot_obstacles_polygon], self.initial_state, self.goal_state, self.resolution)


