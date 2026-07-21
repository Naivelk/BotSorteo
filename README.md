# 🎁 Buscador de sorteos → aviso por Telegram

Este programa **busca sorteos** en YouTube y en webs de sorteos, les pone una
etiqueta de confianza (🟢🟡🔴) y **te avisa por Telegram** cuando aparecen nuevos.

**Importante:** NO te inscribe en nada automáticamente. Solo te avisa para que
**tú** decidas y participes a mano. Eso es 100% legal y no arriesga tus cuentas.

---

## 🚀 Puesta en marcha (una sola vez, ~15 min)

Necesitas conseguir **3 datos** y pegarlos como "secretos" en GitHub.

### 1) Crear tu bot de Telegram (2 datos)

1. En Telegram, busca **@BotFather** y ábrelo.
2. Escribe `/newbot` y sigue los pasos (le pones nombre y usuario).
3. Al terminar te da un **TOKEN** parecido a `123456:ABC-DEF...` → ese es tu
   **TELEGRAM_BOT_TOKEN**.
4. Ahora busca tu nuevo bot, ábrelo y mándale cualquier mensaje (ej. "hola").
5. Para saber tu **CHAT_ID**: busca **@userinfobot** en Telegram, ábrelo y te
   dirá tu `Id` (un número). Ese es tu **TELEGRAM_CHAT_ID**.

### 2) Conseguir la API key de YouTube (1 dato)

1. Entra a <https://console.cloud.google.com/>
2. Crea un proyecto nuevo (arriba, "Select a project" → "New project").
3. Menú → **APIs & Services → Library** → busca **YouTube Data API v3** →
   **Enable**.
4. Menú → **APIs & Services → Credentials** → **Create credentials → API key**.
5. Copia la clave → esa es tu **YOUTUBE_API_KEY**.

> Es gratis. La cuota diaria alcanza de sobra para revisar cada 6 horas.

### 3) Subir el proyecto a GitHub y poner los secretos

1. Crea una cuenta en <https://github.com> si no tienes.
2. Crea un repositorio nuevo (puede ser privado) y sube esta carpeta.
   - Si no sabes usar git, puedes arrastrar los archivos en la web con el botón
     **"Add file → Upload files"**.
3. En el repo ve a **Settings → Secrets and variables → Actions → New
   repository secret** y crea estos tres (nombre exacto):
   - `YOUTUBE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Ve a la pestaña **Actions**, activa los workflows si te lo pide, entra a
   **"Buscar sorteos"** y dale **"Run workflow"** para probarlo ya mismo.

Si todo está bien, te llegan los sorteos por Telegram. A partir de ahí corre
**solo cada 6 horas**. 🎉

---

## ⚙️ Personalizar

Edita **`config.yaml`** (no toques el código):

- `palabras_clave`: qué cuenta como sorteo.
- `youtube_busquedas`: qué buscar en YouTube.
- `youtube_canales`: canales concretos a vigilar (opcional).
- `feeds_rss`: webs de sorteos (feeds RSS). Añade o quita las que quieras.
- `senales_estafa`: frases que marcan un sorteo como 🔴 sospechoso.

Para cambiar cada cuánto corre, edita la línea `cron` en
`.github/workflows/sorteos.yml`.

---

## 💻 Probarlo en tu PC (opcional)

```bash
pip install -r requirements.txt
copy .env.example .env      # y pega tus 3 datos dentro
python main.py
```

---

## 🛣️ Fase 2 (más adelante)

- **Facebook / Instagram**: técnicamente más difícil y frágil; se puede añadir
  después con cuidado.
- **WhatsApp**: migrar el aviso de Telegram a WhatsApp oficial (tiene costo).
- **Filtro anti-estafa avanzado**: revisar antigüedad del canal / nº de
  suscriptores en YouTube.
