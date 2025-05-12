import json

def guardarJSON(dict,nombre):
    with open(nombre, 'w',encoding='utf-8') as f:
            json.dump(dict,f,indent = 4,ensure_ascii=False)
 
def cargarJSON(archivo):
    data={}
    try:
        with open(archivo,encoding='utf-8') as j:
            data = json.load(j)
    except:
        print('no se encontro el archivo...')
    return data


if __name__ == '__main__':
    dictGuardado='./datos/json/diccionario.json'
    dic= cargarJSON('./datos/json/diccionario.json')
    datos = dict(sorted(dic.items()))
    guardarJSON(datos,dictGuardado)
    print('Guardado JSON...')