
import json
import os,argparse,requests
from bs4 import BeautifulSoup


url_ISSN='https://portal.issn.org/api/search?search[]=MUST='
url_busqueda='https://www.scimagojr.com/journalsearch.php?q='

'''configuracion de request'''
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

def scrap(url:str):
    '''Consigue la pagina usando request'''
    pagina = requests.get(url,headers=headers, timeout=15)
    if pagina.status_code != 200:
        raise Exception(f'Error {pagina.status_code} en la pagina {url}')
    return pagina
    
def weScrappin(dict_base):
    dict={}
    i=0
    for titulo in dict_base.keys():
        i+=1
        if(i==20):
            break
        print(titulo)
        dict[titulo] = {'Sitio web':None,
                            'H_Index':None,
                            'Subject Area and category':None,
                            'Area EPA':dict_base[titulo]['areas'],
                            'Catalogos':dict_base[titulo]['catalogos'],
                            'Publisher': None,
                            'ISSN':None,
                            'Widget':None,
                            'Publication Type': None}
        url=url_ISSN+titulo
        soup = BeautifulSoup(scrap(url).content,"html.parser")
        main_content = soup.find('div',class_='item-result-block')
        if main_content:
            p = main_content.find('p')
            ISSN = p.text.replace('ISSN: ','').replace('Linking ISSN (ISSN-L): ','').strip()
            print('encontre: '+ISSN)
            link='https://www.scimagojr.com/journalsearch.php?q='+ISSN
            soup = BeautifulSoup(scrap(link).content,"html.parser")
            main_content = soup.find('div',class_='search_results')
            if(main_content.a != None):
                href = main_content.a.get('href')

                ref = 'https://www.scimagojr.com/'+href
                print('consegui url...: '+ref)
                soup = BeautifulSoup(scrap(ref).content,"html.parser")
                '''encuentro el bloque principal'''
                divv = soup.find('div',class_='journalgrid')
                '''saco las divisiones'''
                divs = divv.findAll('div')
                '''se consiguen las caracteristicas'''
                
                if(divs[7].find('p')!=None):
                    Sitio =  divs[7].find('p').a.get('href')
                else:
                    Sitio = ''
                H_Index =divs[3].find('p').text
                Subject ={ul.find('li').a.text:[li.a.text for li in ul.find('li').ul.findAll('li',recursive=False)] for ul in divs[1].p.findAll('ul',recursive=False)}

                Publisher=divs[2].find('p').text
                Widget = soup.find('input',id='embed_code').get('value')
                Type =divs[4].find('p').text
                dict[titulo] = {'Sitio web': Sitio,
                                'H_Index':H_Index,
                                'Subject Area and category':Subject,
                                'Area EPA':dict_base[titulo]['areas'],
                                'Catalogos':dict_base[titulo]['catalogos'],
                                'Publisher': Publisher.strip(),
                                'ISSN':ISSN,
                                'Widget':Widget,
                                'Publication Type': Type}
                p = p.text.replace('ISSN: ','').strip()
                print(H_Index)
                
            else:
                print('X no se encontro en scimagojr')
        else:
            print('No se encontro ISSN...')
        print('----------------------------------------')
    return dict
        
def guardarJSON(dict):
    with open('wea.json', 'w') as f:
            json.dump(dict,f,indent = 4)

def json_dict(archivo):
    with open(archivo) as j:
        data = json.load(j)
    return data

if __name__ == '__main__':
    
    dict= json_dict('./parte1/datos/json/diccionario.json')
    nuevo_dict = weScrappin(dict)
    guardarJSON(nuevo_dict)
    print('Guardado JSON...')