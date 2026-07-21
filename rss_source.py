"""Lee sorteos desde feeds RSS de webs de sorteos (más estable que scraping)."""
import feedparser


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
                    "fecha": e.get("published", ""),
                })
        except Exception as ex:
            print(f"[RSS] Error leyendo {url}: {ex}")
    return resultados
