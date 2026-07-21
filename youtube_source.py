"""
Lee sorteos desde YouTube.
- Canales concretos: por RSS, SIN API key (trae también la miniatura/imagen).
- Búsquedas por palabra: usan la API oficial (opcional, solo si hay API key).
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


def _por_canales_rss(config):
    """Videos de canales concretos, sin API key. Incluye imagen."""
    items = []
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
            print(f"[YouTube RSS] Error en canal '{canal}': {e}")
    return items


def _por_busqueda_api(config):
    """Búsquedas por palabra usando la API (solo si hay API key válida)."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        return []

    horas = config.get("youtube_horas_atras", 48)
    desde = (datetime.datetime.utcnow() -
             datetime.timedelta(hours=horas)).strftime("%Y-%m-%dT%H:%M:%SZ")

    items = []
    for consulta in config.get("youtube_busquedas", []):
        try:
            r = requests.get(API_URL, params={
                "q": consulta, "publishedAfter": desde, "key": api_key,
                "part": "snippet", "type": "video", "order": "date",
                "maxResults": 25,
            }, timeout=20)
            r.raise_for_status()
            for it in r.json().get("items", []):
                vid = it.get("id", {}).get("videoId")
                snip = it.get("snippet", {})
                if not vid:
                    continue
                fecha = snip.get("publishedAt", "")
                try:
                    fdt = datetime.datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ")
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
        except Exception as e:
            print(f"[YouTube API] Error buscando '{consulta}': {e}")
    return items


def obtener(config):
    return _por_canales_rss(config) + _por_busqueda_api(config)
