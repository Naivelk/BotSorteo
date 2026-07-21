"""
Lee sorteos desde YouTube.
- Canales concretos: por RSS, SIN API key (trae también la miniatura/imagen).
- Búsquedas por palabra: usan la API oficial (opcional, solo si hay API key).
Devuelve (items, errores) para poder avisar si algo se rompe.
"""
import os
import datetime
import calendar
import feedparser
import requests

API_URL = "https://www.googleapis.com/youtube/v3/search"
CANAL_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={}"


def _a_fecha(struct_time):
    if not struct_time:
        return None
    return datetime.datetime.utcfromtimestamp(calendar.timegm(struct_time))


def _buscar_api(consulta, desde, api_key):
    """Una búsqueda por la API. Devuelve lista de items (o lanza excepción)."""
    r = requests.get(API_URL, params={
        "q": consulta, "publishedAfter": desde, "key": api_key,
        "part": "snippet", "type": "video", "order": "date", "maxResults": 25,
    }, timeout=20)
    r.raise_for_status()
    items = []
    for it in r.json().get("items", []):
        vid = it.get("id", {}).get("videoId")
        snip = it.get("snippet", {})
        if not vid:
            continue
        try:
            fdt = datetime.datetime.strptime(
                snip.get("publishedAt", ""), "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            fdt = None
        items.append({
            "id": f"yt:{vid}",
            "titulo": snip.get("title", ""),
            "descripcion": snip.get("description", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "fuente": "YouTube",
            "autor": snip.get("channelTitle", ""),
            "fecha_dt": fdt,
            "imagen": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        })
    return items


def obtener(config):
    """Devuelve (items, errores). errores lista fallos para el aviso técnico."""
    errores = []
    items = []

    # 1) Canales concretos por RSS (sin API key, con imagen).
    for canal in config.get("youtube_canales", []):
        try:
            feed = feedparser.parse(CANAL_RSS.format(canal))
            for e in feed.entries:
                vid = e.get("yt_videoid")
                if not vid:
                    continue
                items.append({
                    "id": f"yt:{vid}",
                    "titulo": e.get("title", ""),
                    "descripcion": e.get("summary", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "fuente": "YouTube",
                    "autor": e.get("author", ""),
                    "fecha_dt": _a_fecha(e.get("published_parsed")),
                    "imagen": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                })
        except Exception as e:
            errores.append(f"YouTube canal {canal}: {e}")

    # 2) Búsquedas por API (solo si hay key). Si la key falla, se reporta 1 vez.
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key:
        error_api = None
        horas = config.get("youtube_horas_atras", 48)
        desde = (datetime.datetime.utcnow() -
                 datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for consulta in config.get("youtube_busquedas", []):
            try:
                items += _buscar_api(consulta, desde, api_key)
            except Exception as e:
                error_api = str(e)  # misma causa para todas; guardar una vez
        if error_api:
            errores.append(f"YouTube API: {error_api}")

    return items, errores
