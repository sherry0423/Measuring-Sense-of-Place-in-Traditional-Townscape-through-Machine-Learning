import osmnx as ox
import matplotlib.pyplot as plt
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

# Function for making directory
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.mkdir(path)


# Configure CRHD format
street_types = ['service', 'residential', 'tertiary_link', 'tertiary', 'secondary_link', 'primary_link',
                'motorway_link', 'secondary', 'trunk', 'primary', 'motorway']

street_widths = {'service': 1,
                 'residential': 1,
                 'tertiary_link': 1,
                 'tertiary': 2,
                 'secondary_link': 2,
                 'primary_link': 2,
                 'motorway_link': 2,
                 'secondary': 3,
                 'trunk': 3,
                 'primary': 4,
                 'motorway': 2.5}

# 保持原始颜色方案
street_colors_w = {'service': 'violet',
                   'residential': 'violet',
                   'tertiary_link': 'violet',
                   'tertiary': 'lavender',
                   'secondary_link': 'lavender',
                   'primary_link': 'lavender',
                   'trunk_link': 'lavender',
                   'motorway_link': 'lavender',
                   'secondary': 'lavender',
                   'trunk': 'lavender',
                   'primary': 'lavender',
                   'motorway': 'lavender'}


water_colors = {
    'river': 'blue',
    'stream': 'blue',
    'canal': 'blue',
    'lake': 'lightcyan'
}


def PlotCRHD(center_point, dist, name=None, save_path=None, dpi=300, format='png'):

    import osmnx as ox
    import matplotlib.pyplot as plt
    import geopandas as gpd
    from shapely.geometry import box

    print(f"Generating CRHD for {name} at {center_point}")

    G = ox.graph_from_point(center_point=center_point, network_type='all', dist=dist)
    gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
    gdf.highway = gdf.highway.map(lambda x: x[0] if isinstance(x, list) else x)

    minx, miny, maxx, maxy = gdf.total_bounds
    bbox = box(minx, miny, maxx, maxy)

    width = maxx - minx
    height = maxy - miny
    aspect_ratio = height / width if width != 0 else 1

    fig, ax = plt.subplots(1, 1, figsize=(6, 6 * aspect_ratio))

    gdf.plot(ax=ax, linewidth=1, edgecolor='violet')
    for stype in street_types:
        if (gdf.highway == stype).any():
            gdf[gdf.highway == stype].plot(
                ax=ax,
                linewidth=street_widths[stype],
                edgecolor=street_colors_w[stype]
            )


    water_gdf, water_bodies = None, None
    try:

        water_gdf = ox.features_from_point(center_point, dist=dist, tags={'waterway': True})
        water_bodies = ox.features_from_point(center_point, dist=dist, tags={'natural': 'water'})

        print(f"{name}: Waterways = {len(water_gdf)}, Water bodies = {len(water_bodies)}")

        if not water_gdf.empty:
            water_gdf = gpd.clip(water_gdf, bbox)

        if not water_bodies.empty:
            water_bodies = gpd.clip(water_bodies, bbox)

    except Exception as e:
        print(f"Warning: No water features found for {name}. Skipping water layer. Error: {e}")


    if water_gdf is not None and not water_gdf.empty and 'waterway' in water_gdf.columns:
        for water_type in water_gdf['waterway'].dropna().unique():
            if water_type in water_colors:
                water_gdf[water_gdf['waterway'] == water_type].plot(
                    ax=ax,
                    color=water_colors[water_type],
                    linewidth=1.5
                )

    if water_bodies is not None and not water_bodies.empty:
        water_bodies.plot(
            ax=ax,
            color='lightcyan',
            edgecolor='none',
            linewidth=0
        )

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    plt.axis('off')

    if save_path:
        filename = os.path.join(save_path, f'{dist}_{name}.{format}')
        plt.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0, format=format)
        plt.close()
    else:
        return fig



save_path = '水乡检验样本_CRWHD_2'
mkdir(save_path)

excel_path = "水乡检验样本.xlsx"  # 确保 Excel 文件存在

try:
    df = pd.read_excel(excel_path, engine="openpyxl")  # 使用 openpyxl 避免报错
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()

for index, row in df.iterrows():
    try:
        name = row['name']
        lat = float(row['latitude'])
        lon = float(row['longitude'])

        PlotCRHD(center_point=(lat, lon),
                 dist=900,
                 name=name,
                 save_path=save_path)

    except Exception as e:
        print(f"Error processing {row}: {e}")

print('CRHD images generated successfully!')

