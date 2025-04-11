import os
import json
import asyncio
import aiohttp
import nest_asyncio
nest_asyncio.apply()
import requests
import json
import asyncio
import aiohttp
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import ConversationHandler
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)


from telegram import BotCommand
from telegram.ext import ApplicationBuilder



def save_approved_users():
    with open("approved_users.json", "w") as f:
        json.dump(list(approved_users), f)


def load_approved_users():
    try:
        with open("approved_users.json", "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


# Áp dụng nest_asyncio nếu chạy trên môi trường async như Jupyter, Replit...
nest_asyncio.apply()

# === Cấu hình ===
TELEGRAM_BOT_TOKEN = "6850377308:AAH4Onov4rbqyN8BK5Y26a0KVZ44_-pQqhs"
UID_FILE = "uids.json"
STATUS_FILE = "status.json"
CHECK_INTERVAL = 10  # giây


# === File IO ===

def load_uids():
    if os.path.exists(UID_FILE):
        with open(UID_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_uids(data):
    with open(UID_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_status(data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#get id tele
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 ID Telegram của bạn là: `{user.id}`", parse_mode="Markdown")


# ✅ Lệnh /duyet

# Danh sách các Admin ID
admin_ids = {5973850512, 1342890563}  # ← Thêm ID admin khác tại đây
approved_users = set()


def is_approved(user_id):
    return user_id in admin_ids or user_id in approved_users


def require_approval(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_approved(user_id):
            await update.message.reply_text(
                f"🚫 *Bạn chưa được duyệt để sử dụng bot!*\n\n"
                f"🆔 *ID của bạn:* `{user_id}`\n"
                "🧑‍💻 *Admin:* Lê Thịnh Đạt\n"
                "📱 *Zalo:* `0924130629`\n\n"
                "👉 *Vui lòng sao chép ID và nhắn tin cho Admin qua Zalo để được cấp quyền sử dụng bot.*\n"
                "💬 Sau khi được duyệt, bạn sẽ có quyền sử dụng đầy đủ tính năng!",
                parse_mode="Markdown"
            )
            return
        return await func(update, context)
    return wrapper


async def duyet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print("👤 Gọi /duyet bởi:", user_id)

    if user_id not in admin_ids:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return

    try:
        target_id = int(context.args[0])
        approved_users.add(target_id)
        save_approved_users()
        await update.message.reply_text(f"✅ Đã duyệt user có ID: {target_id}")
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "🎉 *Chúc mừng!*\n\n"
                "✅ Bạn đã được Admin duyệt sử dụng bot.\n"
                "Hãy dùng lệnh /start để bắt đầu nhé!\n\n"
                "🤖 Chúc bạn sử dụng vui vẻ~"
            ),
            parse_mode="Markdown"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Dùng đúng cú pháp: /duyet <user_id>")

#huy duyet
async def huy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print("🗑 Gọi /huy bởi:", user_id)

    if user_id not in admin_ids:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return

    try:
        target_id = int(context.args[0])
        if target_id in approved_users:
            approved_users.remove(target_id)
            save_approved_users()  # Nếu bạn có lưu file
            await update.message.reply_text(f"🗑 Đã hủy duyệt user có ID: {target_id}")
        else:
            await update.message.reply_text("⚠️ User này chưa được duyệt.")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Dùng đúng cú pháp: /huy <user_id>")




# === File IO ===
def load_uids():
    try:
        with open("uids.json", "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            data = json.loads(content)
            # Chuyển định dạng cũ sang mới (nếu có)
            for chat_id in data:
                new_list = []
                for entry in data[chat_id]:
                    if isinstance(entry, str):
                        new_list.append({"uid": entry, "name": "Chưa đặt tên"})
                    else:
                        new_list.append(entry)
                data[chat_id] = new_list
            return data
    except Exception:
        return {}





# get uid


def get_uid(fb_url: str) -> str:
    """Lấy UID từ link Facebook bằng API Trao Đổi Sub"""
    api_url = "https://id.traodoisub.com/api.php"
    
    try:
        response = requests.post(api_url, data={"link": fb_url})
        data = response.json()
        
        if "id" in data:
            return data["id"]
        else:
            return "Không tìm thấy UID!"
    
    except Exception as e:
        return f"Lỗi: {e}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Nếu đang đợi người dùng nhập ghi chú
    if context.user_data.get("awaiting_note"):
        await handle_note_input(update, context)
        return

    # Nếu đang đợi người dùng nhập tên
    if context.user_data.get("awaiting_name"):
        await handle_name_input(update, context)
        return

    # Nếu đang thêm UID
    if context.user_data.get("adding_uid"):
        await add_uid(update, context)
        return

    # Nếu là link hoặc UID và không trong quá trình thêm UID
    if "facebook.com" in text or text.isdigit():
        await update.message.reply_text("🔍 Đang lấy UID từ link...")
        uid = get_uid(text) if "facebook.com" in text else text
        if not uid.isdigit():
            await update.message.reply_text(f"❌ Không tìm thấy UID: {uid}")
            return
        await update.message.reply_text(f"✅ UID của bạn là: `{uid}`", parse_mode="Markdown")
        return

    # Mặc định
    await update.message.reply_text("🚫 Vui lòng gửi một liên kết Facebook hợp lệ hoặc UID số!")








    
    
# === UID Checker ===

async def check_uid(session, uid):
    url = f"https://graph.facebook.com/{uid}/picture?type=normal"
    try:
        async with session.get(url, allow_redirects=True) as resp:
            final_url = str(resp.url)
            if "100x100" in final_url:
                return "live"
            else:
                return "die"
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra UID {uid}: {e}")
        return "die"


async def periodic_check(context: ContextTypes.DEFAULT_TYPE):
    uids = load_uids()
    prev_status = load_status()
    updated_status = {}

    async with aiohttp.ClientSession() as session:
        for chat_id, uid_list in uids.items():
            results = await asyncio.gather(*(check_uid(session, entry["uid"]) for entry in uid_list))

            for entry, status in zip(uid_list, results):
                uid = entry["uid"]
                name = entry["name"]
                key = f"{chat_id}_{uid}"
                old_status = prev_status.get(key)
                updated_status[key] = status

                # Nếu trạng thái thay đổi → thông báo ngay
                if old_status != status:
                    emoji = "✅" if status == "live" else "❌"
                    await context.bot.send_message(
                        chat_id=int(chat_id),
                        text=f"{emoji} UID [{uid}](https://facebook.com/{uid}) ({name}) đã chuyển sang trạng thái: *{status.upper()}*",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )

    save_status(updated_status)






# === Bot commands ===
@require_approval
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Thêm UID", callback_data="add_uid")],
        [InlineKeyboardButton("🗑 Xóa UID", callback_data="remove_uid")],
        [InlineKeyboardButton("📋 Danh sách UID", callback_data="list_uids")],
        [InlineKeyboardButton("🔄 Kiểm tra UID", callback_data="check_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔹 Chọn thao tác:", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Hướng dẫn sử dụng bot:*\n"
        "\n/start - Hiển thị MENU thao tác"
        "\n/save - Lưu UID để theo dõi"
        "\n/delete - Xóa UID không cần theo dõi"
        "\n/list - Danh sách UID được lưu lại"
        "\n/check - Trạng thái của UID"
        "\n/help - Hiển thị hướng dẫn sử dụng"
        "\n\n*Các chức năng:*"
        "\n✅ Thêm UID: Bấm nút và gửi UID Facebook"
        "\n🗑 Xóa UID: Chọn UID muốn xoá khỏi danh sách"
        "\n📋 Danh sách UID: Xem các UID bạn đang theo dõi"
        "\n🔄 Kiểm tra UID: Kiểm tra tình trạng Live/Die của UID"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    msg = query.message

    if data == "add_uid":
        context.user_data["adding_uid"] = True
        await msg.reply_text("✍ Vui lòng gửi UID Facebook bạn muốn thêm.")

    elif data == "remove_uid":
        await remove_uid_menu(chat_id, context, msg)
    elif data == "list_uids":
        await list_uids(chat_id, context, msg)
    elif data == "check_all":
        await check_all(chat_id, context, msg)

#add uid
@require_approval
async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["adding_uid"] = True
    await update.message.reply_text("📥 Vui lòng gửi UID hoặc link Facebook:")

# ======= Nhận UID ban đầu =======
async def add_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not context.user_data.get("adding_uid"):
        return

    raw_input = update.message.text.strip()
    chat_id = str(update.message.chat_id)
    uids = load_uids()

    if "facebook.com" in raw_input:
        uid = get_uid(raw_input)
        if not uid.isdigit():
            await update.message.reply_text(f"❌ Không tìm thấy UID: {uid}")
            context.user_data["adding_uid"] = False
            return
    else:
        uid = raw_input

    if not uid.isdigit() or len(uid) < 5 or len(uid) > 20:
        await update.message.reply_text("❌ UID không hợp lệ.")
        context.user_data["adding_uid"] = False
        return

    if chat_id not in uids:
        uids[chat_id] = []

    if any(entry["uid"] == uid for entry in uids[chat_id]):
        await update.message.reply_text(f"⚠️ UID [{uid}](https://www.facebook.com/{uid}) đã tồn tại.", parse_mode="Markdown")
        context.user_data["adding_uid"] = False
        return

    context.user_data["pending_uid"] = uid
    context.user_data["awaiting_name"] = True
    context.user_data["adding_uid"] = False

    await update.message.reply_text("✏️ Vui lòng nhập tên bạn muốn gán cho UID này:")

# ======= Nhập tên UID =======
async def handle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_name") or not update.message:
        return

    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("⚠️ Tên không được để trống. Vui lòng nhập lại:")
        return

    context.user_data["pending_name"] = name
    context.user_data["awaiting_name"] = False
    context.user_data["awaiting_note"] = True

    await update.message.reply_text("📝 Vui lòng nhập ghi chú cho UID này (hoặc gửi `-` nếu không có):")

# ======= Nhập ghi chú =======
async def handle_note_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_note") or not update.message:
        return

    note = update.message.text.strip()
    if note == "-":
        note = ""

    uid = context.user_data.get("pending_uid")
    name = context.user_data.get("pending_name")
    chat_id = str(update.message.chat_id)
    uids = load_uids()

    if not uid or not name:
        await update.message.reply_text("❌ Thiếu thông tin UID hoặc tên.")
        context.user_data.clear()
        return

    uids.setdefault(chat_id, []).append({
        "uid": uid,
        "name": name,
        "note": note,
        "status": "Unknown"
    })
    save_uids(uids)

    await update.message.reply_text(
        f"✅ Đã thêm UID: [{uid}](https://www.facebook.com/{uid})\n📛 Tên: *{name}*\n📝 Ghi chú: *{note or 'Không có'}*",
        parse_mode="Markdown"
    )

    context.user_data.clear()



#list uid
@require_approval
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await list_uids(chat_id, context, update.message)

async def list_uids(chat_id, context: ContextTypes.DEFAULT_TYPE, msg):
    uids = load_uids()
    chat_id = str(chat_id)

    if chat_id not in uids or not uids[chat_id]:
        await msg.reply_text("📭 Danh sách UID trống!")
        return

    uid_list = "\n\n".join(
        f"🧑‍💼 Tên: *{entry['name']}*\n🆔 [{entry['uid']}](https://facebook.com/{entry['uid']})\n📝 Ghi chú: {entry.get('note', 'Không có') or 'Không có'}"
        for entry in uids[chat_id]
    )

    await msg.reply_text(
        f"📋 *Danh sách UID:*\n\n{uid_list}",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )





#xoa uid
@require_approval
async def delete_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = update.message
    await remove_uid_menu(chat_id, context, msg)

async def remove_uid_menu(chat_id, context: ContextTypes.DEFAULT_TYPE, msg):
    uids = load_uids()
    chat_id = str(chat_id)

    if chat_id not in uids or not uids[chat_id]:
        await msg.reply_text("📭 Không có UID để xóa!")
        return
    keyboard = [
    [InlineKeyboardButton(
        text=f"👤 {entry['name']}",   
        callback_data=f"del_{entry['uid']}"
    )]
    for entry in uids[chat_id]
]



    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.reply_text("🗑 Chọn UID để xóa:", reply_markup=reply_markup)
async def remove_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid_to_remove = query.data.replace("del_", "")
    chat_id = str(query.message.chat.id)

    uids = load_uids()
    if chat_id in uids:
        uids[chat_id] = [entry for entry in uids[chat_id] if entry["uid"] != uid_to_remove]
        if not uids[chat_id]:
         del uids[chat_id]
    save_uids(uids)
    await query.message.reply_text(f"✅ Đã xóa UID [{uid_to_remove}](https://www.facebook.com/{uid_to_remove})", parse_mode="Markdown")
    await remove_uid_menu(chat_id, context, query.message)




#check all uid
@require_approval
async def check_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = update.message
    await check_all(chat_id, context, msg)

async def check_all(chat_id, context: ContextTypes.DEFAULT_TYPE, msg):
    uids = load_uids()
    chat_id = str(chat_id)
    prev_status = load_status()
    updated_status = {}

    if chat_id not in uids or not uids[chat_id]:
        await msg.reply_text("📭 Danh sách UID trống!")
        return

    await msg.reply_text("🔄 Đang kiểm tra UID...")

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(check_uid(session, entry["uid"]) for entry in uids[chat_id]))

    live_text = ""
    die_text = ""

    for entry, status in zip(uids[chat_id], results):
        uid = entry["uid"]
        name = entry["name"]
        note = entry.get("note", "Không có") or "Không có"
        updated_status[f"{chat_id}_{uid}"] = status

        line = f"🧑‍💼 {name}\n🆔 [{uid}](https://facebook.com/{uid})\n📝 Ghi chú: {note}\n\n"
        if status == "live":
            live_text += line
        else:
            die_text += line

    save_status({**prev_status, **updated_status})

    result_text = "📋 *Kết quả kiểm tra:*\n\n"
    if live_text:
        result_text += "✅ *UID Live:*\n\n" + live_text
    if die_text:
        result_text += "❌ *UID Die:*\n\n" + die_text

    await msg.reply_text(result_text, parse_mode="Markdown", disable_web_page_preview=True)


#thong bao

async def thong_bao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_ids:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập nội dung thông báo sau lệnh /thongbao.")
        return

    message = "📢 Thông báo từ ADMIN:\n" + " ".join(context.args)

    sent_count = 0
    for uid in approved_users:
        try:
            await context.bot.send_message(chat_id=uid, text=message)
            sent_count += 1
        except Exception as e:
            print(f"Không gửi được tới {uid}: {e}")

    await update.message.reply_text(f"✅ Đã gửi thông báo đến {sent_count} người dùng được duyệt.")



from telegram import Update
from telegram.ext import ContextTypes
import requests

ACCESS_TOKEN = "EAAGNO4a7r2wBO28ZBuk4f8lCF1vV5jLTgY6HkeyzRZCXFxZBuaywURdtagiq9K1d2VADKpPUrTn1vx9ZC4tBtclg6CtaG8WmfKe83z4WroWYEZCAyglxCwUZCV7vk9ErYz3q5ZBKtQRlYkPncXh7A6pxVkSgAYzUZAtRQ2UqAIEVdBUGT99Dyq9qvsytlSKF3SOZAfwZDZD"  # <-- Thay bằng token thật
COOKIE = "sb=6TD3ZxCQKJrdzNFqODrRbf0T; ps_l=1; ps_n=1; datr=P2H3Z7uwpyyzc9DKfWrqu4uW; c_user=61574284283448; locale=en_US; vpd=v1%3B844x390x3.0000001192092896; fbl_st=100632612%3BT%3A29071844; wl_cbv=v2%3Bclient_version%3A2785%3Btimestamp%3A1744310696; wd=1536x730; dpr=1.25; fr=12zyh1r40JBXBB9bd.AWdcxQcVHxWm8Bbjis_TJhvV2HekFF8yYG3I6eNUVvXps55TX2g.Bn-BMD..AAA.0.0.Bn-BMD.AWeKrEP61Enkh-aSlwmZxp5uklk; xs=32%3AGhXcAgwzsUSzCA%3A2%3A1744275604%3A-1%3A-1%3A%3AAcUf_v27kFJLy9u7yrwo9yAftBEc7h32jNfX8Enu1g; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1744311514257%2C%22v%22%3A1%7D; useragent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNS4wLjAuMCBTYWZhcmkvNTM3LjM2; _uafec=Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F135.0.0.0%20Safari%2F537.36; "  # <-- Thay bằng cookie thật

async def get_fb_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập UID Facebook. Ví dụ: /getfbimg 100072447776739")
        return

    uid = context.args[0]

    # === Ảnh đại diện ===
    avt_url = f"https://graph.facebook.com/{uid}/picture?height=720&width=720&access_token=6628568379%7Cc1e620fa708a1d5696fb991c1bde5662"

    # === Ảnh bìa ===
    cover_api = f"https://graph.facebook.com/{uid}?fields=cover&access_token={ACCESS_TOKEN}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': COOKIE
    }

    try:
        # Gửi ảnh đại diện
        await update.message.reply_photo(photo=avt_url, caption=f"🖼 Ảnh đại diện của UID {uid}")

        # Lấy và gửi ảnh bìa
        response = requests.get(cover_api, headers=headers)
        data = response.json()

        if 'cover' in data:
            cover_url = data['cover']['source']
            await update.message.reply_photo(photo=cover_url, caption=f"📘 Ảnh bìa của UID {uid}")
        elif 'error' in data:
            await update.message.reply_text(f"❌ Lỗi từ Facebook: {data['error']['message']}")
        else:
            await update.message.reply_text("⚠️ Không tìm thấy ảnh bìa.")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi xử lý yêu cầu: {e}")


#get info



# === Main ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    approved_users.update(load_approved_users())

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getfbimg", get_fb_images))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("check", check_command_handler))
    app.add_handler(CommandHandler("save", save_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("delete", delete_command_handler))  # Hiển thị menu xoá
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(remove_uid, pattern="^del_"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(?!del_).*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_uid))
    app.job_queue.run_repeating(periodic_check, interval=CHECK_INTERVAL, first=10)
    app.add_handler(CommandHandler("duyet", duyet))
    app.add_handler(CommandHandler("id", get_id))  # Đăng ký handler
    app.add_handler(CommandHandler("huy", huy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name_input))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # CHỈ CẦN 1 handler
    app.add_handler(CommandHandler("thongbao", thong_bao))
    app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_note_input))
    app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_name_input))



    print("🚀 Bot Telegram kiểm tra UID đang chạy!")
    await app.run_polling()

# Cập nhật lệnh cho bot
async def post_init(app):
    await app.bot.set_my_commands([
        BotCommand("start", " Bắt Đầu "),
        BotCommand("save", " Lưu UID "),
        BotCommand("delete", " Xoá UID "),
        BotCommand("list", " Danh sách UID "),
        BotCommand("check", " Check trạng thái UID"),
        BotCommand("getfbimg", " Lấy avatar và bìa Facebook"),
        BotCommand("help", " Hướng dẫn sử dụng ")
        
    ])
    print("✅ Đã cập nhật danh sách lệnh")

# Chạy chương trình
if __name__ == "__main__":
    approved_users = load_approved_users()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())



