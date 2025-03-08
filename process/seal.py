from mesa import Agent
from math import sqrt
from process.utils import get_nearest_position, get_random_move_position, chase_or_home
from process import INITIAL_LOCATIONS, MAP_SIZE, PARAMS
from random import gauss

class Seal(Agent):
    def __init__(self, unique_id, model, checks: int = 50):
        super().__init__(unique_id, model)
        self.type = "seal"
        self.id = unique_id
        self.status = "hunt"

        proc_check = 0
        while True:
            proc_check += 1
            sigma = max(3, MAP_SIZE / 10.0)
            x = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["seal"][0], sigma=sigma))))
            y = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["seal"][1], sigma=sigma))))
            if model.terrain[x][y] == "water":
                self.home = {"x": x, "y": y}
                break

            if proc_check > checks:
                self.home = None
                break

    def step(self):

        if self.status == "full":
            self.random_move()
        else:
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=int(PARAMS["seal"]["alert"]["hunt"]))
            penguin_nearby_pos = [agent.pos for agent in neighbors if (agent.type == "penguin" and agent.status != "dead")]
            
            if len(penguin_nearby_pos) > 0:
                closest_penguin_pos = get_nearest_position(
                    penguin_nearby_pos, 
                    self.pos
                )

                new_position = chase_or_home(
                    self.model, 
                    self.pos, 
                    closest_penguin_pos, 
                    PARAMS["penguin"]["speed"]["run"],
                    terrain_type="water") 
                self.hunt(new_position)
            else:
                self.random_move()

    def random_move(self, new_position = None):
        proc_pos = self.pos
        if new_position is not None:
            proc_pos = new_position
        new_position = get_random_move_position(
            self.model, proc_pos, PARAMS["penguin"]["speed"]["walk"], terrain_type = "water")
        self.model.grid.move_agent(self, new_position)

    def hunt(self, new_position):
        self.model.grid.move_agent(self, new_position)
        cellmates = self.model.grid.get_cell_list_contents([new_position])
        for agent in cellmates:
            if agent.type == "penguin":
                agent.status = "dead"
                self.status = "full"
                break

