import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from os.path import exists, join
from os import makedirs, listdir
from process import LAND_LOCATIONS
from PIL import Image

def simple_vis(output: DataFrame, output_dir = "img"):

    if not exists(output_dir):
        makedirs(output_dir)

    # Define colors for different animal types
    colors = {'fish': 'green', 'penguin': 'blue', "seal": "red"}

    # Define markers for different statuses
    markers = {"alive": "o", 'hunt': 'o', 'dead': 'x', "full": "*"}  # Add more statuses if needed

    for timestep in range(int(output["time"].min()), output["time"].max()):
        proc_output = output[output["time"] == timestep]

        # Create the plot
        plt.figure(figsize=(10, 10))
        # Add brown region for 15 < x < 100 and 30 < y < 50
        plt.gca().add_patch(plt.Rectangle(
            (LAND_LOCATIONS[0][0], LAND_LOCATIONS[1][0]), 
            LAND_LOCATIONS[0][1] - LAND_LOCATIONS[0][0],
            LAND_LOCATIONS[1][1] - LAND_LOCATIONS[1][0],
            label='land',
            facecolor='brown', 
            zorder=1))
        # Iterate through unique combinations of type and status
        for animal_type in proc_output["type"].unique():
            for status in proc_output["status"].unique():
                # Filter the DataFrame for this combination
                subset = proc_output[
                    (proc_output["type"] == animal_type) & (proc_output["status"] == status)]
                
                # Skip if no data for this combination
                if len(subset) == 0:
                    continue
                    
                # Plot this subset
                plt.scatter(subset['x'], 
                        subset['y'], 
                        c=colors.get(animal_type, 'gray'),  # Default to gray if type not in colors
                        marker=markers.get(status, '.'),    # Default to dot if status not in markers
                        label=f'{animal_type} ({status})',
                        s=100)  # Size of the markers
        # LAND_LOCATIONS = [(50, 80), (50, 100)]

        # Set the map boundaries [0, 20] for both x and y
        plt.xlim(0, 200)
        plt.ylim(0, 200)

        # Add grid, labels, and legend
        plt.grid(True)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title(f'Timestep {timestep}')
        plt.legend()
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
    
    # Get all PNG files in the folder
    png_files = [f for f in listdir(input_folder) if f.lower().endswith('.png')]
    
    # Sort files to ensure they are in the correct order (e.g., timestep_0, timestep_1, etc.)
    png_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]) if 'timestep_' in x else x)
    
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

