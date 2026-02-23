import io
import os
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from encryptor import encrypt_data, decrypt_data

# ======= Load token từ file .env =======
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
#               COMMANDS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Xin chào {name}! 👋\n\n"
        "🔐 *Bot Mã Hóa File*\n\n"
        "📌 Các lệnh:\n"
        "• Gửi file → Bot mã hóa và gửi lại\n"
        "• /decrypt → Giải mã file\n"
        "• /getkey → Lấy key mã hóa\n"
        "• /cancel → Huỷ thao tác\n"
        "• /help → Hướng dẫn",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Hướng dẫn sử dụng:*\n\n"
        "1️⃣ *Mã hóa:* Gửi file bất kỳ\n"
        "2️⃣ *Giải mã:* Gõ /decrypt rồi gửi file .enc\n"
        "3️⃣ *Lấy key:* Gõ /getkey\n\n"
        "⚠️ Mất key = Mất dữ liệu!",
        parse_mode="Markdown"
    )

async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as f:
            await update.message.reply_document(
                InputFile(f, filename="secret.key"),
                caption="🔑 Key mã hóa của bạn!\n⚠️ Giữ bí mật!"
            )
    else:
        await update.message.reply_text("❌ Chưa có key! Hãy mã hóa 1 file trước.")

async def decrypt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "decrypt"
    await update.message.reply_text(
        "🔓 Chế độ giải mã đã bật!\n"
        "📤 Gửi file .enc để giải mã!\n"
        "❌ Gõ /cancel để huỷ."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = None
    await update.message.reply_text("❌ Đã huỷ thao tác!")

# ==========================================
#           XỬ LÝ FILE
# ==========================================

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file_name = doc.file_name
    mode = context.user_data.get("mode")

    # Tải file từ Telegram về
    file = await doc.get_file()
    file_bytes = bytes(await file.download_as_bytearray())

    # ===== CHẾ ĐỘ GIẢI MÃ =====
    if mode == "decrypt":
        await update.message.reply_text(f"⏳ Đang giải mã `{file_name}`...", parse_mode="Markdown")
        try:
            result = decrypt_data(file_bytes)
            out_name = file_name.replace(".enc", "")
            caption = f"✅ *Giải mã thành công!*\n📁 File: `{out_name}`"
        except ValueError as e:
            await update.message.reply_text(str(e))
            return
        finally:
            context.user_data["mode"] = None

    # ===== CHẾ ĐỘ MÃ HÓA =====
    else:
        await update.message.reply_text(f"⏳ Đang mã hóa `{file_name}`...", parse_mode="Markdown")
        result = encrypt_data(file_bytes)
        out_name = file_name + ".enc"
        caption = (
            f"✅ *Mã hóa thành công!*\n"
            f"📁 File: `{out_name}`\n\n"
            f"💡 Dùng /decrypt để giải mã."
        )

    # Gửi file kết quả về Telegram
    await update.message.reply_document(
        InputFile(io.BytesIO(result), filename=out_name),
        caption=caption,
        parse_mode="Markdown"
    )

# ==========================================
#               MAIN
# ==========================================

def main():
    if not BOT_TOKEN:
        print("❌ Không tìm thấy BOT_TOKEN trong file .env!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Đăng ký các lệnh
    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("getkey",  get_key))
    app.add_handler(CommandHandler("decrypt", decrypt_cmd))
    app.add_handler(CommandHandler("cancel",  cancel))

    # Đăng ký xử lý file
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🤖 Bot đang chạy! Nhấn Ctrl+C để dừng.")
    app.run_polling()

if __name__ == "__main__":
    main()