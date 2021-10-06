# Agent.py

import sys
import Action
import random

class Agent:
    # Updates facing after a left turn
    def turn_left(self):
        left_turn = {
            "E": "N",
            "N": "W",
            "W": "S",
            "S": "E"
        }
        self.facing = left_turn[self.facing]

    # Updates facing after a right turn
    def turn_right(self):
        right_turn = {
            "E": "S",
            "S": "W",
            "W": "N",
            "N": "E"
        }
        self.facing = right_turn[self.facing]

    # Updates position after a move
    def record_move(self):
        if self.facing == "E":
            self.location_x = self.location_x + 1
        elif self.facing == "W":
            self.location_x = self.location_x - 1
        elif self.facing == "N":
            self.location_y = self.location_y + 1
        elif self.facing == "S":
            self.location_y = self.location_y - 1

    def __init__(self):
        self.debug = True
    
    def __del__(self):
        pass
    
    def Initialize(self):
        self.facing = "E"
        self.location_x = 1
        self.location_y = 1
        self.moved = False
        self.gold = False
        self.arrow = True
    
    def Process(self, percept):
        # Record successful movements
        if self.moved and not percept.bump:
            self.record_move()
        self.moved = False
        if self.debug:
            print("X = " + str(self.location_x) + " Y = " + str(self.location_y))
            print("facing = " + str(self.facing))
            input("Next? ")

        # If there is gold, grab it
        if percept.glitter:
            action = Action.GRAB
            self.gold = True
        # If the agent has the gold on (1,1), leave
        elif self.location_x == 1 and self.location_y == 1 and self.gold:
            action = Action.CLIMB
        # If the agent smells the wumpus, shoot
        elif percept.stench and self.arrow:
            action = Action.SHOOT
            self.arrow = False
        # Random movement
        else:
            # Pick a random number between 0 and 2 (inclusive)
            think = random.randint(0, 2)
            if self.debug:
                print("Think = " + str(think))
            # If the number is 0, go forward
            if think == 0:
                action = Action.GOFORWARD
                self.moved = True
            # If the number is 1, turn left
            elif think == 1:
                action = Action.TURNLEFT
                self.turn_left()
            # If the number is 2, turn right
            elif think == 2:
                action = Action.TURNRIGHT
                self.turn_right()
        return action
    
    def GameOver(self, score):
        pass
