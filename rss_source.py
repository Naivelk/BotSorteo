"""Lee sorteos desde feeds RSS (Google News y cualquier otro feed que pongas)."""
import datetime
import calendar
import feedparser


def _a_fecha(struct_time):
    if not struct_time:
        return None
    return datetime.datetime.utcfromtimestamp(calendar.timegm(struct_time))


def _imagen(entry):
    """Intenta sacar una imagen del item (muchos feeds no traen)."""
    if entry.get("media_thumbnail"):
        return entry["media_thumbnail"][0].get("url")
    if entry.get("media_content"):
        return entry["media_content"][0].get("url")
    return None


def obtener(config):
    """Devuelve una lista de posibles sorteos encontrados en los feeds RSS."""
    resultados = []
    for url in config.get("feeds_rss", []):
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                print(f"[RSS] Feed sin datos o con error: {url}")
                continue
            for e in feed.entries:
                enlace = e.get("link", "")
                if not enlace:
                    continue
                resultados.append({
                    "id": f"rss:{enlace}",
                    "titulo": e.get("title", ""),
                    "descripcion": e.get("summary", ""),
                    "url": enlace,
                    "fuente": feed.feed.get("title", "Web de sorteos"),
                    "autor": feed.feed.get("title", ""),
                    "fecha_dt": _a_fecha(e.get("published_parsed")),
                    "imagen": _imagen(e),
                })
        except Exception as ex:
            print(f"[RSS] Error leyendo {url}: {ex}")
    return resultados
