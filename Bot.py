import logging
import dropbox
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens
BOT_TOKEN = '7435095569:AAFgJSZk1tQNUZ7DM54QLNNVMr-y_kv_uhs'
DROPBOX_ACCESS_TOKEN = "sl.u.AFq0gx4y96xwJEXo6MyED1QryqAvPeB3x0kS8amM1MfXiWCdqjVLsgbXMgM0y3Vt4TzwFuYbR34g0ACYDLpu8IA6N5t_HYQK7lQ7rxDqdP8uvlmlxX_CltpzvJOj7rNyfkSasT7z1U7y0GoBPsg3fc7LI2Eq8XjQHO9ObW9njpjTBWKXvFnRxRBb96PFhl725VyIxkpamJw5AxNAu6tPu36UuGza1gwdiSracI9_d4dLrsblBjZwXv10rRMSBnuijbayBekvKjYk3RfV4PisNhZCUT599PExKXep9ccq91-wi7iJHfc3_is61yeJE9nUZIqnLdAwef3QMHr_DDkLzwml8CZYqWg80pv3FGktNbFtVld4J702PGfupJPT-rTMyb0PjgY6rp4X5pprjgPOrfj_D_p_tU4XtKY2oXGXWm2e8F0zLqrxb1K7r3efeVq3WinRQaiY1HYt9AhygaGxumm1qFDHzfwPBHoH9wZOcLAUF6tbAiwc8pD18oqvJLXBNWGzvRiUTzYylk8V4gZfiUUe-MD6KiDnFIYkm91BQF3K6oTLFLYOUvNtS36JEf0Bv3Gap9U-yQizWIADz04RlffHAwzoeVudT_fSxG3eGUQ-uiWMn2XOEj2qWjZ07vP5R-Xtgt7YoXX5vwus-5h-yoAS9e1XwWtaseiQpPbpeHXE-pxm2MI5Tmcr4MQXJ_iH6_9F-57FXRlu1-MhL2PNr4zpEknb8cTN3od8fSlsYfXN4tJZK_OnvTx3UEcFvSm02iYe68Wk1O50myAscjDXeOpwempt5863Z8sw38SZHwWV-JQqkc-IBz0roHeTzdcWtsPhDJfTd-ylb409xRr0qOoK7--gf61yLMqJLPs4kq-qtD7zFHlLG1D_DwJXNh4o8D2-wsJw0KF7gdQa_AEv17OyW4o9AAnxjX80OIez0-4wu4WelhcVW7uGmbBIOW8KpsPoS51ISx8WYg3HvsXFlMcvGa_8VKUah7IPAKz58xBfYrVZwKz5-iqD6cosLLiNyqVYdDWKELHQMTgYxyjnbQI6I-xKThxc9la95VgwALlebATFPYMZlJfE-WEyIkj1_dNS2vp6-7JMtBCn3Yd3EcymFgLmlqAl7sunmC_U7_ws73DbFSPPfH2L-SzXDXrrFx90ZSw4PvK1lnKTy7Q2sLUaxKAEupXsgFUhR74TNArh1dCs2TfzXzX0KvS9KL5m0IKYbraQ4G1ilbRHKsTFsjfbweMUMwYjq-cKMCJoV5N27442O8ljcM7yd3nGoU0TlMLneiO7ZzcuUCX_IKlaFz2j1IE6srrOPhaUEqa-uI0X0Ci2YWt-v2k9VcYmrcbGbGIVc_WmGMMoUlQXS7GP-nunMWwXaW5hqj3OjHGSc3KnKGnl0cY8hIhoSydkD-p3AYCYDzT12gyebc3F_B6bQsvM"

# Dropbox upload
def upload_to_dropbox(local_file_path, dropbox_dest_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(local_file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_dest_path, mode=dropbox.files.WriteMode("overwrite"))
    logger.info(f"Uploaded {local_file_path} to Dropbox at {dropbox_dest_path}")

# Dropbox delete
def delete_from_dropbox(dropbox_path):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    dbx.files_delete_v2(dropbox_path)
    logger.info(f"Deleted file from Dropbox: {dropbox_path}")

# /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Owner  --⟩ [KING - ALI] ⟨--\nSend me a file and I will rename, upload to Dropbox, send back, and clean up.")

# File received
async def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document
    if file:
        context.user_data['file_name'] = file.file_name
        context.user_data['file_id'] = file.file_id
        context.user_data['file_extension'] = os.path.splitext(file.file_name)[1]
        await update.message.reply_text(f"Send a new name for the file (without extension):")

# Rename and send back
async def rename_file(update: Update, context: CallbackContext) -> None:
    new_name = update.message.text.strip()
    
    if 'file_name' in context.user_data:
        original_name = context.user_data['file_name']
        file_id = context.user_data['file_id']
        extension = context.user_data['file_extension']
        new_file_name = f"{new_name}{extension}"

        original_path = f"/data/data/com.termux/files/home/{original_name}"
        renamed_path = f"/data/data/com.termux/files/home/{new_file_name}"
        dropbox_path = f"/{new_file_name}"

        try:
            msg = await update.message.reply_text("Downloading file...")
            telegram_file = await context.bot.get_file(file_id)
            await telegram_file.download_to_drive(original_path)

            await msg.edit_text("Renaming file...")
            os.rename(original_path, renamed_path)

            await msg.edit_text("Uploading to Dropbox...")
            upload_to_dropbox(renamed_path, dropbox_path)

            await msg.edit_text("Sending file back...")
            with open(renamed_path, 'rb') as f:
                await update.message.reply_document(document=f, filename=new_file_name)

            await msg.edit_text("Cleaning up...")
            delete_from_dropbox(dropbox_path)
            os.remove(renamed_path)

            await msg.edit_text("Done!")

        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"Something went wrong:\n{e}")
    else:
        await update.message.reply_text("Please send a file first.")

# Error handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

# Main
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, rename_file))
    app.add_error_handler(error)

    app.run_polling()

if __name__ == '__main__':
    main()
