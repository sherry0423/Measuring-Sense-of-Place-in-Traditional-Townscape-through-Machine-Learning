import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import box


district_name = "Shanghai, China"

shanghai_boundary = ox.geocode_to_gdf(district_name)

shanghai_admin = ox.geocode_to_gdf([
    "Pudong, Shanghai, China",
    "Huangpu, Shanghai, China",
    "Xuhui, Shanghai, China",
    "Jing'an, Shanghai, China",
    "Changning, Shanghai, China",
    "Yangpu, Shanghai, China",
    "Hongkou, Shanghai, China",
    "Putuo, Shanghai, China",
    "Minhang, Shanghai, China",
    "Baoshan, Shanghai, China",
    "Jiading, Shanghai, China",
    "Songjiang, Shanghai, China",
    "Qingpu, Shanghai, China",
    "Fengxian, Shanghai, China",
    "Jinshan, Shanghai, China"
])

grid_size = 900  # 900 meters

minx, miny, maxx, maxy = shanghai_admin.total_bounds

cols = int((maxx - minx) / (grid_size / 111000)) + 1  # 1度 ≈ 111km
rows = int((maxy - miny) / (grid_size / 111000)) + 1

grid_cells = []
for i in range(cols):
    for j in range(rows):
        x1 = minx + i * (grid_size / 111000)
        y1 = miny + j * (grid_size / 111000)
        x2 = x1 + (grid_size / 111000)
        y2 = y1 + (grid_size / 111000)
        grid_cells.append(box(x1, y1, x2, y2))

grid = gpd.GeoDataFrame({"geometry": grid_cells}, crs=shanghai_admin.crs)

grid = gpd.overlay(grid, shanghai_admin, how="intersection")

grid["center"] = grid.geometry.centroid

grid["latitude"] = grid["center"].y
grid["longitude"] = grid["center"].x
grid["name"] = ["grid_" + str(i) for i in range(len(grid))]

grid_df = grid[["name", "latitude", "longitude"]]
output_file = "Shanghai_900m_Grid_Centers_No_Chongming.xlsx"
grid_df.to_excel(output_file, index=False)

print(f"上海主城区 900m 网格（去掉崇明岛）已生成并保存至 {output_file}")
