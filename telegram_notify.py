"""Envía los sorteos nuevos a tu Telegram (con imagen si la hay)."""
import os
import html
import requests


def _escapar(t):
    return html.escape(t or "")


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
    """Un sorteo, en formato compacto para la lista del resumen.

    El título es un enlace clicable (así se oculta la URL larga y fea)."""
    emoji = it["etiqueta"].split()[0]              # 🟢 / 🟡 / 🔴
    if it.get("colombia"):
        globo = "🇨🇴 "
    elif it.get("internacional"):
        globo = "🌎 "
    else:
        globo = ""
    url = _escapar(it["url"])
    fuente = _escapar(it["fuente"])
    if it.get("autor") and it["autor"] != it["fuente"]:
        fuente += " · " + _escapar(it["autor"])
    return (
        f"{n}. {emoji} {globo}<a href=\"{url}\"><b>{_escapar(it['titulo'])}</b></a>\n"
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
        print(f"[Telegram] Error enviando resumen: {e}")


def enviar_resumen(items):
    """Manda UN resumen (o varios trozos si es largo) con todos los sorteos."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[Telegram] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.")
        return
    base = f"https://api.telegram.org/bot{token}"

    if not items:
        _enviar_texto(base, chat_id, "🎁 <b>Sorteos de hoy</b>\n\nHoy no hubo "
                      "sorteos nuevos. Mañana reviso otra vez. 👌")
        return

    co = sum(1 for it in items if it.get("colombia"))
    intl = sum(1 for it in items if it.get("internacional") and not it.get("colombia"))
    extras = []
    if co:
        extras.append(f"{co} de Colombia 🇨🇴")
    if intl:
        extras.append(f"{intl} internacionales 🌎")
    encabezado = (f"🎁 <b>Sorteos de hoy</b> — {len(items)} nuevos"
                  + (f" ({', '.join(extras)})" if extras else "")
                  + "\n")

    # Armar la lista partiendo en mensajes de <4000 caracteres (límite Telegram).
    trozo = encabezado
    for i, it in enumerate(items, 1):
        bloque = "\n" + _bloque_resumen(it, i) + "\n"
        if len(trozo) + len(bloque) > 3900:
            _enviar_texto(base, chat_id, trozo)
            trozo = ""
        trozo += bloque
    if trozo.strip():
        _enviar_texto(base, chat_id, trozo)


def enviar(items):
    """Manda un mensaje a Telegram por cada sorteo nuevo."""
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

        # 1) Si hay imagen, intentamos mandarla como foto con pie de texto.
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

        # 2) Si no hay imagen (o falló), mandamos texto con vista previa.
        if not enviado:
            try:
                r = requests.post(f"{base}/sendMessage", data={
                    "chat_id": chat_id, "text": mensaje,
                    "parse_mode": "HTML", "disable_web_page_preview": False,
                }, timeout=20)
                r.raise_for_status()
            except Exception as e:
                print(f"[Telegram] No se pudo enviar '{it['titulo']}': {e}")
