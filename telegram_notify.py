"""Envía los sorteos nuevos a tu Telegram."""
import os
import html
import requests


def _escapar(t):
    return html.escape(t or "")


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

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for it in items:
        mensaje = (
            f"{it['etiqueta']}\n\n"
            f"<b>{_escapar(it['titulo'])}</b>\n"
            f"📺 {_escapar(it['fuente'])}"
            + (f" · {_escapar(it['autor'])}" if it.get('autor') else "")
            + f"\n🔗 {_escapar(it['url'])}"
        )
        if it.get("motivos"):
            mensaje += "\n⚠️ " + _escapar(", ".join(it["motivos"]))

        try:
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": mensaje,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            }, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print(f"[Telegram] No se pudo enviar '{it['titulo']}': {e}")
