# from sys import argv
from io import BytesIO
from PIL import Image
import folium
import pandas as pd
from pyproj import Transformer
import base64

t = Transformer.from_crs(4216, 4326)    # (4216, 4326)      default 3857
eur_latitude, eur_longitude = 45.4, 16.17
aa_latitude, aa_longitude = 44., 135.
latitude, longitude = aa_latitude, aa_longitude

# https://view.eumetsat.int/geoserver/ows?service=WMS&request=GetMap&version=1.3.0&layers=msg_fes:h60b&styles=&format=image/geotiff&crs=EPSG:4326&bbox=-77,-77,77,77&width=800&height=800
df = pd.read_csv('coords_asia_img.csv', delimiter=';')  # 'Samples/bulkall.csv'

tomtom_API_Key = 'XrZAUB7qYWfBWHgPfJi9msE3Hl7FlwsB'
# https://tile.gbif.org/{srs}/{tileset}/{z}/{x}/{y}{format}{params}
# https://map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}'
# https://api.tomtom.com/map/1/wms/?key={Your_API_Key}&service=WMS&version=1.1.1&request=GetMap&bbox=1.355233,42.982261,24.980233,56.526017&srs=EPSG:4326&width=1305&height=748&layers=basic&styles=&format=image/png
m = folium.Map(
    location=[latitude, longitude], # list(t.transform(latitude, longitude))
    zoom_start=5,
    # control_scale=True,
    # max_bounds=True,
    # max_zoom=2,
    # max_native_zoom=1,
    # crs='EPSG4326',
    # tiles='https://tile.gbif.org/4326/omt/0/1/0@4x.png?style=gbif-natural-en',
    # tiles = f'http://localhost:8080/demo/wms/?srs=EPSG%3A4326&format=image%2Fpng&wms_layer=osm',
    attr="<a href=https://github.com/scripting-drafts/>scripting-drafts</a>"
)

def get_frame(url,url_frontend,img_url,width,height):
    html = """ 
            <!doctype html>
        <html>
        <iframe id="myIFrame" width="{}" height="{}" src={}""".format(width,height,img_url) + """ frameborder="0"></iframe>
        <script type="text/javascript">
        var resizeIFrame = function(event) {
            var loc = document.location;
            if (event.origin != loc.protocol + '//' + loc.host) return;

            var myIFrame = document.getElementById('myIFrame');
            if (myIFrame) {
                myIFrame.style.height = event.data.h + "px";
                myIFrame.style.width  = event.data.w + "px";
            }
        };
        if (window.addEventListener) {
            window.addEventListener("message", resizeIFrame, false);
        } else if (window.attachEvent) {
            window.attachEvent("onmessage", resizeIFrame);
        }
        </script>""" + """
        <a href="{}" target="_blank" >{}</a>""".format(url,url_frontend) + """
        </html>"""
    
    return html

for row in range(0, len(df.index)):
    lat, lon = df.loc[row, 'lat'], df.loc[row, 'lon']

    tooltip = str(df.loc[row, 'zone'])
    url = str(df.loc[row, 'url'])
    url_frontend = ' '.join([x.capitalize() for x in tooltip.split(' ')] if tooltip[1:] else tooltip.capitalize())

    img_url = df.loc[row, 'img']

    im = base64.b64decode(img_url.encode('utf_8_sig'))
    img = Image.open(BytesIO(im))
    # img.show(img)
    buffer = img.resize((210,118))   # 210,118 - 158,89
    
    buffered = BytesIO()
    buffer.save(buffered, format="JPEG")
    img_url = base64.b64encode(buffered.getvalue()).decode('utf_8_sig')

    html = '<img src="data:image/png;base64,{}"><p></p><a href="{}" target="_blank" >{}</a>'.format
    iframe = folium.IFrame(html(img_url,url,url_frontend), width=245japan, height=180)  # Original 420 236
    popup = folium.Popup(iframe, max_width=270)

    folium.CircleMarker(
        location=[lat, lon], #list(t.transform(lat, lon)),
        radius=4, # radius
        tooltip=url_frontend,
        fill=True,
        fill_color='#{:02x}{:02x}{:02x}'.format(214, 37, 152),  # color
        stroke = False,
        fill_opacity=.5,
        popup=popup).add_to(m)        

m.save('Samples/maptest.html')
m.show_in_browser()