import numpy as np
import matplotlib
from matplotlib.patches import Polygon as mPolygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.axes import Axes

import json
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
from shapely.wkt import loads
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
            print(input_file)
            with open(input_file, mode='r', encoding='utf-8') as a_file:
                environment = json.loads(a_file.read())
        except FileNotFoundError as fl:
            print("File not found", fl)
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
        x_path, y_path = [], []

        for ls in path:
            x_path.append(key_xy(ls)[0])
            y_path.append(key_xy(ls)[1])

        colors = 100*np.random.rand(len(self.plot_obstacles_polygon))
        p = PatchCollection(self.plot_obstacles_polygon, cmap=matplotlib.cm.jet, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        plt.colorbar(p)
        # print("x_path is " + str(x_path[0])+" "+str(x_path[1]))
        # print("y_path is " + str(y_path))

        plt.plot([self.initial_state[0]], [self.initial_state[1]], 'bs', self.goal_state[0], self.goal_state[1], 'g^')
            # ,
                 # x_path, y_path, '')
        plt.axis([0, self.resolution, 0, self.resolution])

        # plt.plot(X_point,y_point)
        plt.arrow(x_path[0], y_path[0], x_path[1]-x_path[0], y_path[1]-y_path[0], fc="k", ec="k", head_width=1.55, head_length=1.1)


        plt.title("figure"+ str(k_value)+".jpeg")

        fig.savefig("figure"+ str(k_value),format = 'jpeg',dpi=fig.dpi)

    def animate_path(self, path, key_xy):
        fig, ax = plt.subplots()

        colors = 100*np.random.rand(len(self.plot_obstacles_polygon))
        p = PatchCollection(self.plot_obstacles_polygon, cmap=matplotlib.cm.jet, alpha=0.4)
        p.set_array(np.array(colors))
        ax.add_collection(p)
        plt.colorbar(p)

        plt.plot([self.initial_state[0]], [self.initial_state[1]], 'bs', self.goal_state[0], self.goal_state[1], 'g^')
        plt.axis([0, self.resolution, 0, self.resolution])

        x_0, y_0 = path[0].position[0], path[0].position[1]
        x_1, y_1 = path[0 + 1].position[0], path[0 + 1].position[1]
        print((x_0, x_1), (y_0, y_1))
        # line, = ax.plot((x_0, x_1), (y_0, y_1))
        dx, dy = x_1 - x_0, y_0 - y_1
        qv = ax.quiver(x_0, y_0, dx, dy, angles='xy',scale_units='xy',scale=1)
        # arrow = ax.arrow(x_0, y_0, dx, dy, fc="k", ec="k", head_width=1.55, head_length=1.1)
        def animate(i):
            x_init, y_init = path[i].position[0], path[i].position[1]
            x_f, y_f = path[i + 1].position[0], path[i + 1].position[1]
            dx, dy = x_f - x_init, y_f - y_init
            # line.set_ydata((y_init, y_f))
            # line.set_xdata((x_init, x_f))
            # ax.arrow.remove(qv)
            # qv.set_offsets(qv.get_offsets() * (dx, dy))
            # qv.remove()
            qv.set_UVC(np.array(dx), np.array(dy))
            # print(qv.C)
            # print(qv.U, " ", qv.V, " ", type(qv.U))
            # print(np.array(dx))
            # qv.U = np.array(dx)
            # qv.V = np.array(y_f)
            qv.set_offsets((x_init, y_init))
            # print(qv.X, qv.Y, qv.U, qv.V)
            # qv.X = x_init
            # qv.
            # qv = ax.quiver(x_init, y_init, dx, dy, angles='xy',scale_units='xy',scale=1)
            return qv

        anim = animation.FuncAnimation(fig, animate, frames=range(0, len(path)-1), interval=500)
        # movieWriter = matplotlib.animation.MovieWriter(fps=5, codec=None, bitrate=None, extra_args=None, metadata=None)
        # mywriter = animation.FFMpegWriter()
        # anim.save('mymovie.mp4', writer=mywriter)

        # FFMpegWriter = animation.writers['avconv']
        # metadata = dict(title='Movie Test', artist='Matplotlib',
        #                 comment='Movie support!')
        # writer = FFMpegWriter(fps=15, metadata=metadata)
        # anim.save('demoanimation.gif', writer='avconf', fps=4, dpi=1)
        plt.show()

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


