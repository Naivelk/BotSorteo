"""Filtro simple anti-estafa. Da a cada sorteo una etiqueta de confianza."""

# Palabras que indican que SÍ es un sorteo (relevancia).
def es_relevante(item, palabras_clave):
    texto = f"{item['titulo']} {item['descripcion']}".lower()
    return any(p.lower() in texto for p in palabras_clave)


# ¿Contiene alguna palabra a excluir? (ruido: Mundial, lotería, etc.)
def esta_excluido(item, palabras_excluir):
    texto = f"{item['titulo']} {item['descripcion']}".lower()
    return any(p.lower() in texto for p in palabras_excluir)


def evaluar(item, senales_estafa):
    """Devuelve (nivel, motivos). nivel: 'ok' | 'duda' | 'riesgo'."""
    texto = f"{item['titulo']} {item['descripcion']} {item['url']}".lower()
    motivos = [s for s in senales_estafa if s.lower() in texto]

    # Señales extra por el enlace.
    acortadores = ["bit.ly", "tinyurl", "cutt.ly", "t.co/", "is.gd", "adf.ly"]
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
