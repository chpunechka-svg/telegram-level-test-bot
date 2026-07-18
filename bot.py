from flask import Flask
import threading
import os
import telegram
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import csv
from datetime import datetime

# ========== ТОКЕН И ССЫЛКИ ==========
TOKEN = "8578549035:AAEAtaT30SoLDcpuyKUzL9R4V4DiNWmvtFo"
BOOKING_URL = "https://planerka.app/alena-tomina-gpk3ee/30min"
DOCS_URL = "https://docs.google.com/document/d/1R0c106HJ9uwCfZtabpAzMN64ZpizxAf3YCiHRn-JvdM/edit?tab=t.0#heading=h.mpakg2mcgoy2"

# ========== FLASK ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!", 200

# ========== ТЕЛЕГРАМ БОТ ==========
bot = telegram.Bot(token=TOKEN)
user_data = {}

# ========== ВОПРОСЫ И УРОВНИ (ваши данные) ==========
# ... ВСТАВЬТЕ СЮДА ВСЕ ВАШИ ВОПРОСЫ И ФУНКЦИИ ...
# (они такие же, как в предыдущих версиях кода)

# ========== ОБРАБОТЧИКИ ==========
async def handle_start(update, context):
    user_id = update.effective_user.id
    user_data[user_id] = {"score": 0, "q_num": 0}
    await update.message.reply_text(
        "Бу! Испугался? Не бойся, я друг.\n\nПомогу тебе узнать твой уровень языка.\nLanguage Casa заботливо подготовила небольшой и эффективный тест.\n\nВыбери язык или запишись на урок",
        reply_markup=get_lang_keyboard()
    )

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    if user_id not in user_data:
        user_data[user_id] = {"score": 0, "q_num": 0}
    
    # --- ВЫБОР ЯЗЫКА ---
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_data[user_id]["lang"] = lang
        user_data[user_id]["score"] = 0
        user_data[user_id]["q_num"] = 0
        
        if lang == "en":
            total = 20
            q_text, options, _ = QUESTIONS_EN[0]
        else:
            total = 24
            q_text, options, _ = QUESTIONS_ES[0]
        
        await query.edit_message_text(
            f"🎯 Отлично! Выбран язык: {'🇺🇸 Английский' if lang == 'en' else '🇪🇸 Испанский'}\n\n"
            f"Тест состоит из {total} вопросов.\nБудь честен с собой — переводчиком не пользуйся!\n"
        )
        keyboard = [[telegram.InlineKeyboardButton(opt, callback_data=f"ans_{lang}_{0}_{i}")] for i, opt in enumerate(options)]
        await query.message.reply_text(
            f"Вопрос 1 из {total}:\n\n{q_text}",
            reply_markup=telegram.InlineKeyboardMarkup(keyboard)
        )
        return
    
    # --- ОТВЕТ НА ВОПРОС ---
    if data.startswith("ans_"):
        parts = data.split("_")
        lang = parts[1]
        q_num = int(parts[2])
        answer_idx = int(parts[3])
        
        if lang == "en":
            questions = QUESTIONS_EN
            total = 20
        else:
            questions = QUESTIONS_ES
            total = 24
        
        _, options, correct_idx = questions[q_num]
        
        if answer_idx == correct_idx:
            user_data[user_id]["score"] += 1
            await query.edit_message_text(f"✅ Верно!\n\nПравильный ответ: {options[correct_idx]}")
        else:
            await query.edit_message_text(f"❌ Неверно!\n\nПравильный ответ: {options[correct_idx]}")
        
        next_q = q_num + 1
        user_data[user_id]["q_num"] = next_q
        
        if next_q < total:
            q_text, options, _ = questions[next_q]
            keyboard = [[telegram.InlineKeyboardButton(opt, callback_data=f"ans_{lang}_{next_q}_{i}")] for i, opt in enumerate(options)]
            await query.message.reply_text(
                f"Вопрос {next_q + 1} из {total}:\n\n{q_text}",
                reply_markup=telegram.InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text(
                "📋 Последний вопрос:\n\nДля чего ты хочешь изучать язык?",
                reply_markup=get_purpose_keyboard()
            )
        return
    
    # --- ЦЕЛЬ ---
    if data.startswith("purpose_"):
        purpose_map = {
            "purpose_travel": "✈️ Путешествия",
            "purpose_work": "💼 Работа",
            "purpose_relocation": "🌍 Переезд",
            "purpose_love": "❤️ Найти любовь",
            "purpose_other": "🤔 Другое",
        }
        purpose = purpose_map.get(data, "🤔 Другое")
        lang = user_data[user_id].get("lang", "en")
        score = user_data[user_id]["score"]
        total = 20 if lang == "en" else 24
        
        if lang == "en":
            for (low, high), text in LEVELS_EN.items():
                if low <= score <= high:
                    level_text = text
                    break
        else:
            level_text = get_level_es(score)
        
        save_result(
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language="English" if lang == "en" else "Español",
            score=f"{score}/{total}",
            level_text=level_text,
            purpose=purpose
        )
        
        await query.edit_message_text(
            f"🎉 Тест завершён!\n\n"
            f"📊 Результат: {score} из {total}\n\n"
            f"{level_text}\n\n"
            f"📝 Твоя цель: {purpose}\n\n"
            f"Забери свой подарок",
            reply_markup=get_gift_keyboard()
        )
        return

# ========== КЛАВИАТУРЫ ==========
def get_lang_keyboard():
    return telegram.InlineKeyboardMarkup([
        [telegram.InlineKeyboardButton("🇺🇸 Английский", callback_data="lang_en")],
        [telegram.InlineKeyboardButton("🇪🇸 Испанский", callback_data="lang_es")],
        [telegram.InlineKeyboardButton("📄 Документы", url=DOCS_URL)],
        [telegram.InlineKeyboardButton("✨ Записаться на пробный урок ✨", url=BOOKING_URL)],
    ])

def get_purpose_keyboard():
    return telegram.InlineKeyboardMarkup([
        [telegram.InlineKeyboardButton("✈️ Путешествия", callback_data="purpose_travel")],
        [telegram.InlineKeyboardButton("💼 Работа", callback_data="purpose_work")],
        [telegram.InlineKeyboardButton("🌍 Переезд", callback_data="purpose_relocation")],
        [telegram.InlineKeyboardButton("❤️ Найти любовь", callback_data="purpose_love")],
        [telegram.InlineKeyboardButton("🤔 Другое", callback_data="purpose_other")],
    ])

def get_gift_keyboard():
    return telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("🎁 Забрать подарок 🎁", url=BOOKING_URL)]])

# ========== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ ==========
def save_result(user_id, username, first_name, language, score, level_text, purpose):
    file_path = "test_results.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Дата", "User ID", "Username", "Имя", "Язык", "Баллы", "Уровень", "Цель"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            username,
            first_name,
            language,
            score,
            level_text.split("\n")[0] if level_text else "Unknown",
            purpose
        ])

# ========== ЗАПУСК ==========
def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Запускаем Flask в фоновом потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота в главном потоке
    print("🤖 Бот запускается в главном потоке...")
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", handle_start))
    bot_app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Запускаем polling (теперь в главном потоке)
    bot_app.run_polling()