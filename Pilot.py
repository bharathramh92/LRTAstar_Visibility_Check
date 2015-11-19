from queue import PriorityQueue
from Config import Environment
from State import State
import math


def main():
    env = Environment("Environment1.json")
    # obstacle_list = set()  #Known obstacles for the robot
    print(env.get_apprx_visible_vertices(env.initial_state))
    traversal_path = []


    # def local_search(present_state):
    goal_state = State(env.goal_state)
    initial_state = State(env.initial_state, GOAL_STATE=goal_state)
    traversed = {}
    # print(initial_state.successor(env.get_apprx_visible_vertices(initial_state.position)))

    def hill_climbing(state):
        pq = PriorityQueue()
        successor_list = state.successor(env.get_apprx_visible_vertices(state.position))
        for successor in successor_list:
            if successor.position in traversed:
                successor = traversed[successor.position]
            pq.put(successor)
        next_state = pq.get()
        if next_state.is_goal():
            return next_state
        if next_state.position in traversed:
            next_state.h += math.sqrt((state.position[0] - next_state.position[0])**2 +
                                      (state.position[1] - next_state.position[1]) ** 2)
        traversed[next_state.position] = next_state
        traversal_path.append(next_state)

        # print("next state ", next_state)
        return hill_climbing(next_state)
    traversal_path.append(initial_state)
    goal = hill_climbing(initial_state)
    if goal is not None:
        traversal_path.append(goal)
        print("Goal found, total stops are %d" % (len(traversal_path)))

    print(traversal_path)
    env.draw_env(traversal_path, lambda x: x.position)
    # local_search(env.initial_state)

    # def a_star(present_state):
    #     open_set_pq, open_set, closed_set = PriorityQueue(), {}, {}

    # goal_state = State(env.goal_state, env.resolution, obstacle_list)
    # initial_state = State(present_state, env.resolution, obstacle_list, GOAL_STATE=goal_state)
        # open_set_pq.put(initial_state)
        # open_set[initial_state.position] = initial_state
        # state_examinations, state_generated = 0, 1
        # while True:
        #     if not open_set_pq.empty():
        #         current_state = open_set_pq.get()
        #         state_examinations += 1
        #         open_set.pop(current_state.position)
        #         closed_set[current_state.position] = current_state
        #     else:
        #         print('No solution')
        #         exit()
        #     if current_state.position == goal_state.position:
        #         return current_state, state_examinations, state_generated
        #     else:
        #         for x in current_state.successor():
        #             if x.position in closed_set or x.position in obstacle_list:
        #                 continue
        #             g_cost = current_state.g + 1      #STEP_COST --> 1
        #             if x.position not in open_set or g_cost < open_set[x.position].g:
        #                 x.g = g_cost
        #                 x.parent = current_state
        #                 if x.position not in open_set:
        #                     state_generated += 1
        #                     open_set[x.position] = x
        #                     open_set_pq.put(x)

    # def lrta_star(present_state, total_restarts_lrta_star):
    #     print("lrta_star restart number: ", total_restarts_lrta_star)
    #
    #     def tree_traversal():
    #         current_state, state_examinations, state_generated = a_star(present_state)
    #         path = []
    #         while current_state.parent is not None:
    #             path.append(current_state)
    #             current_state = current_state.parent
    #         path.reverse()
    #         return path, state_generated, state_examinations
    #     path, state_generated, state_examinations = tree_traversal()
    #
    #     def go_to_next_position(i):
    #         # print("i: %d path %s" %(i, path))
    #         current_position_traversed = path[i]
    #         x, y = current_position_traversed.position[0], current_position_traversed.position[1]
    #         print(x, y, env.is_point_inside_box(x, y))
    #         if env.is_point_inside_box(x, y) or current_position_traversed.position == tuple(env.goal_state):
    #             return current_position_traversed
    #         else:
    #             traversal_path.append(current_position_traversed)
    #             return go_to_next_position(i + 1)
    #     current_position = go_to_next_position(0)
    #     if current_position.position == tuple(env.goal_state):
    #         print(traversal_path)
    #         env.draw_env(traversal_path)
    #         # print('Total steps were %d, generated %d and expanded %d ' % (len(path), state_generated, state_examinations))
    #
    #     else:
    #         obstacle_list.add(current_position.position)
    #         print("obstacle list is ", obstacle_list)
    #         lrta_star(current_position.parent.position, total_restarts_lrta_star + 1)
    #
    # lrta_star(env.initial_state, 0)
    # print(env.internal_is_point_inside(16, 13))

if __name__ == '__main__':
    main()