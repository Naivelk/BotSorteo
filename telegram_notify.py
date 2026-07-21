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
