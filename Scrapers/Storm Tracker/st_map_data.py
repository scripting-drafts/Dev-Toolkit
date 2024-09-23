# from sys import argv
import folium
import pandas as pd

# https://view.eumetsat.int/geoserver/ows?service=WMS&request=GetMap&version=1.3.0&layers=msg_fes:h60b&styles=&format=image/geotiff&crs=EPSG:4326&bbox=-77,-77,77,77&width=800&height=800
df = pd.read_csv('Samples/bulk0.csv', delimiter=';')

m = folium.Map(
    location=[45.4, 16.17],
    zoom_start=3
)

for row in range(0, len(df.index)):
    lat, lon = df.loc[row, 'lat'], df.loc[row, 'lon']

    tooltip = str(df.loc[row, 'zone'])
    url = str(df.loc[row, 'url'])
    url_frontend = ' '.join([x.capitalize() for x in tooltip.split(' ')] if tooltip[1:] else tooltip.capitalize())

    folium.CircleMarker(
        location=[lat, lon],
        radius=4, # radius
        tooltip=url_frontend,
        fill=True,
        fill_color='#{:02x}{:02x}{:02x}'.format(214, 37, 152),  # color
        stroke = False,
        fill_opacity=.5,
        popup=f'<a href="{url}" target="_blank" >{url_frontend}</a>').add_to(m)

m.save('Samples/mapbulkall.html')
