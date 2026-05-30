# main.py
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Carga variables antes de importar servicios que usan API keys.
load_dotenv()

from services.llm_service import analyze_lead
from services.sheets_service import log_lead

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Responde cuando el usuario manda /start.
    await update.message.reply_text(
        "Bot activo.\nEnviame un lead y lo analizo."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Captura el texto enviado por Telegram y lo manda al flujo de analisis.
    text = update.message.text
    print(f"[Telegram] Mensaje recibido: {text}")

    await update.message.reply_text("Analizando lead...")

    try:
        result = analyze_lead(text)
    except Exception:
        print("[LLM] Fallo el analisis del lead")
        await update.message.reply_text(
            "No pude analizar el lead en este momento. Revisemos la configuracion del proveedor LLM."
        )
        return

    decision = "Cualificado" if result["qualified"] else "No cualificado"

    reply = f"""{decision}

{result["reason"]}"""

    await update.message.reply_text(reply)

    # Guarda el lead despues de responder para que Sheets no bloquee al usuario.
    print("[Sheets] Intentando guardar lead...")
    sheets_ok = log_lead(text, result)

    if sheets_ok:
        print("[Sheets] Lead guardado correctamente")
    else:
        print("[Sheets] Fallo el guardado del lead")


def main():
    print("[Bot] Iniciando Orbyn Lead Bot...")

    # Crea la app del bot usando el token de BotFather.
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler para /start.
    app.add_handler(CommandHandler("start", start))

    # Handler para mensajes normales de texto.
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[Bot] Bot corriendo con polling...")

    # Mantiene el bot escuchando mensajes.
    app.run_polling()


if __name__ == "__main__":
    main()
