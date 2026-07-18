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

# ========== ВОПРОСЫ АНГЛИЙСКИЙ ==========
QUESTIONS_EN = [
    ("I ____ to Paris every summer.", ["go", "goes", "going", "am go"], 0),
    ("She ____ beautiful.", ["am", "is", "are", "be"], 1),
    ("I work ____ a nurse.", ["like", "as", "for", "of"], 1),
    ("He dances very ____.", ["good", "well", "nice", "beautiful"], 1),
    ("Every evening I ____ Netflix.", ["look", "see", "watch", "view"], 2),
    ("Last night I ____ a great series.", ["see", "saw", "seen", "was see"], 1),
    ("He smiled ____ me and my heart stopped.", ["to", "at", "on", "for"], 1),
    ("If you want a better job, you ____ learn English.", ["should", "may", "can", "will"], 0),
    ("She applied ____ a position as a tour guide.", ["to", "on", "for", "with"], 2),
    ("Feminism means women and men have equal ____.", ["rights", "tasks", "jobs", "moneys"], 0),
    ("Many feminists fight ____ this idea.", ["against", "for", "with", "to"], 0),
    ("I've been watching videos, ____ I'm still nervous.", ["so", "because", "but", "and"], 2),
    ("He reminds me ____ that actor from Suits.", ["about", "of", "from", "with"], 1),
    ("She gave him a subtle smile, but he completely missed the ____.", ["clue", "cue", "hint", "sign"], 2),
    ("After a long flight, he tried to strike ____ a conversation.", ["up", "out", "off", "down"], 0),
    ("The series The Crown shows how the Queen navigated a male-____ political world.", ["dominant", "dominated", "dominating", "dominance"], 1),
    ("That show is so addictive — I ended up ____ the entire second season.", ["binge-watch", "to binge-watch", "binge-watching", "binge-watched"], 2),
    ("Despite her qualifications, she was overlooked for the promotion due to unconscious ____.", ["bias", "stereotype", "prejudice", "discrimination"], 0),
    ("The tango is often described as a vertical expression of ____ desire.", ["horizontal", "diagonal", "circular", "parallel"], 0),
    ("His flirtatious remarks created a ____ environment that made colleagues uncomfortable.", ["toxic", "hostile", "risky", "fragile"], 1),
]

# ========== УРОВНИ АНГЛИЙСКИЙ ==========
LEVELS_EN = {
    (0, 4): "Твой уровень А1\n\nО май гад, ты что, крейзи?\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (5, 7): "Твой уровень А2\n\nБьютифул! Твой уровень просто анбеливбл.\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (8, 10): "Твой уровень В1\n\nDamn! Полный фэшн!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (11, 13): "Твой уровень В1+\n\nЭто просто инкрэдбл. Все хотят быть тобой, а ты неповторим(-а).\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (14, 16): "Твой уровень В2\n\nСириосли? Кто ты, воин?\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (17, 18): "Твой уровень В2+\n\nАй миииииииин... Ты просто супер-стар!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
    (19, 20): "Твой уровень С1\n\nDamn, giiiirl / boooooy! Slay queen / king!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста.",
}

# ========== ВОПРОСЫ ИСПАНСКИЙ ==========
QUESTIONS_ES = [
    ("Hola, ¿cómo ____ llamas?", ["te", "se", "me"], 0),
    ("Yo ____ a España el próximo año.", ["voy", "vas", "van"], 0),
    ("¿Dónde ____ trabajar en el extranjero?", ["quieres", "quiero", "quiere"], 0),
    ("Necesito ____ un piso en Madrid.", ["buscar", "busco", "buscando"], 0),
    ("Mi novio ____ en Estados Unidos.", ["vive", "vivo", "viven"], 0),
    ("¿Tienes ____ experiencia en trabajos internacionales?", ["alguna", "algún", "algunos"], 0),
    ("Voy a viajar ____ México este verano.", ["a", "en", "de"], 0),
    ("No ____ inglés muy bien, pero estoy aprendiendo.", ["hablo", "habla", "hablan"], 0),
    ("Cuando vivía en Rusia, ____ español todos los días.", ["estudiaba", "estudié", "estudiaré"], 0),
    ("Si ____ dinero, me mudaría a España.", ["tengo", "tuviera", "tendré"], 1),
    ("Estoy buscando trabajo ____ pueda usar inglés.", ["donde", "cuando", "porque"], 0),
    ("¿Ya ____ los documentos para el visado?", ["preparaste", "preparas", "prepararás"], 0),
    ("Quiero conocer a alguien que ____ viajar conmigo.", ["quiere", "quiera", "quiso"], 1),
    ("Me gusta vivir en otro país porque ____ nuevas culturas.", ["conozco", "conocí", "conoceré"], 0),
    ("Si hubiera sabido que era tan difícil, no ____ cambiado de país.", ["había", "habría", "habré"], 1),
    ("Busco un trabajo que me ____ crecer profesionalmente.", ["permite", "permita", "permitió"], 1),
    ("Aunque ____ difícil al principio, ahora me siento cómodo aquí.", ["fue", "sea", "era"], 1),
    ("Llevo dos años ____ en el extranjero.", ["vivir", "viviendo", "vivido"], 1),
    ("Antes de mudarme, ya ____ trabajado con extranjeros.", ["había", "he", "estaba"], 0),
    ("No creo que ____ fácil adaptarse a otro país sin idioma.", ["es", "sea", "será"], 1),
    ("Me sorprendió que la gente ____ tan abierta conmigo.", ["es", "fuera", "será"], 1),
    ("En cuanto ____ el visado, me mudo inmediatamente.", ["tengo", "tenga", "tenía"], 1),
    ("Ojalá ____ sabido antes lo importante que es el idioma.", ["he", "hubiera", "tendré"], 1),
    ("A pesar de ____ muchos errores, sigo hablando sin miedo.", ["hacer", "haciendo", "hecho"], 0),
]

# ========== УРОВНИ ИСПАНСКИЙ ==========
def get_level_es(score):
    if score <= 10: return "Твой уровень А1\n\n¡ Vamooooooos!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    elif score <= 13: return "Твой уровень А2\n\n¡ Olé ! Excelente!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    elif score <= 16: return "Твой уровень В1\n\n¡Ay, Dios mío!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    elif score <= 18: return "Твой уровень В1+\n\nЭто просто increíble!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    elif score <= 20: return "Твой уровень В2\n\n¿ En serio? Кто ты, воин?\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    elif score <= 22: return "Твой уровень В2+\n\nO seaaaaaaaa ... Ты просто súper estrella!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."
    else: return "Твой уровень С1\n\nMadre mía ... ¡Eres un/a crack!\nМы в восторге от тебя и хотим быть частью твоего дальнейшего роста."

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

# ========== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В ЛОГИ ==========
def save_result(user_id, username, first_name, language, score, level_text, purpose):
    # Формируем читаемую строку для логов
    log_entry = (
        f"РЕЗУЛЬТАТ ТЕСТА | "
        f"User ID: {user_id} | "
        f"Username: {username or 'Нет'} | "
        f"Имя: {first_name or 'Нет'} | "
        f"Язык: {language} | "
        f"Баллы: {score} | "
        f"Уровень: {level_text.split(chr(10))[0] if level_text else 'Unknown'} | "
        f"Цель: {purpose}"
    )
    
    # Выводим в консоль — это и будет лог на Render
    print(log_entry)
    
    # Дополнительно выводим в консоль для красоты
    print("=" * 80)

# ========== ОБРАБОТЧИКИ КОМАНД ==========
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
        
        # =================================================
        # СОХРАНЯЕМ РЕЗУЛЬТАТ В ЛОГИ (вместо файла)
        # =================================================
        save_result(
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language="English" if lang == "en" else "Español",
            score=f"{score}/{total}",
            level_text=level_text,
            purpose=purpose
        )
        # =================================================
        
        await query.edit_message_text(
            f"🎉 Тест завершён!\n\n"
            f"📊 Результат: {score} из {total}\n\n"
            f"{level_text}\n\n"
            f"📝 Твоя цель: {purpose}\n\n"
            f"Забери свой подарок",
            reply_markup=get_gift_keyboard()
        )
        return

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
    
    # Запускаем polling (игнорируем старые обновления)
    bot_app.run_polling(drop_pending_updates=True)