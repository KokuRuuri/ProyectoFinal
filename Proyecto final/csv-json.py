import csv
import os
import json

def cargar_csvs(lista):
    lecturas = []
    reader=[]
    for archivo in lista:
        with open(archivo,encoding='latin-1') as f:
            reader=f.readlines()
        lecturas.append(reader)
    return lecturas
        
def guardar_csv(archivo,objetos):
    if not objetos:
        return
    with open(archivo, 'w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,next(iter(objetos.values())).to_dict().keys())
        writer.writeheader()
        for obj in objetos.values():
            writer.writerow(obj.to_dict())

def guardarJson(diccionario):
    diccionario = {}
            
'''El objetivo es leer los archivos csv del subfolder areas y catálogos, crear un diccionario de revistas
donde la llave sea el título de la revista y el valor un diccionario con las llaves "areas" y "catalogos". Ejemplo:

    { "acta geophysica"       : { "areas": ["CIENCIAS_EXA", "ING"], "catalogos":["JCR","SCOPUS"]},
      "acta geophysica sinica": { "areas": ["CIENCIAS_EXA"], "catalogos":["SCOPUS"]}  
    }

Una vez creado el diccionario, guardarlo como archivo json en el subfolder del mismo nombre (datos/json). Verificar que puede ser leído
'''
if __name__ == '__main__':
    folderAreas = "./datos/csv/areas"
    folderCatalogos = "./datos/csv/catalogos"
    listaAreas = [folderAreas+'/'+x for x in os.listdir(folderAreas)]
    listaNombreAreas = [x.replace(' RadGridExport.csv','') for x in os.listdir(folderAreas)]
    listaCatalogos = [folderCatalogos+'/'+x for x in os.listdir(folderCatalogos)]
    listaNombreCatalogos = [x.replace('_RadGridExport.csv','') for x in listaCatalogos]
    diccionario = {'':{'':[],'':[]}}

    lecturaAreas = cargar_csvs(listaAreas)
    lecturaCatalogos = cargar_csvs(listaCatalogos)
    i=0
    for Areas in lecturaAreas:
        for x in Areas:
            if x in diccionario:
                diccionario[x.strip()]['areas'].append(listaNombreAreas[i])
            else:
                diccionario[x.strip()] = {'areas':[listaNombreAreas[i]],'catalogos':[]}
        i+=1
    
    i=0
    for Catalogos in lecturaCatalogos:
        for x in Catalogos:
            diccionario[x.strip()]['catalogos'].append(listaNombreCatalogos[i])
        i+=1
    
    with open('diccionario.json', 'w') as f:
        json.dump(diccionario,f,indent = 4)