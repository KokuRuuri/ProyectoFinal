from flask import Flask, render_template, request
import json
import revista_classes as rc

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/area')
def area():
    with open('datos/json/diccionario.json', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('area.html', data=data)

@app.route('/catalogos')
def catalogos():
    with open('datos/json/diccionario.json', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('catalogos.html', data=data)

@app.route('/explorar')
def explorar():
    with open('./datos/json/diccionario.json', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('explorar.html', data=data)

@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    resultados = []
    if request.method == 'POST':
        termino = request.form['termino'].lower()
        with open('datos/json/diccionario.json', encoding='utf-8') as f:
            data = json.load(f)
        resultados = [rev for rev in data if termino in rev.lower()]
    return render_template('busqueda.html', resultados=resultados)

@app.route('/revista/<titulo>')
def revista(titulo):
    with open('datos/json/diccionario.json', encoding='utf-8') as f:
        data = json.load(f)
    info = data.get(titulo.lower())
    return render_template('revista.html', titulo=titulo, info=info)

@app.route('/creditos')
def creditos():
    return render_template('creditos.html')

if __name__ == '__main__':
    app.run(debug=True)
