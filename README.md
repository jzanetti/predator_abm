# Predator-Prey Model: Fish, Penguins, and Seals
This ABM model simulates a predator-prey ecosystem involving fish, penguins, and seals. The model visualizes interactions between these animals, with their types and statuses represented by distinct colors and markers.

The simulation is based on several key assumptions:
- Both penguins and seals hunt exclusively in the sea.
- Penguins prey on fish, while seals prey on penguins.
- Penguins leave land to hunt, returning after consuming a fish.
- Seals roam the sea continuously, hunting penguins.
- ....

<div style="display: flex; justify-content: space-around;">
  <img src="etc/animation.gif" alt="Animal Tracking Demo" width="45%">
  <img src="etc/animation1.gif" alt="Animal Tracking Demo" width="45%">
</div>

To set up the working environment, use the provided env.yml file with Conda:

```
conda env create -f env.yml
```
You can adjust the model parameters in `process/__init__.py` to tune the simulation behavior (e.g., population sizes, interaction rates). The visualization uses color coding and marker symbols to represent animal types and their statuses. For example:

- `Fish`: Green
- `Penguin`: Blue
- `Seal`: Red

These colors help distinguish between different animal types when viewing the data. In addition, the status of each animal is represented by a unique marker symbol:

- `Resting/Hunting`: o (circle)
- `Dead`: x (cross)
- `Full (Just had food)`: * (star)

Contact `Sijin Zhang` at _zsjzyhzp@gmail.com_ for more details.