import re
import json
import requests
from bs4 import BeautifulSoup

url_ISSN='https://portal.issn.org/api/search?search[]=MUST='
url_busqueda='https://www.scimagojr.com/journalsearch.php?q='
bing='https://www.bing.com/search?q='
'''configuracion de request'''
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

def scrap(url:str):
    '''Consigue la pagina usando request'''
    pagina = requests.get(url,headers=headers, timeout=20)
    if pagina.status_code != 200:
        raise Exception(f'Error {pagina.status_code} en la pagina {url}')
    return pagina

def BusquedaCorrupto(titulo):
    url=bing+'"ISSN" "Title"'+titulo
    soup = BeautifulSoup(scrap(url).content,"html.parser")
    main_content = soup.find('ol',id='b_results')
    
    lis = main_content.findAll('li')
    if(main_content.findAll('li')[1].get('class')=='b_ans'):
        if(main_content.findAll('li')[2].get('class')=='b_ans b_top b_topborder b_qnacdxcont'):
            url = lis[3].h2.a.get('href')
        else:
            url = lis[2].h2.a.get('href')
    else:
        url = lis[1].h2.a.get('href')
    return url

def ConseguirInformacion(titulo,areas,catalogos):
    dict={}
    flag=True
    print(titulo)
    if re.search('[^\u0020-\u007F\u00A0-\u00FF\u0100-\u017F\u0180-\u024F\s]+',titulo) or '?' in titulo:
        url = BusquedaCorrupto(titulo)
        if 'https://portal.issn.org/resource' in url:
            soup = BeautifulSoup(scrap(url).content,"html.parser")
            ntitulo = soup.find('div',class_='record-header-keytitle').h1.text.replace('(en línea)','').strip()
            print(ntitulo)
            ISSN = soup.find('div',class_='sidebar-accordion-list-selected-item').a.text
            flag=False
    else:
        ntitulo=titulo
        url=url_ISSN+titulo
        soup = BeautifulSoup(scrap(url).content,"html.parser")
        main_content = soup.find('div',class_='item-result-block')
        
    dict[ntitulo] = {'Sitio web':None,
        'H_Index':None,
        'Subject Area and category':None,
        'Area EPA':areas,
        'Catalogos':catalogos,
        'Publisher': None,
        'ISSN':None,
        'Widget':None,
        'Publication Type': None}
    if main_content:
        if flag:
            p = main_content.find('p')
            ISSN = p.text.replace('ISSN: ','').replace('Linking ISSN (ISSN-L): ','').strip()
            print('encontre: '+ISSN)
        link='https://www.scimagojr.com/journalsearch.php?q='+ISSN
        soup = BeautifulSoup(scrap(link).content,"html.parser")
        main_content = soup.find('div',class_='search_results')
        if(main_content != None):
            if(main_content.a != None):
                href = main_content.a.get('href')

                ref = 'https://www.scimagojr.com/'+href
                print('consegui url...: '+ref)
                soup = BeautifulSoup(scrap(ref).content,"html.parser")
                '''encuentro el bloque principal'''
                divv = soup.find('div',class_='journalgrid')
                '''saco las divisiones'''
                if(divv!=None):
                    divs = divv.findAll('div')
                    '''se consiguen las caracteristicas'''
                    
                    if(divs[7].find('p')!=None):
                        Sitio =  divs[7].find('p').a.get('href')
                    else:
                        Sitio = ''
                    dict[ntitulo]['Sitio web']=Sitio
                    dict[ntitulo]['H_Index'] =divs[3].find('p').text
                    dict[ntitulo]['Subject Area and category'] ={ul.find('li').a.text:[li.a.text for li in ul.find('li').ul.findAll('li',recursive=False)] for ul in divs[1].p.findAll('ul',recursive=False)}
                    dict[ntitulo]['Publisher']=divs[2].find('p').text
                    dict[ntitulo]['ISSN']=ISSN
                    dict[ntitulo]['Widget'] = soup.find('input',id='embed_code').get('value')
                    dict[ntitulo]['Publication Type'] =divs[4].find('p').text
                    print('O EXITO')
            else:
                dict[ntitulo]['ISSN']=ISSN
                print('X No se encontro en scimagojr')
        else:
            dict[ntitulo]['ISSN']=ISSN
            print('X No se encontro en scimagojr')
    else:
        print('X No se encontro ISSN...')
    print('----------------------------------------')
    return dict
        
def guardarJSON(dict,nombre):
    with open(nombre, 'w') as f:
            json.dump(dict,f,indent = 4)

def cargarJSON(archivo):
    with open(archivo,encoding='utf-8') as j:
        data = json.load(j)
    return data

if __name__ == '__main__':
    dictGuardado='./datos/json/datos.json'
    dict= cargarJSON('./datos/json/diccionario.json')
    datos = {}
    contador = 0
    for titulo in dict.keys():
        contador+=1
        if contador==100:
            break
        informacion = ConseguirInformacion(titulo,dict[titulo]['areas'],dict[titulo]['catalogos'])
        datos.update(informacion)
    guardarJSON(datos,dictGuardado)
    print('Guardado JSON...')