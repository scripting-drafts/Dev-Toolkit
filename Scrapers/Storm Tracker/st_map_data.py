# from sys import argv
import folium
import pandas as pd
# import branca

df = pd.read_csv('Samples/bulkall.csv', delimiter=';')

m = folium.Map(
    location=[45.4, 16.17],
    zoom_start=3
)

for row in range(0, len(df.index)):
    lat, lon = df.loc[row, 'lat'], df.loc[row, 'lon']

#    if df.loc[row, 'rate'] == 0:
#        radius = 3
#    else:
    # radius = int(df.loc[row, 'rate'])*int(df.loc[row, 'rate'])/2+3

    tooltip = str(df.loc[row, 'zone'])
    url = str(df.loc[row, 'url'])
    url_frontend = ' '.join([x.capitalize() for x in tooltip.split(' ')] if tooltip[1:] else tooltip.capitalize())


    # if comments < 10:
    #     color = '#{:02x}{:02x}{:02x}'.format(255, 215, 0)
    # elif comments >= 10 and comments <= 50:
    #     color = '#{:02x}{:02x}{:02x}'.format(249, 56, 34)
    # elif comments > 50 and comments <= 200:
    #     color = '#{:02x}{:02x}{:02x}'.format(214, 37, 152)
    # elif comments > 200 and comments <= 500:
    #     color = '#{:02x}{:02x}{:02x}'.format(78, 0, 142)
    # elif comments > 500:
    #     color = '#{:02x}{:02x}{:02x}'.format(0, 36, 156)

    folium.CircleMarker(
        location=[lat, lon],
        radius=4, # radius
        tooltip=url_frontend,
        fill=True,
        fill_color='#{:02x}{:02x}{:02x}'.format(214, 37, 152),  # color
        stroke = False,
        fill_opacity=.5,
        popup=f'<a href="{url}" target="_blank" >{url_frontend}</a>').add_to(m)


## LLEGENDA
# colormap = branca.colormap.LinearColormap(colors=[
#     (255, 215, 0, 255),
#     (249, 56, 34, 255),
#     (214, 37, 152, 255),
#     (78, 0, 142, 255),
#     (0, 36, 156, 255)
# ]).scale(0, 600)

# colormap.caption = 'Color per Comments, Radius per Stars Rate'
# colormap.add_to(m)

m.save('Samples/mapbulkall.html')
