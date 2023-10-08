import plotly.io as pio
import webbrowser
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go

# Your data processing code
key = 'b57a993d7cec7ce1b9b0d4978c10d6d7'
kaz_url = 'https://firms.modaps.eosdis.nasa.gov/api/country/csv/' + key + '/VIIRS_SNPP_NRT/KAZ/2/2023-10-07'
df_kaz = pd.read_csv(kaz_url)
df_kaz['acq_time_new'] = pd.to_datetime(df_kaz['acq_date'] + ' ' + df_kaz['acq_time'].astype(str).str.zfill(4), format='%Y-%m-%d %H%M')

# Find the latest fire
latest_fire = df_kaz[df_kaz['acq_time_new'] == df_kaz['acq_time_new'].max()]
latest_fire_datetime_str = latest_fire['acq_time_new'].dt.strftime('%Y-%m-%d %H:%M').values[0]
# Your geospatial data processing code
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

gdf = gpd.GeoDataFrame(
    df_kaz,
    geometry=gpd.points_from_xy(df_kaz.longitude, df_kaz.latitude),
    crs='EPSG:4326' 
)


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

country_name = 'Kazakhstan' 

selected_country = world[world['name'] == country_name]

gdf['dot_size'] = gdf['scan'] * gdf['track']

fig = px.choropleth_mapbox(
    selected_country,
    geojson=selected_country.geometry.__geo_interface__,
    locations=selected_country.index,
    hover_name="name",
    color_discrete_sequence=[px.colors.qualitative.Pastel2[2]],
    title=f'{country_name} wildfires',
    mapbox_style="carto-positron",
    center={"lat": selected_country.centroid.y.values[0], "lon": selected_country.centroid.x.values[0]},
    opacity=0.6,
    zoom=4,
)
df_kaz['acq_time_new_str'] = df_kaz['acq_time_new'].dt.strftime('%Y-%m-%d %H:%M')

scatter = go.Scattermapbox(
    lat=df_kaz['latitude'],
    lon=df_kaz['longitude'],
    mode='markers',
    marker=dict(
        size=gdf['dot_size']*80,  
        color=df_kaz['bright_ti4'],  
        colorscale='reds', 
        colorbar=dict(
            title='Intensity',
            x=0.95,
            len=0.7,
        ),
    ),
    text=df_kaz['acq_time_new_str'],
    hovertemplate='<b>Date&Time:</b> %{text}<br>'
                  '<b>Intensity:</b> %{marker.color:.2f}<br>'
                  '<b>Latitude:</b> %{lat:.2f}<br>'
                  '<b>Longitude:</b> %{lon:.2f}<br>'
                  '<b>Size:</b> %{marker.size:.2f}', 
)
fig.add_trace(scatter)


# Save the Plotly figure as an HTML file
html_file = "wildfire_map.html"
pio.write_html(fig, html_file)

# Create a simple HTML template to wrap your plot
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wildfire Map</title>
    <style>
        /* Reset some default styles */
        body, html {{
            margin: 0;
            padding: 0;
        }}

        /* Global styles */
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        h1 {{
            font-size: 28px;
            margin-bottom: 20px;
            color: #333;
        }}

        /* Custom styles for the Plotly plot iframe */
        .plot-iframe {{
            width: 100%;
            height: 500px;
            border: none;
        }}

        /* Add your own custom styles here */
    </style>
</head>
<body>
    <div class="container">
        <h1>Kazakhstan Wildfires</h1>
        <!-- Embed your Plotly plot here -->
        <iframe class="plot-iframe" src="{html_file}"></iframe>
        
        <!-- Display information about the latest fire -->
        <h2>Latest Fire Information</h2>
        <p><b>Date:</b> {latest_fire_datetime_str}</p>
        <p><b>Intensity:</b> {latest_fire['bright_ti4'].values[0]:.2f}</p>
        <p><b>Latitude:</b> {latest_fire['latitude'].values[0]:.2f}</p>
        <p><b>Longitude:</b> {latest_fire['longitude'].values[0]:.2f}</p>
        
        <!-- Add more content or iframes as needed -->
        <!-- Example additional iframe -->
        <h2>Drought Monitoring</h2>
        <iframe class="plot-iframe" frameborder="0" scrolling="no" allowfullscreen src="https://arcg.is/1XSiuj0"></iframe>
    </div>
</body>
</html>
"""

# Save the HTML template to a file
with open("wildfire_website.html", "w") as html_template_file:
    html_template_file.write(html_template)

# Open the HTML file in a web browser
webbrowser.open("wildfire_website.html")
print("Website HTML file created: wildfire_website.html")
