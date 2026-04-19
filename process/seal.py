from mesa import Agent
from math import sqrt
from process.utils import get_nearest_position, get_random_move_position, chase_or_home, success_rate
from process import INITIAL_LOCATIONS, MAP_SIZE, PARAMS
from random import gauss
from random import choices as random_choices

class Seal(Agent):
    def __init__(self, unique_id, model, checks: int = 50):
        super().__init__(unique_id, model)
        self.type = "seal"
        self.id = unique_id
        self.status = "hunt"
        self.target_id = None
        self.target_pos = None

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
            new_position = chase_or_home(
                self.model, 
                self.pos, 
                (self.home["x"], self.home["y"]), 
                PARAMS["seal"]["speed"]["walk"]) 
            self.model.grid.move_agent(self, new_position)
            # self.random_move()
        else:
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, radius=int(PARAMS["seal"]["vision"]["hunt"]))
            penguin_nearby = [(agent.id, agent.pos) for agent in neighbors if (agent.type == "penguin" and agent.status != "dead")]
            # only keep penguin nearby in the sea
            penguin_nearby = [
                proc_penguin_nearby for proc_penguin_nearby in 
                penguin_nearby if self.model.terrain[
                    proc_penguin_nearby[1][0]][proc_penguin_nearby[1][1]] == "water"]

            penguin_nearby_id = []
            penguin_nearby_pos = []
            for proc_penguin_nearby in penguin_nearby:
                penguin_nearby_id.append(proc_penguin_nearby[0])
                penguin_nearby_pos.append(proc_penguin_nearby[1])

            if len(penguin_nearby) > 0:
                
                if self.target_id in penguin_nearby_id:
                    # observe other 3 penguins while hunting the target penguin (note this selection may include target penguin itself)
                    target_pengun_pos = penguin_nearby_pos[penguin_nearby_id.index(self.target_id)]
                    
                    random_penguin_nearby_loc = random_choices(range(len(penguin_nearby)), k = 3)
                    selected_random_penguin_id = [penguin_nearby_id[i] for i in random_penguin_nearby_loc]
                    selected_random_penguin_pos = [penguin_nearby_pos[i] for i in random_penguin_nearby_loc]

                    # increase the possibility that the target penguin will be chosen
                    penguin_nearby_id = [self.target_id] * 3 + selected_random_penguin_id
                    penguin_nearby_pos = [target_pengun_pos] * 3 + selected_random_penguin_pos

                closest_penguin_pos, closest_penguin_id = get_nearest_position(
                    penguin_nearby_pos, 
                    self.pos,
                    possible_ids = penguin_nearby_id
                )

                self.target_id = closest_penguin_id
                self.target_pos = closest_penguin_pos

                new_position = chase_or_home(
                    self.model, 
                    self.pos, 
                    closest_penguin_pos, 
                    PARAMS["seal"]["speed"]["run"],
                    terrain_type="water") 
                self.hunt(new_position)
            else:
                self.random_move()

    def random_move(self, new_position = None):
        proc_pos = self.pos
        if new_position is not None:
            proc_pos = new_position
        new_position = get_random_move_position(
            self.model, proc_pos, PARAMS["seal"]["speed"]["walk"], terrain_type = "water")
        self.model.grid.move_agent(self, new_position)

    def hunt(self, new_position):
        self.model.grid.move_agent(self, new_position)
        cellmates = self.model.grid.get_cell_list_contents([new_position])
        for agent in cellmates:
            if agent.type == "penguin" and success_rate(PARAMS["seal"]["hunt_success_rate"]):
                agent.status = "dead"
                self.status = "full"
                break

