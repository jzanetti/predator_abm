from mesa import Agent
from math import sqrt
from process.utils import get_nearest_position, get_random_move_position, chase_or_home, escape_strategy, success_rate
from process import INITIAL_LOCATIONS, MAP_SIZE, PARAMS
from random import gauss

class Penguin(Agent):
    def __init__(self, unique_id, model, checks: int = 50):
        super().__init__(unique_id, model)
        self.type = "penguin"
        self.id = unique_id
        self.status = "hunt"
        max_energy = PARAMS["penguin"]["energy"]["max"]
        self.energy = int(gauss(mu=max_energy, sigma=max_energy/4))
        # self.full_speed = True
        # self.water_travel_distance = 0.0
        self.speed_mode = "walk" # Tracker for differential burn rates


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

    def step(self, return_nearest_land = True):
        if self.status == "dead":
            return
        
        old_pos = self.pos
        self.speed_mode = "walk" # Reset to baseline at the start of each step

        neighbors = self.model.grid.get_neighbors(
            self.pos, 
            moore=True, 
            radius=int(PARAMS["penguin"]["vision"]["escape"]))
        seals_nearby = [agent for agent in neighbors if agent.type == "seal"]
        
        if seals_nearby:
            self.escape(seals_nearby)
        else:
            if self.status == "full":

                if not self.model.land_cells:
                    self.status = "dead" # No ice left in the entire simulation
                    return

                if return_nearest_land:
                    min_dist = float('inf')
                    land_target = None

                    for lx, ly in self.model.land_cells:
                        dist = ((self.pos[0] - lx)**2 + (self.pos[1] - ly)**2)**0.5
                        if dist < min_dist:
                            min_dist = dist
                            land_target = (lx, ly)
                else:
                    land_target = (self.home["x"], self.home["y"])

                # Climate Change Impact: automatically snap to nearest land if current cell melts
                if self.model.terrain[self.pos[0]][self.pos[1]] == "water":
                    if land_target:
                        self.model.grid.move_agent(self, land_target)
                else:
                    new_position = chase_or_home(
                        self.model, 
                        self.pos, 
                        land_target, 
                        PARAMS["penguin"]["speed"]["walk"]) 
                    self.model.grid.move_agent(self, new_position)
                
                # 2. UPDATED HUNT RETURN: Use nested "max" key
                if self.energy <= (PARAMS["penguin"]["energy"]["max"] * 0.5) and self.model.terrain[self.pos[0]][self.pos[1]] == "land":
                    self.status = "hunt"


                # self.energy = min(PARAMS["penguin"]["energy"], self.energy + 1)

                # 3. Return to Sea/Hunt once fully rested on land
                # if self.energy >= PARAMS["penguin"]["energy"] and self.model.terrain[self.pos[0]][self.pos[1]] == "land":
                #    self.status = "hunt"
            else:
                neighbors = self.model.grid.get_neighbors(
                    self.pos, moore=True, radius=int(PARAMS["penguin"]["vision"]["hunt"]))
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

        # ODOMETER LOGIC (Runs at the very end of the step)
        if self.pos != old_pos:
            # Calculate physical distance moved this step
            # dist_moved = ((self.pos[0] - old_pos[0])**2 + (self.pos[1] - old_pos[1])**2)**0.5
            
            current_terrain = self.model.terrain[self.pos[0]][self.pos[1]]
            
            if current_terrain == "water":
                # self.water_travel_distance += dist_moved # Tick up the odometer
                self.energy -= PARAMS["penguin"]["energy"]["burn_rate"]["water"][self.speed_mode]  # Penguins get more exhausted in water
            elif current_terrain == "land":
                # self.water_travel_distance = 0.0  # Reset odometer upon reaching safety
                # self.energy = min(PARAMS["penguin"]["energy"], self.energy + 1)
                self.energy -= PARAMS["penguin"]["energy"]["burn_rate"]["land"]
                
            # Exhaustion check
            # if self.water_travel_distance > PARAMS["penguin"]["max_travel_distance"]:
            #    self.status = "dead"
            if self.energy <= 0:
                self.status = "dead" # Died of starvation/hypothermia

    def random_move(self, new_position = None):
        proc_pos = self.pos
        if new_position is not None:
            proc_pos = new_position
        new_position = get_random_move_position(
            self.model, proc_pos, PARAMS["penguin"]["speed"]["walk"])
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
            if agent.type == "fish" and success_rate(PARAMS["penguin"]["hunt_success_rate"]):
                agent.status = "dead"
                self.status = "full"
                self.energy = PARAMS["penguin"]["energy"]["max"]
                break

    def energy_level(self):
        # 5. UPDATED SPEED TOGGLE: Use nested "max" key and flag the speed mode
        if self.energy > (PARAMS["penguin"]["energy"]["max"] * 0.3):
            self.speed_mode = "run"
            return PARAMS["penguin"]["speed"]["run"]
        else:
            self.speed_mode = "walk"
            return PARAMS["penguin"]["speed"]["walk"]

