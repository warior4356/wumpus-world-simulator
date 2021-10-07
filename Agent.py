# Agent.py

import sys
import Action
import random
import Search
import Orientation
import math

debug = False
single_step = False

min_world_size = 3
max_world_size = 9
orientations = 4


def find_closest_target(start_location, targets):
    closest_distance = math.inf
    closest = [1, 1]
    for target in targets:
        distance_x = abs(target[0] - start_location[0])
        distance_y = abs(target[1] - start_location[1])
        distance_total = distance_x + distance_y
        print("Target = " + str(target) + " Distance = " + str(distance_total))
        if distance_total < closest_distance:
            closest = target
            closest_distance = distance_total

    return closest


class MySearchEngine(Search.SearchEngine):
    # Define heuristic distance as city block distance plus turns needed
    def HeuristicFunction(self, state, goalState):
        distance_x = abs(state.location[0] - goalState.location[0])
        distance_y = abs(state.location[1] - goalState.location[1])
        # Find turns needed for goal orientation. UNEEDED. LEFT FOR FUTURE PROOFING
        # if state.orientation <= goalState.orientation:
        #     distance_orientation = goalState.orientation - state.orientation
        # else:
        #     distance_orientation = goalState.orientation + orientations - state.orientation
        return distance_x + distance_y


class Agent:
    # Clear spots in memory that are out of bounds
    def clear_invalid_spots(self):
        for spot in self.searchEngine.safeLocations:
            if spot[0] > self.world_size or spot[1] > self.world_size:
                self.searchEngine.RemoveSafeLocation(spot[0], spot[1])
                if [spot[0], spot[1]] in self.frontier:
                    self.frontier = list(filter([spot[0], spot[1]].__ne__, self.frontier))

    # Generate adjacent locations that could be in bounds
    def generate_adjacent(self):
        adjacent = []
        if self.location_x - 1 > 0:
            adjacent.append([self.location_x - 1, self.location_y])
        if self.location_y - 1 > 0:
            adjacent.append([self.location_x, self.location_y - 1])
        if not (self.size_confirmed and self.location_x + 1 > self.world_size):
            adjacent.append([self.location_x + 1, self.location_y])
        if not (self.size_confirmed and self.location_y + 1 > self.world_size):
            adjacent.append([self.location_x, self.location_y + 1])

        return adjacent

    # Updates facing after a left turn
    def turn_left(self):
        left_turn = {
            Orientation.RIGHT: Orientation.UP,
            Orientation.UP: Orientation.LEFT,
            Orientation.LEFT: Orientation.DOWN,
            Orientation.DOWN: Orientation.RIGHT
        }
        self.facing = left_turn[self.facing]

    # Updates facing after a right turn
    def turn_right(self):
        right_turn = {
            Orientation.RIGHT: Orientation.DOWN,
            Orientation.DOWN: Orientation.LEFT,
            Orientation.LEFT: Orientation.UP,
            Orientation.UP: Orientation.RIGHT
        }
        self.facing = right_turn[self.facing]

    # Updates agent information after a move
    def record_move(self):
        # Update position
        if self.facing == Orientation.RIGHT:
            self.location_x = self.location_x + 1
        elif self.facing == Orientation.LEFT:
            self.location_x = self.location_x - 1
        elif self.facing == Orientation.UP:
            self.location_y = self.location_y + 1
        elif self.facing == Orientation.DOWN:
            self.location_y = self.location_y - 1

        # After updating position record the location as safe and visited, also update exploration frontier
        self.searchEngine.AddSafeLocation(self.location_x, self.location_y)
        if [self.location_x, self.location_y] not in self.visited:
            self.visited.append([self.location_x, self.location_y])
        if [self.location_x, self.location_y] in self.frontier:
            self.frontier = list(filter([self.location_x, self.location_y].__ne__, self.frontier))
        self.frontier.extend(spot for spot in self.generate_adjacent() if spot not in self.visited and
                             spot not in self.frontier)
        if [self.location_x, self.location_y] in self.death:
            self.death = list(filter([self.location_x, self.location_y].__ne__, self.death))

        # If we went "out of bounds" expand the world size
        if self.location_x > self.world_size:
            self.world_size = self.location_x
        elif self.location_y > self.world_size:
            self.world_size = self.location_y

        # Respect max world size
        if self.world_size == max_world_size:
            self.size_confirmed = True

    def go_to_exit(self):
        if not (self.location_x == 1 and self.location_y == 1):
            self.actionList = self.searchEngine.FindPath([self.location_x, self.location_y], self.facing,
                                                         [1, 1], Orientation.RIGHT)
            self.current_goal = [1, 1]
        else:
            self.actionList = [5]

    def __init__(self):
        self.searchEngine = MySearchEngine()
        self.gold_location = False
        self.visited = [[1, 1]]
        self.searchEngine.AddSafeLocation(1, 1)
        self.death = []
        self.world_size = min_world_size
        self.size_confirmed = False
        self.get_out = False

        self.facing = Orientation.RIGHT
        self.location_x = 1
        self.location_y = 1
        self.moved = False
        self.gold = False
        self.arrow = True
        self.actionList = []
        self.current_goal = [1, 1]

        self.frontier = self.generate_adjacent()

    def __del__(self):
        pass
    
    def Initialize(self):
        self.facing = Orientation.RIGHT
        self.location_x = 1
        self.location_y = 1
        self.moved = False
        self.gold = False
        self.arrow = True
        self.actionList = []
        self.current_goal = [1, 1]

    def Process(self, percept):
        # Record movement information
        if self.moved:
            # Record successful movement
            if not percept.bump:
                self.record_move()
            # If bump note max world size and stop
            else:
                self.size_confirmed = True
                self.clear_invalid_spots()
                self.actionList = []
        self.moved = False
        if single_step:
            input("Press Enter...")
        if debug:
            print("X = " + str(self.location_x) + " Y = " + str(self.location_y))
            print("facing = " + str(self.facing))

        # Record adjacent safe locations
        if not percept.stench and not percept.breeze:
            adjacent = self.generate_adjacent()
            if debug:
                print("Adjacent = " + str(adjacent))
            for location in adjacent:
                self.searchEngine.AddSafeLocation(location[0], location[1])

        # If there is gold, grab it and stop moving
        if percept.glitter:
            self.gold_location = (self.location_x, self.location_y)
            action = Action.GRAB
            self.gold = True
            self.actionList = []
        # If the agent has the gold on (1,1), leave
        elif self.location_x == 1 and self.location_y == 1 and (self.gold or self.get_out):
            action = Action.CLIMB
        # If the agent smells the wumpus, shoot
        # elif percept.stench and self.arrow:
        #     action = Action.SHOOT
        #     self.arrow = False
        else:
            if debug:
                print("Visited Locations = " + str(self.visited))
                print("Frontier Locations = " + str(self.frontier))
                print("Safe Locations = " + str(self.searchEngine.safeLocations))
            # If at current goal stop, don't worry about turning to face goal orientation, it's a waste of moves for now
            if self.location_x == self.current_goal[0] and self.location_y == self.current_goal[1]:
                self.actionList = []
            # Pick new destination
            if len(self.actionList) == 0:
                # If gold, go to ladder
                if self.gold:
                    self.go_to_exit()

                # If gold location is known
                elif self.gold_location:
                    self.actionList = self.searchEngine.FindPath([self.location_x, self.location_y],
                                                                 self.facing,
                                                                 [self.gold_location[0], self.gold_location[1]],
                                                                 Orientation.DOWN)
                    self.current_goal = [self.gold_location[0], self.gold_location[1]]

                # Explore
                else:
                    # Try to find a safe unvisited location
                    safe_unvisited = [spot for spot in self.frontier if spot in self.searchEngine.safeLocations]
                    if len(safe_unvisited):
                        if debug:
                            print("Safe Unvisited Locations = " + str(safe_unvisited))
                        self.current_goal = find_closest_target([self.location_x, self.location_y], safe_unvisited)
                        self.actionList = self.searchEngine.FindPath([self.location_x, self.location_y],
                                                                     self.facing,
                                                                     [self.current_goal[0], self.current_goal[1]],
                                                                     Orientation.DOWN)

                    # Try to find an unvisited location that is not death
                    else:
                        questionable_unvisited = [spot for spot in self.frontier if spot not in self.death]
                        if len(questionable_unvisited):
                            if debug:
                                print("Questionable Unvisited Locations = " + str(questionable_unvisited))
                            self.current_goal = find_closest_target([self.location_x, self.location_y],
                                                                    questionable_unvisited)
                            self.searchEngine.AddSafeLocation(self.current_goal[0], self.current_goal[1])
                            self.actionList = self.searchEngine.FindPath([self.location_x, self.location_y],
                                                                         self.facing,
                                                                         [self.current_goal[0], self.current_goal[1]],
                                                                         Orientation.DOWN)
                            self.death.append(self.current_goal)
                            self.searchEngine.RemoveSafeLocation(self.current_goal[0], self.current_goal[1])
                        # No way to win, just get out
                        else:
                            self.get_out = True
                            self.go_to_exit()

            # Process queued movement
            if debug:
                print("Current Goal = " + str(self.current_goal))
                print("Actions = " + str(self.actionList))
            action = self.actionList.pop(0)
            if action == Action.GOFORWARD:
                self.moved = True
            elif action == Action.TURNLEFT:
                self.turn_left()
            elif action == Action.TURNRIGHT:
                self.turn_right()
        return action
    
    def GameOver(self, score):
        # if debug:
        #     input("Press Enter...")
        pass
