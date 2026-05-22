import os
import pandas as pd
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ─── FAQ tự động trong group ──────────────────────────────────
FAQ = {
    # Ebook
    "tải ebook": "📥 Bạn vui lòng nhắn tin trực tiếp với bot @MarketingBDS_bot và gõ /start để nhận ebook!",
    "nhận ebook": "📥 Bạn vui lòng nhắn tin trực tiếp với bot @MarketingBDS_bot và gõ /start để nhận ebook!",
    "download": "📥 Bạn vui lòng nhắn tin trực tiếp với bot @MarketingBDS_bot và gõ /start để nhận ebook!",
    
    # Giá cả
    "giá bao nhiêu": "💰 Vui lòng liên hệ admin @TruongKTS để được tư vấn giá chi tiết!",
    "bao nhiêu tiền": "💰 Vui lòng liên hệ admin @TruongKTS để được tư vấn giá chi tiết!",
    "chi phí": "💰 Vui lòng liên hệ admin @TruongKTS để được tư vấn giá chi tiết!",
    
    # Liên hệ
    "liên hệ": "📞 Liên hệ admin: @TruongKTS hoặc nhắn tin trực tiếp vào bot!",
    "admin": "📞 Liên hệ admin: @TruongKTS hoặc nhắn tin trực tiếp vào bot!",
    "hỗ trợ": "🆘 Để được hỗ trợ, vui lòng nhắn tin trực tiếp @MarketingBDS_bot hoặc liên hệ @TruongKTS!",
    
    # Nội dung ebook
    "ebook có gì": "📚 Ebook AI Marketing BĐS bao gồm: chiến lược marketing, công cụ AI, mẫu nội dung, case study thực tế!",
    "nội dung": "📚 Ebook AI Marketing BĐS bao gồm: chiến lược marketing, công cụ AI, mẫu nội dung, case study thực tế!",
    
    # Thanh toán
    "thanh toán": "💳 Hỗ trợ thanh toán: chuyển khoản ngân hàng, MoMo. Liên hệ @TruongKTS để biết thêm!",
    "chuyển khoản": "💳 Hỗ trợ thanh toán: chuyển khoản ngân hàng, MoMo. Liên hệ @TruongKTS để biết thêm!",
    "momo": "💳 Hỗ trợ thanh toán: chuyển khoản ngân hàng, MoMo. Liên hệ @TruongKTS để biết thêm!",
}

# ─── Quản lý khách hàng ───────────────────────────────────────
def load_customers():
    try:
        return pd.read_csv("customers.csv")
    except:
        return pd.DataFrame(columns=["telegram_id", "name", "phone", "ebook", "status"])

def save_customers(df):
    df.to_csv("customers.csv", index=False)

def is_customer(user_id):
    df = load_customers()
    return str(user_id) in df["telegram_id"].astype(str).values

# ─── Lệnh /start ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_customer(user.id):
        keyboard = [
            [InlineKeyboardButton("📥 Nhận Ebook", callback_data="get_ebook")],
            [InlineKeyboardButton("❓ Hỗ trợ", callback_data="support")],
            [InlineKeyboardButton("📋 Thông tin đơn hàng", callback_data="order_info")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Xin chào {user.first_name}! 👋\n"
            "Chào mừng bạn đến với hệ thống hỗ trợ Ebook.\n"
            "Chọn chức năng bên dưới:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "⚠️ Bạn chưa được đăng ký trong hệ thống.\n"
            "Vui lòng liên hệ admin để được hỗ trợ."
        )

# ─── Xử lý nút bấm ────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "get_ebook":
        if is_customer(user_id):
            df = load_customers()
            row = df[df["telegram_id"].astype(str) == str(user_id)].iloc[0]
            ebook_file = f"ebooks/{row['ebook']}"
            
            if os.path.exists(ebook_file):
                await context.bot.send_document(
                    chat_id=user_id,
                    document=open(ebook_file, "rb"),
                    caption=f"📚 Ebook của bạn: *{row['ebook']}*\nCảm ơn bạn đã tin tưởng!",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("❌ File chưa sẵn sàng. Admin sẽ gửi sớm!")
        else:
            await query.edit_message_text("⚠️ Bạn không có quyền nhận ebook này.")

    elif query.data == "support":
        await query.edit_message_text(
            "🆘 *Hỗ trợ khách hàng*\n\n"
            "Vui lòng mô tả vấn đề của bạn.\n"
            "Admin sẽ phản hồi trong vòng 24h.",
            parse_mode="Markdown"
        )

    elif query.data == "order_info":
        df = load_customers()
        row = df[df["telegram_id"].astype(str) == str(user_id)]
        if not row.empty:
            r = row.iloc[0]
            await query.edit_message_text(
                f"📋 *Thông tin đơn hàng*\n\n"
                f"👤 Tên: {r['name']}\n"
                f"📦 Ebook: {r['ebook']}\n"
                f"✅ Trạng thái: {r['status']}",
                parse_mode="Markdown"
            )

# ─── Lệnh Admin: thêm khách hàng ──────────────────────────────
async def add_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    # Dùng: /add <telegram_id> <tên> <phone> <ebook_file>
    try:
        args = context.args
        df = load_customers()
        new_row = {
            "telegram_id": args[0],
            "name": args[1],
            "phone": args[2],
            "ebook": args[3],
            "status": "active"
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_customers(df)
        await update.message.reply_text(f"✅ Đã thêm khách hàng: {args[1]}")
        # Thông báo cho khách hàng
        await context.bot.send_message(
            chat_id=int(args[0]),
            text=f"🎉 Tài khoản của bạn đã được kích hoạt!\n"
                 f"Gõ /start để nhận ebook."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {e}\nCú pháp: /add <id> <tên> <phone> <ebook>")

# ─── Broadcast thông báo tới tất cả KH ────────────────────────
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Cú pháp: /broadcast <nội dung>")
        return
    
    df = load_customers()
    success = 0
    for _, row in df[df["status"] == "active"].iterrows():
        try:
            await context.bot.send_message(
                chat_id=int(row["telegram_id"]),
                text=f"📢 *Thông báo từ Admin:*\n\n{message}",
                parse_mode="Markdown"
            )
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ Đã gửi tới {success}/{len(df)} khách hàng.")

# ─── Xử lý tin nhắn trong group ──────────────────────────────
async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Chỉ xử lý tin nhắn trong group, không phải private chat
    if update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    message = update.message
    if not message or not message.text:
        return
    
    text = message.text.lower()
    user = message.from_user
    
    # Kiểm tra từng câu hỏi trong FAQ
    for keyword, answer in FAQ.items():
        if keyword in text:
            await message.reply_text(
                f"👋 {user.first_name}, {answer}",
                parse_mode="Markdown"
            )
            return  # Chỉ trả lời 1 lần
    
    # Nếu có đề cập (@mention) bot thì trả lời hướng dẫn
    bot_username = context.bot.username
    if f"@{bot_username}".lower() in text:
        await message.reply_text(
            "👋 Xin chào! Tôi là bot hỗ trợ Ebook.\n"
            "📥 Nhắn tin trực tiếp với tôi và gõ /start để nhận ebook!\n"
            "❓ Hoặc liên hệ admin @TruongKTS để được hỗ trợ."
        )

# ─── Khởi chạy Bot ────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_customer))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_message_handler))
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()