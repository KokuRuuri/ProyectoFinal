from flask import Flask, render_template, request, jsonify,session,redirect,url_for
from revista_classes import RevistaCatalogo
from scripts import web_scrapper as wb
import os
import hashlib
import datetime

json_locacion = './datos/json/datos.json'
json = wb.cargarJSONutf8(json_locacion)
users = wb.cargarJSONutf8('./datos/json/users.json')
app = Flask(__name__)
revista_handler = RevistaCatalogo()
app.secret_key = os.urandom(24)
 
@app.route('/area/')
def area():
    nombre_area='CIENCIAS_BIO'
    areas = revista_handler.obtener_areas()
    revistas = revista_handler.revistas_por_area(nombre_area)
    return render_template(
        'area_detalle.html',
        areas=areas,
        revistas=revistas,
        area_actual=nombre_area
    )

@app.route('/')
def index():
    revistas = sorted(
        revista_handler.obtener_todas_revistas(),
        key=lambda r: r.hindex,
        reverse=True
    )
    total = len(revistas)  # calcular total de revistas
    return render_template('index.html', revistas=revistas, total=total)
 

@app.route('/area/<nombre_area>', methods=['GET', 'POST'])
def area_detalle(nombre_area):
    areas = revista_handler.obtener_areas()
    revistas = revista_handler.revistas_por_area(nombre_area)
    resultados = []
    termino = ''
    if request.method == 'POST':
        termino = request.form.get('termino', '')
        resultados = revista_handler.buscar_revistas(termino)
        revistas = [rev for rev in resultados if rev in revistas]
    return render_template(
        'area_detalle.html',
        areas=areas,
        revistas=revistas,
        area_actual=nombre_area
    )
    
@app.route('/buscar_revistas')
def buscar_revistas():
    q = request.args.get('q', '').lower()
    area = request.args.get('area')
    catalogo = request.args.get('catalogo')
    if area:
        filtradas = revista_handler.revistas_por_area(area)
    elif catalogo:
        filtradas = revista_handler.revistas_por_catalogo(catalogo)
    else:
        filtradas = revista_handler.obtener_todas_revistas()
 
    # Búsqueda por término
    resultado = [
        {
            'id': r['issn'],
            'titulo': r['titulo'],
            'h_index': r['hindex']
        }
        for r in filtradas if q in r['titulo'].lower()
    ]
 
    return jsonify({'revistas': resultado})
 
 
@app.route('/revistas/<area>', methods=['GET'])
def obtener_revistas_por_area(area):
    revistas = revista_handler.revistas_por_area(area)
    return jsonify({'revistas': [revista.to_dict() for revista in revistas]})
 
@app.route('/catalogos')
def catalogos():
    catalogos = revista_handler.obtener_catalogos()
    return render_template('catalogo.html', catalogos=catalogos)
 
@app.route('/catalogos/<nombre_catalogo>',methods=['GET', 'POST'])
def catalogo_detalle(nombre_catalogo):
    revistas = revista_handler.revistas_por_catalogo(nombre_catalogo)
    catalogos = revista_handler.obtener_catalogos()
    if request.method == 'POST':
        termino = request.form.get('termino', '')
        resultados = revista_handler.buscar_revistas(termino)
        revistas = [rev for rev in resultados if rev in revistas]
    return render_template(
        'catalogo_detalle.html',
        catalogo=nombre_catalogo,
        revistas=revistas,
        catalogos=catalogos
    )
 
@app.route('/explorar')
@app.route('/explorar/<letra>')
def explorar(letra=None):
    letras = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    revistas = []
    if letra:
        revistas = revista_handler.revistas_por_letra(letra)
    return render_template(
        'explorar_detalle.html',
        letra=letra,
        letras=letras,
        revistas=revistas
    )
 
@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    resultados = []
    termino = ''
    if request.method == 'POST':
        termino = request.form.get('termino', '')
        resultados = revista_handler.buscar_revistas(termino)
    return render_template('busqueda.html', resultados=resultados, termino=termino)
 
@app.route('/revista/<id>')
def revista_detalle(id):
    # Buscar revista por titulo sin guiones (como ID)
    revista = [rev for rev in revista_handler.obtener_todas_revistas() if rev.titulo == id]
    if len(revista)>0:
        revista= revista[0]
        dia=datetime.date.today().day
        mes=datetime.date.today().month
        dia_anio=(mes*30)+dia
        dia_anio_rev=(revista.mes*30)+revista.dia
        if dia_anio-dia_anio_rev>30 or dia_anio-dia_anio_rev<-30 :
            json.update(wb.ConseguirInformacion(revista.titulo,revista.areas,revista.catalogos))
            wb.guardarJSON(json,json_locacion)
    if revista:
        return render_template('revista_detalle.html', revista=revista)
    else:
        return f"Revista con id {id} no encontrada", 404
 
@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

@app.route('/login',methods =['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        if username in users.keys():
            if hashlib.sha256(password.encode()).hexdigest()==users[username]["Password"]:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html')
 

if __name__ == '__main__':
    app.run(debug=True)