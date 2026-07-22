"""Filtros: relevancia, ruido, internacional/Colombia y anti-estafa.

Las coincidencias son por PALABRA COMPLETA, no por trozo de texto: así
"loto" ya no hace match dentro de "piloto", ni "nz" dentro de "gonzalez".
"""
import re

_PATRONES = {}


def _patron(frase):
    """Compila (y cachea) una frase como coincidencia de palabra completa."""
    p = _PATRONES.get(frase)
    if p is None:
        limpia = re.escape(frase.lower().strip())
        p = re.compile(r"(?<!\w)" + limpia + r"(?!\w)")
        _PATRONES[frase] = p
    return p


def _contiene(texto, frases):
    texto = (texto or "").lower()
    return any(_patron(f).search(texto) for f in frases if f and f.strip())


def es_relevante(item, palabras_clave):
    """Solo mira el TÍTULO.

    Si la palabra clave aparece únicamente en la descripción, casi siempre es
    ruido (videos que mencionan un sorteo de pasada, no que lo sean)."""
    return _contiene(item["titulo"], palabras_clave)


def esta_excluido(item, palabras_excluir, palabras_excluir_titulo=()):
    """True si hay que descartarlo.

    - palabras_excluir_titulo: solo en el título (sorteos ya terminados).
      Se mira solo el título para no descartar un sorteo bueno cuya
      descripción diga "anunciaré los ganadores el viernes".
    - palabras_excluir: en título + descripción (loterías, deportes, etc.)."""
    if _contiene(item["titulo"], palabras_excluir_titulo):
        return True
    return _contiene(f"{item['titulo']} {item['descripcion']}", palabras_excluir)


def es_internacional(item, senales_internacional):
    return _contiene(f"{item['titulo']} {item['descripcion']}",
                     senales_internacional)


def es_colombia(item, senales_colombia):
    return _contiene(f"{item['titulo']} {item['descripcion']}", senales_colombia)


def evaluar(item, senales_estafa):
    """Devuelve (nivel, motivos). nivel: 'ok' | 'duda' | 'riesgo'."""
    texto = f"{item['titulo']} {item['descripcion']} {item['url']}".lower()
    motivos = [s for s in senales_estafa if _patron(s).search(texto)]

    acortadores = ["bit.ly", "tinyurl", "cutt.ly", "is.gd", "adf.ly"]
    if any(a in texto for a in acortadores):
        motivos.append("usa enlace acortado")

    if len(motivos) >= 2:
        return "riesgo", motivos
    if len(motivos) == 1:
        return "duda", motivos
    return "ok", motivos


ETIQUETA = {
    "ok": "🟢 Parece legítimo",
    "duda": "🟡 Revísalo con cuidado",
    "riesgo": "🔴 Sospechoso (posible estafa)",
}
