from sys import argv
import folium
import pandas as pd
import branca

file = argv[1]

df = pd.read_csv(file, delimiter=';')
df.fillna(value=0, inplace=True)

m = folium.Map(
    location=[41.4, 2.17],
    zoom_start=13
)

for row in range(0, len(df.index)+1):
    lat, lon, comments = df.loc[row, 'lat'], df.loc[row, 'lon'], df.loc[row, 'comments']

#    if df.loc[row, 'rate'] == 0:
#        radius = 3
#    else:
    radius = int(df.loc[row, 'rate'])*int(df.loc[row, 'rate'])/2+3

    tooltip = (df.loc[row, 'name']) + ' | ' + str(df.loc[row, 'rate']) + ' Stars | ' + str(int(df.loc[row, 'comments'])) + ' Comments'

    if comments < 10:
        color = '#{:02x}{:02x}{:02x}'.format(255, 215, 0)
    elif comments >= 10 and comments <= 50:
        color = '#{:02x}{:02x}{:02x}'.format(249, 56, 34)
    elif comments > 50 and comments <= 200:
        color = '#{:02x}{:02x}{:02x}'.format(214, 37, 152)
    elif comments > 200 and comments <= 500:
        color = '#{:02x}{:02x}{:02x}'.format(78, 0, 142)
    elif comments > 500:
        color = '#{:02x}{:02x}{:02x}'.format(0, 36, 156)

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        tooltip=tooltip,
        fill=True,
        fill_color=color,
        stroke = False,
        fill_opacity=.5
    ).add_to(m)

colormap = branca.colormap.LinearColormap(colors=[
    (255, 215, 0, 255),
    (249, 56, 34, 255),
    (214, 37, 152, 255),
    (78, 0, 142, 255),
    (0, 36, 156, 255)
]).scale(0, 600)
colormap.caption = 'Color per Comments, Radius per Stars Rate'
colormap.add_to(m)

m.save('map.html')
