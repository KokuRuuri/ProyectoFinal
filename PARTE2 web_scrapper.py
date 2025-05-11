import re
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import Levenshtein


url_ISSN='https://portal.issn.org/api/search?search[]=MUST='
url_busqueda='https://www.scimagojr.com/journalsearch.php?q='
bing='https://www.bing.com/search?q='
url_resurch='https://www.resurchify.com/find/?query='

'''configuracion de request'''
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }


'''inicializa el diccionario'''
datos={}


'''pide la informacion de la pagina'''
def scrap(url:str):
    '''Consigue la pagina usando request'''
    pagina = requests.get(url,headers=headers, timeout=20)
    if pagina.status_code != 200:
        raise Exception(f'Error {pagina.status_code} en la pagina {url}')
    return pagina
 
'''proceso que se llama cuando encuentra un caracter corrupto (fuera de latin-1 o no permitido)
    busca en google esperando conseguir un recurso de la pagina del ISSN para corregir el nombre...'''
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
 

'''proceso principal, busca informacion en base al titulo'''
def ConseguirInformacion(titulo,areas,catalogos):
    '''bandera que ve si se consiguen los datos'''
    Consegido=False
    dict={}
    '''bandera para ver si es corrupto'''
    flag=True
    '''proceso si hay caracter corrupto'''
    if re.search('[^\u0020-\u007F\u00A0-\u00FF\u0100-\u017F\u0180-\u024F]+',titulo) or '?' in titulo or '½' in titulo:
        print('C')
        url = BusquedaCorrupto(titulo)
        if 'https://portal.issn.org/resource' in url:
            soup = BeautifulSoup(scrap(url).content,"html.parser")
            main_content = soup
            ntitulo = soup.find('div',class_='record-header-keytitle').h1.text.replace('(en línea)','').strip()
            print('!!'+ntitulo)
            ISSN = soup.find('div',class_='sidebar-accordion-list-selected-item').a.text
            flag=False
            datos.pop(titulo)
    
        '''si no es corrupto, busca en la pagina de ISSN'''
    else:
        ntitulo=titulo
        url=url_ISSN+titulo
        soup = BeautifulSoup(scrap(url).content,"html.parser")
        main_content = soup.find('div',class_='item-result-block')
    '''inicializa el diccionario, aniadiendo de una vez las AREA EPA y CATALOGOS'''   
    dict[ntitulo] = {'Sitio web':None,
        'H_Index':None,
        'Subject Area and category':None,
        'Area EPA':areas,
        'Catalogos':catalogos,
        'Publisher': None,
        'ISSN':None,
        'Widget':None,
        'Publication Type': None}
    '''si consigue el ISSN (main content)'''
    if main_content:
        '''si NO fue archivo corrupto.
            dentro de la pagina ISSN busca...'''
        if flag:
            if soup.find('div',class_='sidebar-accordion-list-selected-item') == None:
                p = main_content.find('p')
                ISSN = p.text.replace('ISSN: ','').replace('Linking ISSN (ISSN-L): ','').strip()
            else:
                ISSN = soup.find('div',class_='sidebar-accordion-list-selected-item').a.text
        '''usa el ISSN para buscar en SCIMAGOJR'''
        link='https://www.scimagojr.com/journalsearch.php?q='+ISSN
        soup = BeautifulSoup(scrap(link).content,"html.parser")
        main_content = soup.find('div',class_='search_results')
        '''si encuentra resultados'''
        if(main_content != None):
            '''aveces me daba error?, asi que es una excepcion para evitar eso'''
            if(main_content.a != None):
                '''consigue el hipernvinculo de la pagina del journal'''
                href = main_content.a.get('href')
                ref = 'https://www.scimagojr.com/'+href
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
                    if len(divs[3].findAll('p'))==2:
                        dict[ntitulo]['H_index']=divs[3].findAll('p')[1].text
                    else:
                        dict[ntitulo]['H_index']=divs[3].findAll('p')[0].text
                    '''aqui consigue las areas y sus categorias en forma de diccionario'''
                    dict[ntitulo]['Subject Area and category'] ={ul.find('li').a.text:[li.a.text for li in ul.find('li').ul.findAll('li',recursive=False)] for ul in divs[1].p.findAll('ul',recursive=False)}
                    dict[ntitulo]['Publisher']=divs[2].find('p').text.strip()
                    dict[ntitulo]['ISSN']=ISSN
                    dict[ntitulo]['Widget'] = soup.find('input',id='embed_code').get('value')
                    dict[ntitulo]['Publication Type'] =divs[4].find('p').text
                    '''Se imprime aviso de que se pudo con este proceso y se levanta la bandera de conseguido'''
                    print('!!')
                    Consegido=True
                    
            else:
                '''en caso de solo haber conseguido ISSN se guarda...'''
                dict[ntitulo]['ISSN']=ISSN

    '''Si no se logro, se intenta con resurchify'''
    if(Consegido==False):
        '''busca en la pagina'''
        url=url_resurch+titulo
        soup = BeautifulSoup(scrap(url).content,"html.parser")
        '''si hay resultados'''
        if soup.find('p',class_='w3-medium'):
            '''se ven todos y se ve su radio de levenstein'''
            for n in soup.findAll('div','w3-white w3-container w3-card-4 w3-hover-light-gray'):
                dist = Levenshtein.ratio(n.b.text[3:].replace('npj','').lower(),titulo.lower())   
                '''si una esta lo suficientemente similar... se continua'''
                if dist>.80:
                    '''se entra al hipervinculo y se consiguen sus atributos'''
                    url= n.find('a').get('href')
                    soup = BeautifulSoup(scrap(url).content,"html.parser")
                    main_content=soup.find('table',class_='w3-table w3-bordered w3-white w3-card-2 w3-hoverable d_table_font_size').findAll('tr')
                    dict[ntitulo]['Subject Area and category'] = main_content[4].findAll('td')[1].text.split(';')
                    dict[ntitulo]['Publisher']=main_content[9].findAll('td')[1].text
                    dict[ntitulo]['H_Index'] =main_content[5].findAll('td')[1].text
                    dict[ntitulo]['ISSN']=main_content[11].findAll('td')[1].text
                    dict[ntitulo]['Widget'] = None
                    dict[ntitulo]['Publication Type'] = main_content[4].findAll('td')[1].text
                    '''imprime mensaje que se logro con este metodo, levanta bandera y rompe el ciclo para que no cheque los demas resultados'''
                    print('O!@')
                    Consegido=True
                    break
    '''imprime mensaje dependiendo de si se encontro o no...'''
    if(Consegido):
        print('O ' + titulo +' Completado')
    else:
        print('X ' + titulo +' No se pudo encontrar...')

    '''guarda el nuevo diccionario en el super diccionario (datos)'''
    datos.update(dict)

'''guarda en UTF 8'''    
def guardarJSON(dict,nombre):
    with open(nombre, 'w',encoding='utf-8') as f:
            json.dump(dict,f,indent = 4,ensure_ascii=False)
 

'''Carga en latin 1'''
def cargarJSON(archivo):
    data={}
    try:
        with open(archivo,encoding='latin-1') as j:
            data = json.load(j)
    except:
        print('no se encontro el archivo...')
    return data
   

def extraccionParalelo(dic,datos,flag):
    '''si detecta que datos esta vacio o llega una bandera de verdad, extrae todos los titulos de diccionario.json
        si detecta que ya hay datos, hace una busqueda para ver si encuentra lo que no encontro...
        '''
    if len(datos)==0 or flag:
        datos={}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            informacion = [executor.submit(ConseguirInformacion, titulo,dic[titulo]['areas'],dic[titulo]['catalogos']) for titulo in dic.keys()]
            concurrent.futures.wait(informacion)
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            informacion = {executor.submit(ConseguirInformacion, titulo,datos[titulo]['Area EPA'],datos[titulo]['Catalogos']) for titulo in datos.keys() if datos[titulo]['H_Index']==None}
            concurrent.futures.wait(informacion)

def extraccionSecuencial():
    for titulo in dic.keys():
        ConseguirInformacion(titulo,dic[titulo]['areas'],dic[titulo]['catalogos'])

if __name__ == '__main__':
    '''carga diccionarios'''
    dictGuardado='./datos/json/datos.json'
    dic= cargarJSON('./datos/json/diccionario.json')
    datos = cargarJSON('./datos/json/datos.json')
    '''extrae'''
    extraccionParalelo(dic,datos)
    '''ordena'''
    datos = dict(sorted(datos.items()))
    '''guarda'''
    guardarJSON(datos,dictGuardado,False)
    print('Guardado JSON...')