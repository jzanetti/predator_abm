from mesa import Agent
from math import sqrt
from process.utils import get_nearest_position, get_random_move_position, chase_or_home, escape_strategy
from process import INITIAL_LOCATIONS, MAP_SIZE, PARAMS
from random import gauss

class Penguin(Agent):
    def __init__(self, unique_id, model, checks: int = 50):
        super().__init__(unique_id, model)
        self.type = "penguin"
        self.id = unique_id
        self.status = "hunt"
        self.energy = int(gauss(mu=PARAMS["penguin"]["energy"], sigma=PARAMS["penguin"]["energy"]/2))
        self.full_speed = True

        proc_check = 0
        while True:
            proc_check += 1
            sigma = max(3, MAP_SIZE / 10.0)
            x = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["penguin"][0], sigma=sigma))))
            y = max(0, min(MAP_SIZE - 1, int(gauss(mu=INITIAL_LOCATIONS["penguin"][1], sigma=sigma))))
            if model.terrain[x][y] == "land":
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
            radius=int(PARAMS["penguin"]["alert"]["escape"]))
        seals_nearby = [agent for agent in neighbors if agent.type == "seal"]
        
        if seals_nearby:
            self.escape(seals_nearby)
        else:
            if self.status == "full":
                new_position = chase_or_home(
                    self.model, 
                    self.pos, 
                    (self.home["x"], self.home["y"]), 
                    PARAMS["penguin"]["speed"]["walk"]) 
                self.model.grid.move_agent(self, new_position)
                self.energy = min(self.energy, self.energy + 1)
            else:
                neighbors = self.model.grid.get_neighbors(
                    self.pos, moore=True, radius=int(PARAMS["penguin"]["alert"]["hunt"]))
                fish_nearby_pos = [agent.pos for agent in neighbors if (agent.type == "fish" and agent.status == "alive")]
                
                if len(fish_nearby_pos) > 0:
                    closest_fish_pos = get_nearest_position(
                        fish_nearby_pos, 
                        self.pos
                    )
                    
                    speed = self.energy_level()

                    new_position = chase_or_home(
                        self.model, 
                        self.pos, 
                        closest_fish_pos, 
                        speed)
                    
                    #if new_position == self.pos:
                    #    print(self.energy)

                    self.hunt(new_position)
                else:
                    self.random_move()

    def random_move(self, new_position = None):
        proc_pos = self.pos
        if new_position is not None:
            proc_pos = new_position
        new_position = get_random_move_position(
            self.model, proc_pos, PARAMS["fish"]["speed"]["walk"])
        self.model.grid.move_agent(self, new_position)

    def escape(self, enemies):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True, 
            include_center=False,
            radius=int(PARAMS["penguin"]["speed"]["run"]))
        land_steps = [pos for pos in possible_steps if self.model.terrain[pos[0]][pos[1]] == "land"]
        if land_steps:
            new_position = self.random.choice(land_steps)
            self.model.grid.move_agent(self, new_position)
        else:
            new_position = escape_strategy(enemies, possible_steps)
            self.model.grid.move_agent(self, new_position)





    def hunt(self, new_position):
        self.model.grid.move_agent(self, new_position)
        cellmates = self.model.grid.get_cell_list_contents([new_position])
        for agent in cellmates:
            if agent.type == "fish":
                agent.status = "dead"
                self.status = "full"
                break

    def energy_level(self):
        if self.energy == PARAMS["penguin"]["energy"]:
            self.full_speed = True
        if self.energy == 0:
            self.full_speed = False

        if self.full_speed:
            speed = PARAMS["penguin"]["speed"]["run"]
            self.energy = max(0, self.energy - 1)
        else:
            speed = PARAMS["penguin"]["speed"]["walk"]
            self.energy = self.energy + 1
        
        return speed

