"""
Generalized behavior for random walking, one grid cell at a time.
"""

from mesa import Agent


class RandomWalker(Agent):
    """
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    """

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, pos, model, moore=True):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def random_move(self):
        # Moves to a random possible cell
        next_moves = []
        for i in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        # Save all the the possible movements
                        if((self.pos[0]+i)>=0 and (self.pos[1]+y)>=0 and (self.pos[0]+i)<=19 and (self.pos[1]+y)<=19 and
                            ((self.pos[0]+i)!=self.pos[0] and (self.pos[1]+y!=self.pos[1]))): 
                            next_moves.append((self.pos[0]+i, self.pos[1]+y)) 
        
        next_move = self.random.choice(next_moves)
        # Now move to the random adjacent cell
        self.model.grid.move_agent(self, next_move)

    def move_position(self, position):
        # Moves to the "position"
        self.model.grid.move_agent(self, position)
