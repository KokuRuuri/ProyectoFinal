import os
import json

def cargar_csvs(lista):
    #carga varios csvs creando una lista de csvs que contiene cada una una lista de palabras
    lecturas = []
    reader=[]
    for archivo in lista:
        #se lee el archivo en latin-1
        with open(archivo,encoding='latin-1') as f:
            reader=f.readlines()
        #se añade la lista a la lista
        lecturas.append(reader)
    return lecturas
        
            
def creaDiccionario(lecturaAreas,listaNombreAreas,lecturaCatalogos,listaNombreCatalogos):
    #crea diccionario usando las 2 listas de listas
    diccionario={}
    #contador 
    i=0
    for Areas in lecturaAreas:
        for x in Areas:
            #readlines trae tambien saltos de  lineas asi que se quitan
            x=x.strip()
            #se busca si ya existe, si no, se crea uno nuevo, si sí, se añade a la lista de areas el nombre del area
            if x in diccionario.keys():
                diccionario[x]['areas'].append(listaNombreAreas[i])
            else:
                diccionario[x] = {'areas':[listaNombreAreas[i]],'catalogos':[]}
        i+=1
    i=0
    for Catalogos in lecturaCatalogos:
        for x in Catalogos:
            x=x.strip()
            if x in diccionario.keys():
                diccionario[x]['catalogos'].append(listaNombreCatalogos[i])
            else:
                diccionario[x] = {'areas':[],'catalogos':[listaNombreCatalogos[i]]}
        i+=1
    diccionario.pop("TITULO:")
    return diccionario

def guardarJson(diccionario,destino):
    #guarda el diccionario en json
    with open(destino, 'w') as f:
        json.dump(diccionario,f,indent = 4)

if __name__ == '__main__':
    #ruta de folders
    folderAreas = "./parte1/datos/csv/areas"
    folderCatalogos = "./parte1/datos/csv/catalogos"
    #se consigue una lista de rutas de los archivos dentro de los folders
    listaAreas = [folderAreas+'/'+x for x in os.listdir(folderAreas)]
    listaCatalogos = [folderCatalogos+'/'+x for x in os.listdir(folderCatalogos)]
    #se consigue el nombre de cada archivo (sin extras o asi)
    listaNombreAreas = [x.replace(' RadGridExport.csv','') for x in os.listdir(folderAreas)]
    listaNombreCatalogos = [x.replace('_RadGridExport.csv','') for x in os.listdir(folderCatalogos)]
    #donde se guardara el json
    destino='./parte1/datos/json/diccionario.json'
    #se leen los archivos
    lecturaAreas = cargar_csvs(listaAreas)
    lecturaCatalogos = cargar_csvs(listaCatalogos)
    #se crea diccionario
    diccionario = creaDiccionario(lecturaAreas,listaNombreAreas,lecturaCatalogos,listaNombreCatalogos)
    #se guarda
    guardarJson(diccionario,destino)