import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from os.path import exists, join
from os import makedirs, listdir
from process import LAND_LOCATIONS
from PIL import Image
from pandas import merge as pandas_merge


def plot_summary_charts(output: DataFrame, output_dir="img"):
    """Generates and displays a line chart of the animal statuses over time."""
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Create a figure with two side-by-side plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # --- Plot 1: Fish Status ---
    fish_data = output[output["type"] == "fish"].groupby(["time", "status"]).size().unstack(fill_value=0)
    if "alive" in fish_data: 
        ax1.plot(fish_data.index, fish_data["alive"], label="Alive", color="green", linewidth=2)
    if "dead" in fish_data: 
        ax1.plot(fish_data.index, fish_data["dead"], label="Dead", color="black", linestyle="--")
        
    ax1.set_title("Fish Population Dynamics")
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Count")
    ax1.legend()
    ax1.grid(True)
    
    # --- Plot 2: Penguin Status & Location ---
    penguin_data = output[output["type"] == "penguin"].copy()
    
    # Combine status and terrain for the labels (e.g., "hunt (water)", "full (land)")
    if "terrain" in penguin_data.columns:
        penguin_data["state"] = penguin_data["status"] + " (" + penguin_data["terrain"] + ")"
    else:
        penguin_data["state"] = penguin_data["status"]
        
    penguin_summary = penguin_data.groupby(["time", "state"]).size().unstack(fill_value=0)
    
    for column in penguin_summary.columns:
        ax2.plot(penguin_summary.index, penguin_summary[column], label=column, linewidth=2)
        
    ax2.set_title("Penguin Status & Location")
    ax2.set_xlabel("Time Step")
    ax2.set_ylabel("Count")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    # Save a copy to your img folder, then physically pop the window open
    plt.savefig(os.path.join(output_dir, "summary_charts.png"), bbox_inches="tight")
    plt.close()


def simple_vis(output: DataFrame, terrain_history: dict, output_dir = "img", enable_traceline = True):

    if not exists(output_dir):
        makedirs(output_dir)

    # Define colors for different animal types
    colors = {'fish': 'green', 'penguin': 'blue', "seal": "red"}

    # Define markers for different statuses
    markers = {"alive": "o", 'hunt': 'o', 'dead': 'x', "full": "*"}  # Add more statuses if needed

    for timestep in range(int(output["time"].min()), output["time"].max()):
        if enable_traceline:
            proc_outputs = output[output["time"] <= timestep]
        else:
            proc_outputs = output[output["time"] == timestep]

        # Create the plot
        plt.figure(figsize=(10, 10))
        # Add brown region for 15 < x < 100 and 30 < y < 50


        # NEW: Plot the dynamic land mask
        if terrain_history and timestep in terrain_history:
            land_cells = terrain_history[timestep]
            if land_cells:
                lx, ly = zip(*land_cells)
                # Use square markers ('s') to simulate grid blocks.
                plt.scatter(lx, ly, c='brown', marker='s', s=15, label='land', zorder=1)
        else:
            # Fallback to the old static method if no history is provided
            for proc_land in LAND_LOCATIONS:
                plt.gca().add_patch(plt.Rectangle(
                    (proc_land[0][0], proc_land[1][0]), 
                    proc_land[0][1] - proc_land[0][0],
                    proc_land[1][1] - proc_land[1][0],
                    label='land',
                    facecolor='brown', 
                    zorder=1))
        """
        for proc_land in LAND_LOCATIONS:
            plt.gca().add_patch(plt.Rectangle(
                (proc_land[0][0], proc_land[1][0]), 
                proc_land[0][1] - proc_land[0][0],
                proc_land[1][1] - proc_land[1][0],
                label='land',
                facecolor='brown', 
                zorder=1))
        """
        # Iterate through unique combinations of type and status
        for animal_type in proc_outputs["type"].unique():
            for status in proc_outputs["status"].unique():

                proc_subsets = proc_outputs[proc_outputs["type"] == animal_type]

                proc_subset = proc_subsets[(proc_subsets["time"] == timestep) & (proc_outputs["status"] == status)]

                # Skip if no data for this combination
                if len(proc_subset) == 0:
                    continue
                    
                # Plot the current location
                plt.scatter(proc_subset['x'], 
                        proc_subset['y'], 
                        c=colors.get(animal_type, 'gray'),  # Default to gray if type not in colors
                        marker=markers.get(status, '.'),    # Default to dot if status not in markers
                        label=f'{animal_type} ({status})',
                        s=100)  # Size of the markers
                
                if enable_traceline:
                    if animal_type != "fish":
                        # Plot track lines
                        for id_value, group in proc_subsets.groupby("id"):
                            plt.plot(group["x"], group["y"],  linewidth=0.15, c=colors.get(animal_type, "gray"), alpha=0.15)


        # LAND_LOCATIONS = [(50, 80), (50, 100)]

        # Set the map boundaries [0, 20] for both x and y
        plt.xlim(0, 200)
        plt.ylim(0, 200)

        # Add grid, labels, and legend
        plt.grid(True)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title(f'Timestep {timestep}')
        plt.legend(loc="upper right")
        plt.savefig(join(output_dir, f"timestep_{timestep}.png"), bbox_inches="tight")
        plt.close()
    
    png_to_gif(input_folder=output_dir, output_gif=join(output_dir, "animation.gif"), duration=100)


def png_to_gif(input_folder="img", output_gif="animation.gif", duration=500):
    """
    Convert all PNG files in a folder to a single animated GIF.
    
    Parameters:
    - input_folder: str, path to the folder containing PNG files (default: "img")
    - output_gif: str, path/name of the output GIF file (default: "animation.gif")
    - duration: int, duration of each frame in milliseconds (default: 500)
    """
    
    # Ensure the input folder exists
    if not exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        return

    # Get ONLY the timestep PNG files in the folder
    png_files = [f for f in listdir(input_folder) if f.lower().endswith('.png') and 'timestep_' in f]
    # Sort files to ensure they are in the correct order
    png_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    # Check if there are any PNG files
    if not png_files:
        print(f"No PNG files found in '{input_folder}'.")
        return
    
    # Load all images
    images = []
    for png_file in png_files:
        file_path = join(input_folder, png_file)
        try:
            img = Image.open(file_path)
            # Ensure the image is in RGBA mode (for consistency)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            images.append(img)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    # Check if we have any valid images
    if not images:
        print("No valid PNG images could be loaded.")
        return
    
    # Save as GIF
    try:
        images[0].save(
            output_gif,
            save_all=True,
            append_images=images[1:],  # All images after the first one
            duration=duration,         # Duration of each frame in milliseconds
            loop=0                      # 0 means loop forever
        )
        print(f"GIF saved as '{output_gif}' with {len(images)} frames.")
    except Exception as e:
        print(f"Error saving GIF: {e}")

