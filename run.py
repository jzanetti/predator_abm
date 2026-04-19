from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
from process.fish import Fish
from process.penguin import Penguin
from process.seal import Seal
from vis import simple_vis
from random import gauss, random
from pandas import DataFrame
from process import CLIMATE_VARS, MAP_SIZE, POPULATION, INITIAL_LOCATIONS, LAND_LOCATIONS
from process.utils import run_model
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class SealPenguinFishModel(Model):
    def __init__(
            self, 
            N_penguins=POPULATION["penguin"], 
            N_seals=POPULATION["seal"], 
            N_fish=POPULATION["fish"], 
            width=MAP_SIZE, 
            height=MAP_SIZE, 
            init_loc = INITIAL_LOCATIONS):
        
        self.current_step = 0

        self.num_penguins = N_penguins
        self.num_seals = N_seals
        self.num_fish = N_fish
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # Separate terrain grid (water everywhere, land in the middle)
        self.terrain = np.full((width, height), "water", dtype=object)
        self.land_cells = set()
        for proc_land in LAND_LOCATIONS:
            for x in range(proc_land[0][0], proc_land[0][1]):
                for y in range(proc_land[1][0], proc_land[1][1]):
                    self.terrain[x][y] = "land"
                    self.land_cells.add((x, y))

        # Create fish (in water only)
        for i in range(self.num_fish):
            fish = Fish(i, self)
            if fish.home is not None:
                self.grid.place_agent(fish, (fish.home["x"], fish.home["y"]))
                self.schedule.add(fish)

        # Create penguins (in both water and land)
        for i in range(self.num_penguins):
            penguin = Penguin(i, self)
            if penguin.home is not None:
                self.grid.place_agent(penguin, (penguin.home["x"], penguin.home["y"]))
                self.schedule.add(penguin)


        # Create seals (in water only)
        for i in range(self.num_seals):
            seal = Seal(i, self)
            while True:
                x = max(0, min(width - 1, int(gauss(mu=init_loc["seal"][0], sigma=3))))
                y = max(0, min(height - 1, int(gauss(mu=init_loc["seal"][1], sigma=3))))
                if self.terrain[x][y] == "water":
                    self.grid.place_agent(seal, (x, y))
                    self.schedule.add(seal)
                    break

        # Data collector
        self.datacollector = DataCollector(
            {
                "Penguins": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, Penguin)),
                "Fish": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, Fish)),
                "Seals": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, Seal))
            }
        )

    def update_ice_dynamics(self):
        self.current_step += 1
        
        edges_to_melt = []
        for x, y in self.land_cells:
            # Check 4 adjacent directions for water (Von Neumann neighborhood)
            is_edge = False
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height:
                    if self.terrain[nx][ny] == "water":
                        is_edge = True
                        break
            if is_edge:
                edges_to_melt.append((x, y))

        # Apply the stability index probability to the edges
        for mx, my in edges_to_melt:
            if random() < CLIMATE_VARS["ice_stability_index"]:
                self.terrain[mx][my] = "water"
                self.land_cells.remove((mx, my))

    def step(self):

        self.update_ice_dynamics()
        self.datacollector.collect(self)
        self.schedule.step()
        if sum(1 for a in self.schedule.agents if isinstance(a, Penguin)) == 0:
            self.running = False

if __name__ == "__main__":
    model = SealPenguinFishModel()
    output, terrain_history = run_model(model) 
    simple_vis(output, terrain_history)
    print("done")