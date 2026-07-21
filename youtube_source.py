"""Lee sorteos desde YouTube usando la API oficial (gratis)."""
import os
import datetime
import requests

API_URL = "https://www.googleapis.com/youtube/v3/search"


def _buscar(params, api_key):
    params["key"] = api_key
    params["part"] = "snippet"
    params["type"] = "video"
    params["order"] = "date"
    params["maxResults"] = 25
    r = requests.get(API_URL, params=params, timeout=20)
    r.raise_for_status()
    items = []
    for it in r.json().get("items", []):
        vid = it.get("id", {}).get("videoId")
        snip = it.get("snippet", {})
        if not vid:
            continue
        items.append({
            "id": f"yt:{vid}",
            "titulo": snip.get("title", ""),
            "descripcion": snip.get("description", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "fuente": "YouTube",
            "autor": snip.get("channelTitle", ""),
            "fecha": snip.get("publishedAt", ""),
        })
    return items


def obtener(config):
    """Devuelve una lista de posibles sorteos encontrados en YouTube."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("[YouTube] Falta YOUTUBE_API_KEY, se omite YouTube.")
        return []

    horas = config.get("youtube_horas_atras", 48)
    desde = (datetime.datetime.utcnow() -
             datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%SZ")

    resultados = []
    for consulta in config.get("youtube_busquedas", []):
        try:
            resultados += _buscar({"q": consulta, "publishedAfter": desde}, api_key)
        except Exception as e:
            print(f"[YouTube] Error buscando '{consulta}': {e}")

    for canal in config.get("youtube_canales", []):
        try:
            resultados += _buscar(
                {"channelId": canal, "publishedAfter": desde}, api_key)
        except Exception as e:
            print(f"[YouTube] Error en canal '{canal}': {e}")

    return resultados
