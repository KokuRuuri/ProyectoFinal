import json
import os

class Revista:
    def __init__(self, titulo, info):
        self.titulo = titulo
        self.hindex = info.get('hindex', 0)
        self.areas = info.get('Area EPA', [])
        self.catalogos = info.get('catalogos', [])
        self.enlace = info.get('link', '')
        self.issn = info.get('issn', '').replace('-', '')
        self.editorial = info.get('editorial', '')
        self.pais = info.get('pais', '')
        self.info = info

    def to_dict(self):
        return {
            'id': self.issn,
            'titulo': self.titulo,
            'h_index': self.hindex
        }

class RevistaCatalogo:
    def __init__(self, path_json='ProyectoFinal/datos/json/datos.json'):
        self.path_json = path_json
        self.revistas = {}
        self._cargar_datos()

    def _cargar_datos(self):
        if not os.path.exists(self.path_json):
            raise FileNotFoundError(f"No se encontró el archivo: {self.path_json}")
        with open(self.path_json, encoding='utf-8') as f:
            data = json.load(f)
        for titulo, info in data.items():
            revista = Revista(titulo, info)
            self.revistas[titulo.lower()] = revista

    def obtener_revista(self, titulo):
        return self.revistas.get(titulo.lower())

    def obtener_todas_revistas(self):
        return list(self.revistas.values())

    def obtener_areas(self):
        areas = set()
        for revista in self.revistas.values():
            areas.update(revista.areas)
        return sorted(areas)

    def obtener_catalogos(self):
        catalogos = set()
        for revista in self.revistas.values():
            catalogos.update(revista.catalogos)
        return sorted(catalogos)

    def revistas_por_area(self, area):
        area = area.lower()
        return sorted(
            [rev for rev in self.revistas.values() if area in [a.lower() for a in rev.areas]],
            key=lambda r: r.hindex,
            reverse=True
        )

    def revistas_por_catalogo(self, catalogo):
        return sorted(
            [rev for rev in self.revistas.values() if catalogo in rev.catalogos],
            key=lambda r: r.hindex,
            reverse=True
        )

    def revistas_por_letra(self, letra):
        letra = letra.lower()
        return sorted(
            [rev for rev in self.revistas.values() if rev.titulo.lower().startswith(letra)],
            key=lambda r: r.titulo.lower()
        )

    def buscar_revistas(self, termino):
        termino = termino.lower()
        return sorted(
            [rev for rev in self.revistas.values() if termino in rev.titulo.lower()],
            key=lambda r: r.hindex,
            reverse=True
        )
