from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from starlette.responses import HTMLResponse
from jinja2 import Template
from subprocess import Popen

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
layer = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/input/{user_id}/", response_model=schemas.Item, tags=["input"])
def enter_item(user_id: str, item: schemas.Incident, db: Session = Depends(get_db)):
    return crud.create_valid_item(db=db, item=item, user_id=user_id)

# curl -d '{"id":"0000000000000000", "inc_type":"objeto", "inc_detail":"mar", "lat":41.358767876876, "lon":2.1878687687667, "url":"https://maps.google.com/maps?q=41.358767876876%2C2.1878687687667&z=14&hl=en", "pic":"https://drive.google.com/file/d/16udAHXF3QNouyb6bXUNgIQYW_bUzhSDp/preview", "is_active":"True"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/input/0034687978031/
# curl -d '{"id":"1000000000000000", "inc_type":"vertido", "inc_detail":"dársena", "lat":41.368767876876, "lon":2.1778687687667, "url":"https://maps.google.com/maps?q=41.368767876876%2C2.1778687687667&z=14&hl=en", "pic":"https://drive.google.com/file/d/16udAHXF3QNouyb6bXUNgIQYW_bUzhSDp/preview", "is_active":"True"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/input/0034687978022/
# curl -d '{"id":"2000000000000000", "inc_type":"vertido", "inc_detail":"calzada", "lat":41.348767876876, "lon":2.1978687687667, "url":"https://maps.google.com/maps?q=41.348767876876%2C2.1978687687667&z=14&hl=en", "pic":"https://drive.google.com/file/d/16udAHXF3QNouyb6bXUNgIQYW_bUzhSDp/preview", "is_active":"True"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/input/0034687978013/


@app.post("/invalid_input/{user_id}/", response_model=schemas.Invalid_Item, tags=["invalid_input"])
def enter_invalid_item(user_id: str, item: schemas.Invalid_Incident, db: Session = Depends(get_db)):
    return crud.create_invalid_item(db=db, item=item, user_id=user_id)

@app.get("/update/{item_id}/", tags=["update"])
def update(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id=item_id)
    if item.is_active:
        item.is_active = False
    else:
        item.is_active = True
    db.commit()
    return

# curl -X GET "http://127.0.0.1:8000/update/0000000000000000/"

@app.get("/move/{item_id}/", tags=["move"])
def make_invalid(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id=item_id)
    data = item.inc_type + ' ' + item.inc_detail + ' ' + str(item.lat) + ' ' + str(item.lon) + ' ' + item.url + ' ' + item.pic + ' ' + str(item.is_active)
    Popen('curl -d \'{"id":"' + item_id + '" , "data":"' + data + '"}\' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/invalid_input/' + item.owner_id + '/', stdin=None, stderr=None, shell=True).communicate()
    db.delete(item)
    db.commit()
    return

# curl -X GET "http://127.0.0.1:8000/move/0000000000000000/"

@app.get("/json/", response_model=List[schemas.Item])
def read_items(skip: int = 0, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip)
    return items

# curl -X GET "http://127.0.0.1:8000/items/" -H  "accept: application/json"

@app.get("/items/", tags=["items"])
def dashboard(skip: int = 0, db: Session = Depends(get_db)):
    items = crud.get_items(db=db, skip=skip)
    template = Template('''
    <table style="width:100%">
        <script>
        function refreshPage(){
            window.location.reload();
        }
        </script>
        <tr>
        <th>ID</th>
        <th>Fecha</th>
        <th>Incidencia</th>
        <th>Detalle</th>
        <th>Mapa</th>
        <th>Foto</th>
        <th>Usuario</th>
        <th>Estado</th>
        </tr>
        {% for item in reversed(items) %}
        <tr>
        <td>{{ item['id'] }}</td>
        <td>{{ item['timestamp'] }}</td>
        <td>{{ item['inc_type'] }}</td>
        <td>{{ item['inc_detail'] }}</td>
        <td><a href={{ item['url'] }}>{{ item['lat'] }} {{ item['lon'] }}</a></td>
        <td><iframe src={{ item['pic'] }}></iframe></td>
        <td>{{ item['owner_id'] }}</td>
            {% if item['is_active'] %}
                <td>
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script type=text/javascript>
                    $(function() {
                      $('a#active').bind('click', function() {
                        $.getJSON('/update/{{ item['id'] }}/',
                            function(data) {
                          //do nothing
                        });
                        return refreshPage();
                      });
                    });
                </script>
                <div class='container'>
                        <form>
                            <a href=# id=active><button class='btn button2'>Activo</button></a>
                        </form>
                </div>
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script type=text/javascript>
                    $(function() {
                      $('a#move').bind('click', function() {
                        $.getJSON('/move/{{ item['id'] }}/',
                            function(data) {
                          //do nothing
                        });
                        return refreshPage();
                      });
                    });
                </script>
                <div class='container'>
                        <form>
                            <a href=# id=move><button class='btn button3'>Invalidar</button></a>
                        </form>
                </div>
                </td>
            {% else %}
                <td>
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                <script type=text/javascript>
                    $(function() {
                      $('a#solved').bind('click', function() {
                        $.getJSON('/update/{{ item['id'] }}/',
                            function(data) {
                          //do nothing
                        });
                        return refreshPage();
                      });
                    });
                </script>
                <div class='container'>
                        <form>
                            <a href=# id=solved><button class='btn button1'>Resuelto</button></a>
                        </form>
                </div>
                </td>
            {% endif %}
        </tr>
        {% endfor %}
    </table>
    <style>
        table {
            margin: 0 auto;
            font-size: medium;
            border: 1px solid black;
        }

        td {
            background-color: #ccffff;
            border: 1px solid black;
        }

        th,
        td {
            font-weight: bold;
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            font-family: 'Helvetica';
        }

        td {
            font-weight: lighter;
        }
        .button1 {background-color: #4CAF50;}
        .button2 {background-color: #FF0000;}
        .button3 {background-color: #CC99FF;}
    </style>
    ''')
    template.globals['reversed'] = reversed
    return HTMLResponse(template.render(items = items))

@app.get("/invalid_items/", tags=["invalid_items"])
def invalid_dashboard(skip: int = 0, db: Session = Depends(get_db)):
    items = crud.get_invalid_items(db=db, skip=skip)
    template = Template('''
    <table style="width:100%">
        <tr>
        <th>ID</th>
        <th>Fecha</th>
        <th>Datos</th>
        <th>Usuario</th>
        </tr>
        {% for item in reversed(items)%}
        <tr>
        <td>{{ item['id'] }}</td>
        <td>{{ item['timestamp'] }}</td>
        <td>{{ item['data'] }}</td>
        <td>{{ item['owner_id'] }}</td>
        </tr>
        {% endfor %}
    </table>
    <style>
        table {
            margin: 0 auto;
            font-size: medium;
            border: 1px solid black;
        }

        td {
            background-color: #ccffff;
            border: 1px solid black;
        }

        th,
        td {
            font-weight: bold;
            border: 1px solid black;
            padding: 10px;
            text-align: center;
            font-family: 'Helvetica';
        }

        td {
            font-weight: lighter;
        }
    </style>
    ''')
    template.globals['reversed'] = reversed
    return HTMLResponse(template.render(items = items))
