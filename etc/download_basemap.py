

import requests
from pyproj import Transformer
import rasterio
from rasterio.transform import from_bounds
from rasterio.io import MemoryFile

def download_clean_ross_sea_basemap(output_filename="scott_base.tif"):
    # 1. Define the center of the area of interest (Ross Sea)
    lat_center = -77.84922593941945
    lon_center = 166.76707435864458
    
    # 2. Convert Lat/Lon (WGS84) to Antarctic Polar Stereographic (EPSG:3031)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    x_center, y_center = transformer.transform(lon_center, lat_center)
    
    # 3. Define the bounding box in meters (600km x 600km footprint)
    box_size_m = 600_000 
    minx = x_center - (box_size_m / 2)
    maxx = x_center + (box_size_m / 2)
    miny = y_center - (box_size_m / 2)
    maxy = y_center + (box_size_m / 2)
    
    # 4. Set target resolution (e.g., 500 meters per pixel)
    resolution_m = 500
    width = int(box_size_m / resolution_m)
    height = int(box_size_m / resolution_m)
    
    # 5. Esri Polar Antarctic Imagery REST Endpoint (Cloud-free composite)
    export_url = "https://services.arcgisonline.com/ArcGIS/rest/services/Polar/Antarctic_Imagery/MapServer/export"
    params = {
        "bbox": f"{minx},{miny},{maxx},{maxy}",
        "bboxSR": "3031",
        "imageSR": "3031",
        "size": f"{width},{height}",
        "format": "png32",
        "transparent": "false",
        "f": "image" # Tells the API to return the raw image byte stream, not JSON
    }
    
    print("Fetching cloud-free basemap from Esri Polar Services...")
    response = requests.get(export_url, params=params)
    response.raise_for_status()
    
    # 6. Translate the raw image into a georeferenced GeoTIFF
    transform = from_bounds(minx, miny, maxx, maxy, width, height)
    
    with MemoryFile(response.content) as memfile:
        with memfile.open() as src:
            profile = src.profile
            
            # Clean up the profile and enforce a lossless TIFF
            profile.pop('compress', None)
            profile.pop('photometric', None)
            profile.update({
                'driver': 'GTiff',
                'crs': 'EPSG:3031',
                'transform': transform,
                'compress': 'lzw'
            })
            
            with rasterio.open(output_filename, 'w', **profile) as dst:
                dst.write(src.read())
                
    print(f"Success! Saved clean georeferenced basemap to {output_filename}")

if __name__ == "__main__":
    download_clean_ross_sea_basemap()