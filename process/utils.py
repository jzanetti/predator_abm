
from math import sqrt as math_sqrt
from random import choices as random_choices
from random import choice as random_choice
from pandas import DataFrame
from process import TOTAL_TIMESTEPS
from random import random as random_random
from numpy import linspace as np_linspace   
from numpy import full as np_full
from numpy import flipud as np_flipud
from rasterio import open as rasterio_open
from rasterio.enums import Resampling

def get_terrain_type(width, height) -> str:
    # Separate terrain grid (water everywhere, land based on Basemap TIFF)
    terrain = np_full((width, height), "water", dtype=object)
    land_cells = set()
    
    # 1. Read the downloaded basemap using rasterio
    # Note: Ensure "scott_base.tif" is in the same directory, or provide the correct path.
    with rasterio_open("scott_base.tif") as src:
        # Read the first band (Red/Grayscale) and automatically resample it to MAP_SIZE
        img_data = src.read(
            1, 
            out_shape=(height, width),
            resampling=Resampling.nearest
        )
        
    # 2. Coordinate Alignment: Image origin (0,0) is at the top-left, 
    # but Mesa grids use (0,0) at the bottom-left. We flip the image vertically to match.
    img_data = np_flipud(img_data)
    
    # 3. Apply Threshold: Dark ocean pixels are roughly <50, bright ice is >200.
    # A threshold of 100 perfectly divides land and water.
    for x in range(width):
        for y in range(height):
            # Note numpy arrays are indexed [row, col] which corresponds to [y, x]
            if img_data[y, x] > 100: 
                terrain[x][y] = "land"
                land_cells.add((x, y))

    return terrain, land_cells

def run_model(model) -> DataFrame:
    """Runs a simulation model for 100 steps and collects agent data into a DataFrame.

    Executes the model for 100 time steps, collecting data about each agent's position,
    type, and status at every step. The collected data is organized into a pandas DataFrame.

    Args:
        model: A simulation model object with a `step()` method and a `schedule` attribute
            containing `agents`. Each agent must have `pos` (tuple of x,y coordinates),
            `type`, and `status` attributes.

    Returns:
        DataFrame: A pandas DataFrame with columns:
            - time (int): Simulation step number (0-99)
            - type: Agent type
            - status: Agent status
            - x (float): Agent x-coordinate
            - y (float): Agent y-coordinate

    Raises:
        AttributeError: If model doesn't have required methods/attributes or if agents
            lack required attributes.
        ValueError: If agent.pos doesn't contain exactly 2 coordinates.

    Example:
        >>> class SimpleModel:
        ...     def step(self): pass
        ...     class Schedule:
        ...         agents = [Agent()]  # Where Agent has pos, type, status
        >>> df = run_model(SimpleModel())
        >>> print(df.columns)
        Index(['time', 'type', 'status', 'x', 'y'], dtype='object')
    """
    output = {"id": [], "time": [], "type": [], "status": [], "x": [], "y": [], "terrain": []}

    terrain_history = {}

    for i in range(TOTAL_TIMESTEPS):
        print(f"step {i}")
        model.step()

        terrain_history[i] = list(model.land_cells)

        for agent in model.schedule.agents:
            x, y = agent.pos
            output["id"].append(agent.id)
            output["time"].append(i)
            output["type"].append(agent.type)
            output["status"].append(agent.status )
            output["x"].append(x)
            output["y"].append(y)
            output["terrain"].append(model.terrain[x][y])


    output = DataFrame.from_dict(output)

    return output, terrain_history


def get_nearest_position(
        possible_pos: list, 
        target_pos: tuple,
        possible_ids: list or None = None,
        probabilies: list = [0.3, 0.3, 0.2, 0.1, 0.1]) -> tuple:
    """Selects a position from possible positions based on distance to target and probabilities.

    Calculates Euclidean distances from each possible position to the target position,
    selects the closest positions up to the number of given probabilities, and returns
    one position randomly chosen based on the provided probability weights.

    Args:
        possible_pos (list): List of possible positions, where each position is a tuple of (x, y) coordinates.
        target_pos (tuple): Target position as a tuple of (x, y) coordinates.
        probabilies (list, optional): List of probabilities for random selection. Must match the number
            of selected positions. Defaults to [0.3, 0.3, 0.2, 0.1, 0.1].

    Returns:
        tuple: Selected position (x, y) from possible_pos based on distance and probability.

    Raises:
        ValueError: If possible_pos is empty or if lengths of selected positions and probabilities don't match.
        IndexError: If positions don't have exactly 2 coordinates.

    Example:
        >>> possible = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        >>> target = (2, 1)
        >>> get_nearest_position(possible, target)
        (1, 1)  # Example output, actual result may vary due to randomness
    """
    all_new_positions = []
    for proc_possible_pos in possible_pos:
        proc_dist = math_sqrt(
            (target_pos[0] - proc_possible_pos[0]) ** 2 + (target_pos[1] - proc_possible_pos[1]) ** 2)
        all_new_positions.append(proc_dist)

    if len(all_new_positions) < len(probabilies):
        probabilies = probabilies[0:len(all_new_positions)]
    probabilies = [x / sum(probabilies) for x in probabilies]

    indices, _ = zip(*sorted(
        enumerate(all_new_positions), key=lambda x: x[1])[:len(probabilies)])
    selected_items = [possible_pos[i] for i in indices]

    new_position = random_choices(selected_items, weights=probabilies, k=1)[0]
    
    if possible_ids is None:
        return new_position

    return new_position, possible_ids[possible_pos.index(new_position)]


def escape_strategy(all_enemies, possible_pos: list, probabilies: list = [0.3, 0.3, 0.2, 0.1, 0.1]) -> tuple:
    """Selects an escape position maximizing distance from enemies based on probabilities.

    Calculates the total Euclidean distance from each possible position to all enemies,
    selects the positions with the greatest total distances (up to the number of probabilities),
    and returns one position randomly chosen based on the provided probability weights.

    Args:
        all_enemies: List of enemy objects, each with a `pos` attribute containing (x, y) coordinates.
        possible_pos (list): List of possible escape positions, each a tuple of (x, y) coordinates.
        probabilies (list, optional): List of probabilities for random selection. Must match the number
            of selected positions. Defaults to [0.3, 0.3, 0.2, 0.1, 0.1].

    Returns:
        tuple: Selected escape position (x, y) from possible_pos that maximizes distance from enemies.

    Raises:
        ValueError: If possible_pos or all_enemies is empty, or if lengths of selected positions
            and probabilities don't match.
        AttributeError: If enemy objects lack `pos` attribute.
        IndexError: If positions don't contain exactly 2 coordinates.

    Example:
        >>> class Enemy:
        ...     def __init__(self, x, y): self.pos = (x, y)
        >>> enemies = [Enemy(1, 1), Enemy(2, 2)]
        >>> positions = [(0, 0), (3, 3), (4, 4), (5, 5), (6, 6)]
        >>> escape_strategy(enemies, positions)
        (6, 6)  # Example output, actual result may vary due to randomness
    """

    probabilies = np_linspace(0.3, 0.1, len(all_enemies))
    probabilies = probabilies / sum(probabilies)
    probabilies = probabilies.tolist()

    all_dis = []
    for proc_position in possible_pos:
        total_dis = 0
        for proc_enemy in all_enemies:
            total_dis += math_sqrt((proc_enemy.pos[0] - proc_position[0]) ** 2 + (proc_enemy.pos[1] - proc_position[1]) ** 2)
        all_dis.append(total_dis)

    indices, _ = zip(*sorted(
        enumerate(all_dis), key=lambda x: x[1], reverse=True)[:len(probabilies)])


    selected_items = [possible_pos[i] for i in indices]

    new_position = random_choices(selected_items, weights=probabilies, k=1)[0]

    return new_position


def get_random_move_position(model, proc_pos, speed, terrain_type: str or None = None) -> tuple:
    """
    Selects a random position within a specified radius from the current position.

    Uses the model's grid to get all possible neighboring positions within the given speed
    (radius) and returns one randomly selected position from those options.

    Args:
        model: A simulation model object with a `grid` attribute that has a `get_neighborhood`
            method.
        proc_pos: Current position as a tuple of (x, y) coordinates.
        speed (int): Maximum distance (radius) for possible moves.

    Returns:
        tuple: A randomly selected position (x, y) from the possible neighboring positions.

    Raises:
        AttributeError: If model lacks a `grid` attribute or `get_neighborhood` method.
        ValueError: If speed is negative or proc_pos is invalid for the grid.
        IndexError: If proc_pos doesn't contain exactly 2 coordinates.

    Example:
        >>> class SimpleModel:
        ...     class Grid:
        ...         def get_neighborhood(self, pos, moore=True, include_center=True, radius=1):
        ...             return [(0, 0), (0, 1), (1, 0), (1, 1)]  # Simplified example
        ...     grid = Grid()
        >>> model = SimpleModel()
        >>> get_random_move_position(model, (0, 0), 1)
        (1, 0)  # Example output, actual result may vary due to randomness
    """
    possible_steps = model.grid.get_neighborhood(
        proc_pos, moore=True, include_center=True, radius=int(speed))
    
    if terrain_type is None:
        return random_choice(possible_steps)
    
    terrain_steps = [pos for pos in possible_steps if model.terrain[pos[0]][pos[1]] == terrain_type]
    if terrain_steps:
        new_position = random_choice(terrain_steps)
        return new_position
    else:
        return proc_pos
    

def chase_or_home(model, start_pos, target_pos, speed, terrain_type: str or None = None) -> tuple:
    possible_positions = model.grid.get_neighborhood(
       start_pos, moore=True, include_center=False, radius=int(speed))

    if terrain_type is not None:
        possible_positions = [pos for pos in possible_positions if model.terrain[pos[0]][pos[1]] == terrain_type]

    if possible_positions:
        new_position = get_nearest_position(possible_positions, target_pos)
        return new_position
    
    return start_pos



def success_rate(rate: float = 0.6) -> bool:
    """Determine success based on a given probability rate.

    Args:
        rate (float): The probability of success, between 0.0 and 1.0 (default: 0.6).

    Returns:
        bool: True if the random chance is less than the rate, False otherwise.

    Examples:
        >>> success_rate(0.6)  # Returns True ~60% of the time
        True
        >>> success_rate(0.3)  # Returns True ~30% of the time
        False
    """
    chance = random_random()
    return chance < rate

"""
self.model.grid.move_agent(self, new_position)
cellmates = self.model.grid.get_cell_list_contents([new_position])
for agent in cellmates:
    if agent.type == "fish":
        agent.status = "dead"
        self.status = "full"
        break
"""