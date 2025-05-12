from flask import Flask, render_template, request, jsonify
from revista_classes import RevistaCatalogo

app = Flask(__name__)
revista_handler = RevistaCatalogo()

@app.route('/')
def index():
    revistas = sorted(
        revista_handler.obtener_todas_revistas(),
        key=lambda r: r.hindex,
        reverse=True
    )
    total = len(revistas)  # calcular total de revistas
    return render_template('index.html', revistas=revistas, total=total)

@app.route('/area')
def area():
    areas = revista_handler.obtener_areas()
    return render_template('area.html', areas=areas)

@app.route('/area/<nombre_area>')
def area_detalle(nombre_area):
    areas = revista_handler.obtener_areas()
    revistas = revista_handler.revistas_por_area(nombre_area)
    return render_template(
        'area_detalle.html',
        areas=areas,
        revistas=revistas,
        area_actual=nombre_area
    )

@app.route('/revistas/<area>', methods=['GET'])
def obtener_revistas_por_area(area):
    revistas = revista_handler.revistas_por_area(area)
    return jsonify({'revistas': [revista.to_dict() for revista in revistas]})

@app.route('/catalogos')
def catalogos():
    catalogos = revista_handler.obtener_catalogos()
    return render_template('catalogo.html', catalogos=catalogos)

@app.route('/catalogos/<nombre_catalogo>')
def catalogo_detalle(nombre_catalogo):
    revistas = revista_handler.revistas_por_catalogo(nombre_catalogo)
    catalogos = revista_handler.obtener_catalogos()
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
    # Buscar revista por ISSN sin guiones (como ID)
    revista = next((rev for rev in revista_handler.obtener_todas_revistas() if rev.issn == id), None)
    if revista:
        return render_template('revista_detalle.html', revista=revista)
    else:
        return f"Revista con id {id} no encontrada", 404

@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

if __name__ == '__main__':
    app.run(debug=True)
