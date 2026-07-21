"""Envía los sorteos nuevos a tu Telegram (resumen por secciones o con imagen)."""
import os
import html
import requests

# Secciones del resumen, en orden de prioridad.
SECCIONES = [
    ("colombia", "🇨🇴 <b>De / para Colombia</b>"),
    ("internacional", "🌎 <b>Internacionales</b>"),
    ("otros", "🌐 <b>Otros</b>"),
]


def _escapar(t):
    return html.escape(t or "")


def _bucket(it):
    if it.get("colombia"):
        return "colombia"
    if it.get("internacional"):
        return "internacional"
    return "otros"


def _texto(it):
    msg = (
        f"{it['etiqueta']}\n\n"
        f"<b>{_escapar(it['titulo'])}</b>\n"
        f"📺 {_escapar(it['fuente'])}"
        + (f" · {_escapar(it['autor'])}" if it.get('autor') else "")
        + f"\n🔗 {_escapar(it['url'])}"
    )
    if it.get("motivos"):
        msg += "\n⚠️ " + _escapar(", ".join(it["motivos"]))
    return msg


def _bloque_resumen(it, n):
    """Un sorteo en formato compacto; el título es un enlace clicable."""
    emoji = it["etiqueta"].split()[0]              # 🟢 / 🟡 / 🔴
    url = _escapar(it["url"])
    fuente = _escapar(it["fuente"])
    if it.get("autor") and it["autor"] != it["fuente"]:
        fuente += " · " + _escapar(it["autor"])
    return (
        f"{n}. {emoji} <a href=\"{url}\"><b>{_escapar(it['titulo'])}</b></a>\n"
        f"   <i>{fuente}</i>"
    )


def _enviar_texto(base, chat_id, texto):
    try:
        r = requests.post(f"{base}/sendMessage", data={
            "chat_id": chat_id, "text": texto, "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[Telegram] Error enviando mensaje: {e}")


def _enviar_en_trozos(base, chat_id, partes):
    """Une las partes y las manda en mensajes de <4000 chars (límite Telegram)."""
    trozo = ""
    for p in partes:
        add = ("\n\n" if trozo else "") + p
        if len(trozo) + len(add) > 3900:
            _enviar_texto(base, chat_id, trozo)
            trozo = p
        else:
            trozo += add
    if trozo.strip():
        _enviar_texto(base, chat_id, trozo)


def enviar_resumen(items, nota=None):
    """Manda el resumen del día, agrupado por secciones. `nota` = aviso técnico."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[Telegram] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.")
        return
    base = f"https://api.telegram.org/bot{token}"

    if nota:                       # aviso de que algo se rompió
        _enviar_texto(base, chat_id, nota)

    if not items:
        if not nota:
            _enviar_texto(base, chat_id, "🎁 <b>Sorteos de hoy</b>\n\nHoy no "
                          "hubo sorteos nuevos. Mañana reviso otra vez. 👌")
        return

    # Agrupar por sección.
    grupos = {"colombia": [], "internacional": [], "otros": []}
    for it in items:
        grupos[_bucket(it)].append(it)

    partes = [f"🎁 <b>Sorteos de hoy</b> — {len(items)} nuevos"]
    n = 1
    for clave, titulo_sec in SECCIONES:
        grupo = grupos[clave]
        if not grupo:
            continue
        partes.append(f"{titulo_sec}  ({len(grupo)})")
        for it in grupo:
            partes.append(_bloque_resumen(it, n))
            n += 1

    _enviar_en_trozos(base, chat_id, partes)


def enviar(items):
    """Manda un mensaje suelto por cada sorteo (modo con imagen)."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[Telegram] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.")
        return
    if not items:
        print("[Telegram] No hay sorteos nuevos que enviar.")
        return

    base = f"https://api.telegram.org/bot{token}"
    for it in items:
        mensaje = _texto(it)
        imagen = it.get("imagen")
        enviado = False
        if imagen:
            try:
                r = requests.post(f"{base}/sendPhoto", data={
                    "chat_id": chat_id, "photo": imagen,
                    "caption": mensaje, "parse_mode": "HTML",
                }, timeout=20)
                r.raise_for_status()
                enviado = True
            except Exception as e:
                print(f"[Telegram] Foto falló, mando como texto: {e}")
        if not enviado:
            try:
                r = requests.post(f"{base}/sendMessage", data={
                    "chat_id": chat_id, "text": mensaje,
                    "parse_mode": "HTML", "disable_web_page_preview": False,
                }, timeout=20)
                r.raise_for_status()
            except Exception as e:
                print(f"[Telegram] No se pudo enviar '{it['titulo']}': {e}")
