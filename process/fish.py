from mesa import Agent
from process import MAP_SIZE, INITIAL_LOCATIONS, PARAMS
from random import gauss
from process.utils import escape_strategy, get_random_move_position, chase_or_home

class Fish(Agent):
    def __init__(self, unique_id, model, checks: int = 50):
        super().__init__(unique_id, model)
        self.type = "fish"
        self.id = unique_id
        self.status = "alive"

        proc_check = 0
        while True:
            proc_check += 1
            sigma = max(3, MAP_SIZE / 10.0)
            x = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["fish"][0], sigma=sigma))))
            y = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["fish"][1], sigma=sigma))))
            if model.terrain[x][y] == "water":
                self.home = {"x": x, "y": y}
                break

            if proc_check > checks:
                self.home = None
                break

    def step(self):
        if self.status == "dead":
            return
        neighbors = self.model.grid.get_neighbors(
            self.pos, 
            moore=True, 
            radius=int(PARAMS["fish"]["alert"]["escape"]))
        penguin_nearby = [agent for agent in neighbors if agent.type == "penguin"]

        if penguin_nearby:
            self.escape(penguin_nearby)
        else:
            new_position = chase_or_home(self.model, self.pos, (self.home["x"], self.home["y"]), PARAMS["fish"]["speed"]["walk"], terrain_type="water") 
            self.random_move(new_position=new_position)

    def random_move(self, new_position = None):
        proc_pos = self.pos
        if new_position is not None:
            proc_pos = new_position
        new_position = get_random_move_position(
            self.model, proc_pos, PARAMS["fish"]["speed"]["walk"], terrain_type = "water")
        self.model.grid.move_agent(self, new_position)

    def escape(self, enemies):
        possible_positions = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True, 
            include_center=False, 
            radius=int(PARAMS["fish"]["speed"]["run"]))
        water_positions = [pos for pos in possible_positions if self.model.terrain[pos[0]][pos[1]] == "water"]

        if water_positions:
            new_position = escape_strategy(enemies, water_positions)
            self.model.grid.move_agent(self, new_position)