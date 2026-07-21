"""
Buscador de sorteos -> te avisa por Telegram.
Corre solo (GitHub Actions o tu PC). No inscribe en nada: solo te avisa
para que TÚ decidas y participes a mano.
"""
import json
import os
import datetime
import yaml

import youtube_source
import rss_source
import scam_filter
import telegram_notify

ARCHIVO_VISTOS = "state/seen.json"
MAX_POR_CORRIDA = 15  # no mandar más de N avisos de golpe


def cargar_env_local():
    """Si existe un archivo .env (solo para probar en tu PC), lo carga."""
    if not os.path.exists(".env"):
        return
    with open(".env", "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())


def cargar_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_vistos():
    try:
        with open(ARCHIVO_VISTOS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def guardar_vistos(vistos):
    os.makedirs("state", exist_ok=True)
    with open(ARCHIVO_VISTOS, "w", encoding="utf-8") as f:
        json.dump(sorted(vistos), f, ensure_ascii=False, indent=2)


def main():
    cargar_env_local()
    config = cargar_config()
    vistos = cargar_vistos()

    # 1) Recolectar de todas las fuentes.
    items = youtube_source.obtener(config) + rss_source.obtener(config)
    print(f"Encontrados {len(items)} elementos en total.")

    palabras = config.get("palabras_clave", [])
    excluir = config.get("palabras_excluir", [])
    senales = config.get("senales_estafa", [])
    max_dias = config.get("max_dias_antiguedad", 4)
    limite_fecha = datetime.datetime.utcnow() - datetime.timedelta(days=max_dias)

    # 2) Filtrar: relevantes + no vistos + recientes + sin ruido; evaluar riesgo.
    nuevos = []
    for it in items:
        if it["id"] in vistos:
            continue
        if not scam_filter.es_relevante(it, palabras):
            continue
        if scam_filter.esta_excluido(it, excluir):
            continue
        fecha = it.get("fecha_dt")
        if fecha and fecha < limite_fecha:
            continue  # demasiado viejo
        nivel, motivos = scam_filter.evaluar(it, senales)
        it["etiqueta"] = scam_filter.ETIQUETA[nivel]
        it["motivos"] = motivos
        nuevos.append(it)

    print(f"Sorteos nuevos relevantes: {len(nuevos)}")

    # 3) Ordenar (primero los que parecen legítimos) y limitar.
    orden = {"🟢 Parece legítimo": 0, "🟡 Revísalo con cuidado": 1,
             "🔴 Sospechoso (posible estafa)": 2}
    nuevos.sort(key=lambda x: orden.get(x["etiqueta"], 3))
    a_enviar = nuevos[:MAX_POR_CORRIDA]

    # 4) Avisar y recordar como vistos SOLO los que sí se enviaron
    #    (los sobrantes se enviarán en la siguiente corrida).
    telegram_notify.enviar(a_enviar)
    for it in a_enviar:
        vistos.add(it["id"])
    guardar_vistos(vistos)
    print("Listo.")


if __name__ == "__main__":
    main()
