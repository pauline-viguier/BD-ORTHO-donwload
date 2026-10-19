#!/usr/bin/env python3

### USAGE: python select_tiles_by_poly.py <dir_tiles> <file_polygon>



import os
from glob import glob
import geopandas as gpd
from shapely.geometry import box
import rasterio as rio
import sys

TILE_EXTENSION = ".jp2"  # Change this if your tiles have a different extension
SELECTION_MARK = "MARKED"  # Suffix to add to selected tiles





def select_tiles(dir_tiles: str, file_polygon: str) -> list[str]:

    all_tiles = sorted(glob(os.path.join(dir_tiles, f"*{TILE_EXTENSION}")))
    print(f"Total tiles found: {len(all_tiles)}")

    polygons = gpd.read_file(file_polygon)
    print(f"Total polygons found: {len(polygons)}")

    selected_tiles = []
    for tile_path in all_tiles:
        with rio.open(tile_path) as src:
            # change to EPSG:4326 if your polygons are in that CRS
            if src.crs.to_string() != polygons.crs.to_string():
                print(f"CRS mismatch: tile {tile_path} has CRS {src.crs}, but polygons have CRS {polygons.crs}. Reprojecting polygons.")
                polygons = polygons.to_crs(src.crs)
            tile_bounds = box(*src.bounds)
            for _, polygon in polygons.iterrows():
                if tile_bounds.intersects(polygon.geometry):
                    selected_tiles.append(tile_path)
                    break

    print(f"Selected tiles: {len(selected_tiles)}")
    return selected_tiles

def mark_selection(selected_tiles: list[str]) -> None:
    for tile_path in selected_tiles:
        base, ext = os.path.splitext(tile_path)
        new_name = f"{base}_{SELECTION_MARK}{ext}"
        os.rename(tile_path, new_name)
        
    print(f"Marked {len(selected_tiles)} tiles with '{SELECTION_MARK}'.")





if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python select_tiles_by_poly.py <dir_tiles> <file_polygon>")
        sys.exit(1)

    selection = select_tiles(
        dir_tiles=sys.argv[1],
        file_polygon=sys.argv[2]
    )
    mark_selection(selection)