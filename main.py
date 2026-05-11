# ============================================================
#  KURS BOT — To'liq kod (bitta fayl)
#  Texnologiyalar: Python 3.10+, aiogram 3.x, aiosqlite
#  O'rnatish: pip install aiogram aiosqlite
#  Yangi funksiyalar:
#    ✅ Promo-kod tizimi
#    ✅ 24 soat to'lov eslatmasi
#    ✅ Ko'p tilli interfeys (UZ / RU / EN)
#    ✅ Bundle chegirma (ikkala kurs birga)
#    ✅ Referral (tavsiya) tizimi
# ============================================================

import asyncio
import logging
import re
import secrets
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite

logging.basicConfig(level=logging.INFO)

# ============================================================
# ⚙️  SOZLAMALAR  —  BU YERNI TO'LDIRING
# ============================================================

BOT_TOKEN    = "8662389331:AAFxUrqELWt8-Nda3dXIFmSdnAM1wXjHIWg"  # @BotFather dan
CHANNEL_ID   = "@ecomind_economy"   # ✅ TO'G'RI FORMAT: @username yoki -100xxxxxxxxxx
ADMIN_IDS    = [7138813964]          # Sizning Telegram ID ingiz
BOT_USERNAME = "@Eduai_uzbot"   # ✅ O'ZGARTIRING: @siz botingizning username

# ✅ KARTA MA'LUMOTLARI — O'Z KARTANGIZNI KIRITING
CARD_NUMBER  = "9860 3501 4757 0625"
CARD_OWNER   = "JAVOHIR G'AYRATALIYEV"

COURSE_NAMES = {
    "logistics":   "📦 Logistika kursi",
    "china_order": "🇨🇳 Xitoydan zakaz kursi",
}

BUNDLE_DISCOUNT = 25   # % (bundle chegirma foizi)
REFERRAL_DISCOUNT = 10  # % (referral chegirma foizi)

DB_PATH = "bot_database.db"

# ============================================================
# 🌐  KO'P TILLI MATNLAR
# ============================================================

TEXTS = {
    "uz": {
        "welcome": "👋 Assalomu alaykum, <b>{name}</b>!\n\nTilni tanlang / Выберите язык / Choose language:",
        "choose_lang": "🌐 Tilni tanlang:",
        "lang_set": "✅ Til o'rnatildi: O'zbekcha",
        "subscribe_required": "⚠️ <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>\n\nObuna bo'lgach <b>✅ Tekshirish</b> tugmasini bosing.",
        "subscribed": "✅ Obuna tasdiqlandi! Kursni tanlang:",
        "not_subscribed": "❌ Hali obuna bo'lmadingiz!",
        "select_course": "Kursni tanlang:",
        "main_menu": "Asosiy menyu:",
        "profile": "👤 <b>Profilingiz</b>\n\n📛 Ism: <b>{name}</b>\n🆔 ID: <code>{uid}</code>\n\n📦 Logistika kursi: {log}\n🇨🇳 Xitoy kursi: {china}\n\n🔗 Sizning referral havolangiz:\n<code>https://t.me/{bot}?start=ref_{uid}</code>\n\n👥 Taklif qilganlaringiz: <b>{refs}</b> kishi\n💰 Referral bonusingiz: <b>{bonus}</b>",
        "bought": "✅ Sotib olingan",
        "not_bought": "❌ Sotib olinmagan",
        "help": "🆘 <b>Yordam</b>\n\nSavollaringiz bo'lsa admin bilan bog'laning:\n👤 @admin_username",
        "course_lessons": "✅ <b>{name}</b>\n\nDarsni tanlang:",
        "course_soon": "✅ <b>{name}</b>\n\n⏳ Darslar tez orada qo'shiladi!",
        "course_buy": "<b>{name}</b>\n\n📝 {desc}\n\n💰 Narxi: <b>{price} so'm</b>\n\n⬇️ Kursni sotib olish uchun tugmani bosing:",
        "payment_info": "💳 <b>To'lov ma'lumotlari</b>\n\n📚 Kurs: <b>{name}</b>\n💰 Narx: <b>{price} so'm</b>\n\n━━━━━━━━━━━━━━━━━━━━\n💳 Karta raqami:\n<code>{card}</code>\n\n👤 Karta egasi: <b>{owner}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n✅ To'lov qilgach chekni (screenshot) yuboring.",
        "send_check": "📸 Iltimos, to'lov chekini (rasmini) yuboring:",
        "check_received": "✅ Chekingiz qabul qilindi!\n\nAdmin tez orada tekshirib, kursni ochib beradi.",
        "course_opened": "🎉 <b>Tabriklaymiz!</b>\n\n<b>{name}</b> kursi sizga ochildi!\nKurs tugmasini bosib darslarni ko'ring.",
        "payment_rejected": "❌ To'lovingiz tasdiqlanmadi.\nTo'g'ri chek yuboring yoki admin bilan bog'laning.",
        "no_access": "❌ Bu kursga kirishingiz yo'q!",
        "lesson_not_found": "❌ Dars topilmadi.",
        "select_course_first": "❌ Avval kursni tanlang.",
        "promo_enter": "🎟 Promo-kod kiriting (yoki /skip yuboring):",
        "promo_invalid": "❌ Promo-kod noto'g'ri yoki muddati o'tgan.",
        "promo_applied": "✅ Promo-kod qo'llandi! Chegirma: <b>{discount}%</b>",
        "bundle_desc": "📦🇨🇳 <b>Ikkala kurs birgalikda</b>\n\nLogistika kursi + Xitoydan zakaz kursi\n\n💰 Alohida narxi: <b>{full} so'm</b>\n🔥 Bundle narxi ({discount}% chegirma): <b>{price} so'm</b>\n\n⬇️ Sotib olish uchun tugmani bosing:",
        "referral_welcome": "🎉 Siz <b>{name}</b> tavsiyasi orqali keldingiz!\nHar qanday kurs sotib olishda <b>{discount}% chegirma</b> olasiz!",
        "reminder_24h": "⏰ <b>Eslatma!</b>\n\nSiz <b>{name}</b> kursiga qiziqgan edingiz, lekin to'lov amalga oshirilmadi.\n\n🔥 Kursni hozir sotib oling va bilimingizni oshiring!\n\n💡 Savolingiz bo'lsa: @admin_username",
        "btn_buy": "💳 To'lov qilish",
        "btn_back": "🔙 Orqaga",
        "btn_check": "📸 Chekni yuborish",
        "btn_bundle": "🎁 Ikkala kursni birgalikda sotib ol ({discount}% chegirma)",
        "btn_referral": "🔗 Do'stingizni taklif qiling",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "btn_main_menu": "🔙 Asosiy menyu",
        "btn_logistics": "📦 Logistika kursi",
        "btn_china": "🇨🇳 Xitoydan zakaz kursi",
        "btn_profile": "👤 Profil / Hisobim",
        "btn_help": "🆘 Yordam",
        "btn_admin": "⚙️ Admin panel",
        "btn_subscribe": "📢 Kanalga obuna bo'lish",
        "btn_check_sub": "✅ Tekshirish",
    },
    "ru": {
        "welcome": "👋 Добро пожаловать, <b>{name}</b>!\n\nВыберите язык / Tilni tanlang / Choose language:",
        "choose_lang": "🌐 Выберите язык:",
        "lang_set": "✅ Язык установлен: Русский",
        "subscribe_required": "⚠️ <b>Для использования бота подпишитесь на наш канал!</b>\n\nПосле подписки нажмите <b>✅ Проверить</b>.",
        "subscribed": "✅ Подписка подтверждена! Выберите курс:",
        "not_subscribed": "❌ Вы ещё не подписались!",
        "select_course": "Выберите курс:",
        "main_menu": "Главное меню:",
        "profile": "👤 <b>Ваш профиль</b>\n\n📛 Имя: <b>{name}</b>\n🆔 ID: <code>{uid}</code>\n\n📦 Логистика: {log}\n🇨🇳 Заказ из Китая: {china}\n\n🔗 Ваша реферальная ссылка:\n<code>https://t.me/{bot}?start=ref_{uid}</code>\n\n👥 Приглашённых: <b>{refs}</b> чел.\n💰 Реферальный бонус: <b>{bonus}</b>",
        "bought": "✅ Куплено",
        "not_bought": "❌ Не куплено",
        "help": "🆘 <b>Помощь</b>\n\nЕсли есть вопросы, обратитесь к администратору:\n👤 @admin_username",
        "course_lessons": "✅ <b>{name}</b>\n\nВыберите урок:",
        "course_soon": "✅ <b>{name}</b>\n\n⏳ Уроки появятся в ближайшее время!",
        "course_buy": "<b>{name}</b>\n\n📝 {desc}\n\n💰 Цена: <b>{price} сум</b>\n\n⬇️ Нажмите кнопку для покупки:",
        "payment_info": "💳 <b>Данные для оплаты</b>\n\n📚 Курс: <b>{name}</b>\n💰 Цена: <b>{price} сум</b>\n\n━━━━━━━━━━━━━━━━━━━━\n💳 Номер карты:\n<code>{card}</code>\n\n👤 Владелец карты: <b>{owner}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n✅ После оплаты отправьте чек (скриншот).",
        "send_check": "📸 Пожалуйста, отправьте чек об оплате:",
        "check_received": "✅ Ваш чек принят!\n\nАдминистратор проверит и откроет курс.",
        "course_opened": "🎉 <b>Поздравляем!</b>\n\nКурс <b>{name}</b> открыт для вас!\nНажмите кнопку курса, чтобы смотреть уроки.",
        "payment_rejected": "❌ Ваша оплата не подтверждена.\nОтправьте правильный чек или свяжитесь с администратором.",
        "no_access": "❌ У вас нет доступа к этому курсу!",
        "lesson_not_found": "❌ Урок не найден.",
        "select_course_first": "❌ Сначала выберите курс.",
        "promo_enter": "🎟 Введите промо-код (или отправьте /skip):",
        "promo_invalid": "❌ Промо-код неверный или истёк.",
        "promo_applied": "✅ Промо-код применён! Скидка: <b>{discount}%</b>",
        "bundle_desc": "📦🇨🇳 <b>Оба курса вместе</b>\n\nЛогистика + Заказ из Китая\n\n💰 Обычная цена: <b>{full} сум</b>\n🔥 Цена пакета ({discount}% скидка): <b>{price} сум</b>\n\n⬇️ Нажмите для покупки:",
        "referral_welcome": "🎉 Вы пришли по приглашению <b>{name}</b>!\nПри покупке любого курса получите скидку <b>{discount}%</b>!",
        "reminder_24h": "⏰ <b>Напоминание!</b>\n\nВы интересовались курсом <b>{name}</b>, но оплата не завершена.\n\n🔥 Купите курс сейчас и прокачайте свои знания!\n\n💡 Вопросы: @admin_username",
        "btn_buy": "💳 Оплатить",
        "btn_back": "🔙 Назад",
        "btn_check": "📸 Отправить чек",
        "btn_bundle": "🎁 Купить оба курса ({discount}% скидка)",
        "btn_referral": "🔗 Пригласить друга",
        "btn_change_lang": "🌐 Изменить язык",
        "btn_main_menu": "🔙 Главное меню",
        "btn_logistics": "📦 Логистика",
        "btn_china": "🇨🇳 Заказ из Китая",
        "btn_profile": "👤 Профиль",
        "btn_help": "🆘 Помощь",
        "btn_admin": "⚙️ Админ панель",
        "btn_subscribe": "📢 Подписаться на канал",
        "btn_check_sub": "✅ Проверить",
    },
    "en": {
        "welcome": "👋 Welcome, <b>{name}</b>!\n\nChoose language / Tilni tanlang / Выберите язык:",
        "choose_lang": "🌐 Choose your language:",
        "lang_set": "✅ Language set: English",
        "subscribe_required": "⚠️ <b>Please subscribe to our channel to use the bot!</b>\n\nAfter subscribing, press <b>✅ Check</b>.",
        "subscribed": "✅ Subscription confirmed! Choose a course:",
        "not_subscribed": "❌ You are not subscribed yet!",
        "select_course": "Choose a course:",
        "main_menu": "Main menu:",
        "profile": "👤 <b>Your Profile</b>\n\n📛 Name: <b>{name}</b>\n🆔 ID: <code>{uid}</code>\n\n📦 Logistics: {log}\n🇨🇳 China Order: {china}\n\n🔗 Your referral link:\n<code>https://t.me/{bot}?start=ref_{uid}</code>\n\n👥 Invited: <b>{refs}</b> people\n💰 Referral bonus: <b>{bonus}</b>",
        "bought": "✅ Purchased",
        "not_bought": "❌ Not purchased",
        "help": "🆘 <b>Help</b>\n\nContact admin for questions:\n👤 @admin_username",
        "course_lessons": "✅ <b>{name}</b>\n\nChoose a lesson:",
        "course_soon": "✅ <b>{name}</b>\n\n⏳ Lessons coming soon!",
        "course_buy": "<b>{name}</b>\n\n📝 {desc}\n\n💰 Price: <b>{price} UZS</b>\n\n⬇️ Press the button to purchase:",
        "payment_info": "💳 <b>Payment Details</b>\n\n📚 Course: <b>{name}</b>\n💰 Price: <b>{price} UZS</b>\n\n━━━━━━━━━━━━━━━━━━━━\n💳 Card number:\n<code>{card}</code>\n\n👤 Card owner: <b>{owner}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n✅ Send your payment receipt (screenshot) after paying.",
        "send_check": "📸 Please send your payment receipt:",
        "check_received": "✅ Your receipt has been received!\n\nThe admin will verify and open the course shortly.",
        "course_opened": "🎉 <b>Congratulations!</b>\n\nCourse <b>{name}</b> has been opened for you!\nPress the course button to view lessons.",
        "payment_rejected": "❌ Your payment was not confirmed.\nSend the correct receipt or contact admin.",
        "no_access": "❌ You don't have access to this course!",
        "lesson_not_found": "❌ Lesson not found.",
        "select_course_first": "❌ Please select a course first.",
        "promo_enter": "🎟 Enter promo code (or send /skip):",
        "promo_invalid": "❌ Invalid or expired promo code.",
        "promo_applied": "✅ Promo code applied! Discount: <b>{discount}%</b>",
        "bundle_desc": "📦🇨🇳 <b>Both Courses Together</b>\n\nLogistics + China Order\n\n💰 Regular price: <b>{full} UZS</b>\n🔥 Bundle price ({discount}% off): <b>{price} UZS</b>\n\n⬇️ Press to purchase:",
        "referral_welcome": "🎉 You came via <b>{name}</b>'s invitation!\nGet <b>{discount}% discount</b> on any course purchase!",
        "reminder_24h": "⏰ <b>Reminder!</b>\n\nYou showed interest in <b>{name}</b> but didn't complete payment.\n\n🔥 Buy now and boost your skills!\n\n💡 Questions: @admin_username",
        "btn_buy": "💳 Pay Now",
        "btn_back": "🔙 Back",
        "btn_check": "📸 Send Receipt",
        "btn_bundle": "🎁 Buy Both Courses ({discount}% off)",
        "btn_referral": "🔗 Invite a Friend",
        "btn_change_lang": "🌐 Change Language",
        "btn_main_menu": "🔙 Main Menu",
        "btn_logistics": "📦 Logistics Course",
        "btn_china": "🇨🇳 China Order Course",
        "btn_profile": "👤 Profile",
        "btn_help": "🆘 Help",
        "btn_admin": "⚙️ Admin Panel",
        "btn_subscribe": "📢 Subscribe to Channel",
        "btn_check_sub": "✅ Check",
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    """Tarjima yordamchi funksiyasi"""
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

# ============================================================
# 🗄️  MA'LUMOTLAR BAZASI
# ============================================================

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                lang        TEXT DEFAULT 'uz',
                referred_by INTEGER DEFAULT NULL,
                referral_bonus INTEGER DEFAULT 0,
                joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS courses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                course_key  TEXT UNIQUE,
                name        TEXT,
                description TEXT,
                price       INTEGER
            );
            CREATE TABLE IF NOT EXISTS lessons (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                course_key    TEXT,
                lesson_number INTEGER,
                title         TEXT,
                content       TEXT,
                file_id       TEXT,
                file_type     TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS purchases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                course_key  TEXT,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_key)
            );
            CREATE TABLE IF NOT EXISTS payment_requests (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                course_key      TEXT,
                check_file_id   TEXT,
                check_file_type TEXT,
                status          TEXT DEFAULT 'pending',
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS promo_codes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT UNIQUE,
                discount    INTEGER,
                max_uses    INTEGER DEFAULT 100,
                used_count  INTEGER DEFAULT 0,
                is_active   INTEGER DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS promo_usage (
                user_id   INTEGER,
                code      TEXT,
                used_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, code)
            );
            CREATE TABLE IF NOT EXISTS payment_views (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                course_key  TEXT,
                viewed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminded    INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER,
                referred_id INTEGER PRIMARY KEY,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("""
            INSERT OR IGNORE INTO courses (course_key, name, description, price) VALUES
            ('logistics',   '📦 Logistika kursi',
             'Logistika sohasida professional bo''lishni o''rganing. Xalqaro yuk tashish, bojxona, hujjatlar va ko''p narsalar.',
             299000),
            ('china_order', '🇨🇳 Xitoydan zakaz kursi',
             'Xitoydan tovar buyurtma qilish sirlarini bilib oling. 1688, Taobao, Alibaba platformalari bilan ishlash.',
             199000)
        """)
        await db.commit()
    print("✅ Ma'lumotlar bazasi tayyor")

# --- DB yordamchi funksiyalar ---

async def db_add_user(user_id, username, full_name, lang="uz", referred_by=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, lang, referred_by) VALUES (?,?,?,?,?)",
            (user_id, username, full_name, lang, referred_by))
        await db.commit()

async def db_get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as c:
            return await c.fetchone()

async def db_set_lang(user_id, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
        await db.commit()

async def db_get_lang(user_id) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)) as c:
            row = await c.fetchone()
            return row[0] if row else "uz"

async def db_get_course(course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM courses WHERE course_key=?", (course_key,)) as c:
            return await c.fetchone()

async def db_has_purchased(user_id, course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM purchases WHERE user_id=? AND course_key=?", (user_id, course_key)) as c:
            return await c.fetchone() is not None

async def db_grant_access(user_id, course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO purchases (user_id, course_key) VALUES (?,?)", (user_id, course_key))
        await db.commit()

async def db_get_lessons(course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM lessons WHERE course_key=? ORDER BY lesson_number ASC", (course_key,)) as c:
            return await c.fetchall()

async def db_get_lesson(course_key, lesson_number):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM lessons WHERE course_key=? AND lesson_number=?", (course_key, lesson_number)) as c:
            return await c.fetchone()

async def db_next_lesson_number(course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT MAX(lesson_number) FROM lessons WHERE course_key=?", (course_key,)) as c:
            row = await c.fetchone()
            return (row[0] or 0) + 1

async def db_add_lesson(course_key, lesson_number, title, content, file_id, file_type):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO lessons (course_key,lesson_number,title,content,file_id,file_type) VALUES (?,?,?,?,?,?)",
            (course_key, lesson_number, title, content, file_id, file_type))
        await db.commit()

async def db_delete_lesson(course_key, lesson_number):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM lessons WHERE course_key=? AND lesson_number=?", (course_key, lesson_number))
        await db.commit()

async def db_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            return (await c.fetchone())[0]

async def db_purchases_count(course_key):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM purchases WHERE course_key=?", (course_key,)) as c:
            return (await c.fetchone())[0]

async def db_total_revenue():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT SUM(c.price) FROM purchases p JOIN courses c ON p.course_key=c.course_key") as cur:
            row = await cur.fetchone()
            return row[0] or 0

async def db_create_payment(user_id, course_key, file_id, file_type):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO payment_requests (user_id,course_key,check_file_id,check_file_type) VALUES (?,?,?,?)",
            (user_id, course_key, file_id, file_type))
        await db.commit()
        return cursor.lastrowid

async def db_pending_payments():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT pr.id, pr.user_id, pr.course_key, pr.check_file_id, pr.check_file_type,
                   u.full_name, u.username, c.name
            FROM payment_requests pr
            JOIN users u ON pr.user_id=u.user_id
            JOIN courses c ON pr.course_key=c.course_key
            WHERE pr.status='pending'
            ORDER BY pr.created_at DESC
        """) as cur:
            return await cur.fetchall()

async def db_get_payment(payment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT pr.id, pr.user_id, pr.course_key, pr.check_file_id, pr.check_file_type,
                   u.full_name, u.username, c.name
            FROM payment_requests pr
            JOIN users u ON pr.user_id=u.user_id
            JOIN courses c ON pr.course_key=c.course_key
            WHERE pr.id=?
        """, (payment_id,)) as cur:
            return await cur.fetchone()

async def db_approve_payment(request_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, course_key FROM payment_requests WHERE id=?", (request_id,)) as c:
            row = await c.fetchone()
        if row:
            await db.execute(
                "UPDATE payment_requests SET status='approved' WHERE id=?", (request_id,))
            await db.execute(
                "INSERT OR IGNORE INTO purchases (user_id,course_key) VALUES (?,?)", (row[0], row[1]))
            await db.commit()
            return row[0], row[1]
        return None, None

async def db_reject_payment(request_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM payment_requests WHERE id=?", (request_id,)) as c:
            row = await c.fetchone()
        await db.execute(
            "UPDATE payment_requests SET status='rejected' WHERE id=?", (request_id,))
        await db.commit()
        return row[0] if row else None

# ============================================================
# 🎟  PROMO-KOD FUNKSIYALARI
# ============================================================

async def db_create_promo(code: str, discount: int, max_uses: int = 100):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO promo_codes (code, discount, max_uses) VALUES (?,?,?)",
            (code.upper(), discount, max_uses))
        await db.commit()

async def db_validate_promo(code: str, user_id: int):
    """Promo-kodni tekshiradi. (discount, xato_xabar) qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT discount, max_uses, used_count, is_active FROM promo_codes WHERE code=?",
            (code.upper(),)) as c:
            row = await c.fetchone()
        if not row:
            return None, "not_found"
        discount, max_uses, used_count, is_active = row
        if not is_active or used_count >= max_uses:
            return None, "expired"
        # Foydalanuvchi oldin ishlatganmi?
        async with db.execute(
            "SELECT 1 FROM promo_usage WHERE user_id=? AND code=?", (user_id, code.upper())) as c:
            if await c.fetchone():
                return None, "already_used"
        return discount, None

async def db_use_promo(code: str, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO promo_usage (user_id, code) VALUES (?,?)", (user_id, code.upper()))
        await db.execute(
            "UPDATE promo_codes SET used_count = used_count + 1 WHERE code=?", (code.upper(),))
        await db.commit()

# ============================================================
# 🔗  REFERRAL FUNKSIYALARI
# ============================================================

async def db_add_referral(referrer_id: int, referred_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?,?)",
            (referrer_id, referred_id))
        await db.commit()

async def db_get_referral_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id=?", (user_id,)) as c:
            return (await c.fetchone())[0]

async def db_get_referrer(user_id: int):
    """Foydalanuvchini kim taklif qilganini topadi"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT referrer_id FROM referrals WHERE referred_id=?", (user_id,)) as c:
            row = await c.fetchone()
            return row[0] if row else None

# ============================================================
# ⏰  TO'LOV ESLATMASI FUNKSIYALARI
# ============================================================

async def db_log_payment_view(user_id: int, course_key: str):
    """Foydalanuvchi to'lov sahifasini ko'rganligini saqlaydi"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payment_views (user_id, course_key) VALUES (?,?)",
            (user_id, course_key))
        await db.commit()

async def db_get_unreminded_views():
    """24 soat o'tgan, hali eslatilmagan, to'lov qilmagan foydalanuvchilar"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT pv.user_id, pv.course_key, pv.id
            FROM payment_views pv
            WHERE pv.reminded = 0
              AND datetime(pv.viewed_at, '+24 hours') <= datetime('now')
              AND NOT EXISTS (
                  SELECT 1 FROM purchases p
                  WHERE p.user_id = pv.user_id AND p.course_key = pv.course_key
              )
              AND NOT EXISTS (
                  SELECT 1 FROM payment_requests pr
                  WHERE pr.user_id = pv.user_id AND pr.course_key = pv.course_key
                    AND pr.status IN ('pending', 'approved')
              )
        """) as c:
            return await c.fetchall()

async def db_mark_reminded(view_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE payment_views SET reminded=1 WHERE id=?", (view_id,))
        await db.commit()

# ============================================================
# 🎹  KLAVIATURALAR
# ============================================================

def kb_main(admin=False, lang="uz"):
    rows = [
        [KeyboardButton(text=t(lang, "btn_logistics")),
         KeyboardButton(text=t(lang, "btn_china"))],
        [KeyboardButton(text=t(lang, "btn_profile")),
         KeyboardButton(text=t(lang, "btn_help"))],
        [KeyboardButton(text=t(lang, "btn_change_lang"))],
    ]
    if admin:
        rows.append([KeyboardButton(text=t(lang, "btn_admin"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def kb_lang_select():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский",    callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English",    callback_data="lang_en")],
    ])

def kb_subscribe(link, lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_subscribe"), url=link)],
        [InlineKeyboardButton(text=t(lang, "btn_check_sub"), callback_data="check_sub")],
    ])

def kb_buy(course_key, lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_buy"), callback_data=f"buy_{course_key}")],
        [InlineKeyboardButton(text=t(lang, "btn_bundle", discount=BUNDLE_DISCOUNT), callback_data="buy_bundle")],
    ])

def kb_pay_confirm(course_key, lang="uz"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_check"), callback_data=f"send_check_{course_key}")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=f"course_{course_key}")],
    ])

def kb_admin_approve(request_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{request_id}"),
        InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"reject_{request_id}"),
    ]])

def kb_admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika",             callback_data="adm_stats")],
        [InlineKeyboardButton(text="📦 Logistika darslari",     callback_data="adm_lessons_logistics"),
         InlineKeyboardButton(text="🇨🇳 Xitoy darslari",       callback_data="adm_lessons_china_order")],
        [InlineKeyboardButton(text="➕ Dars qo'shish",          callback_data="adm_add_lesson")],
        [InlineKeyboardButton(text="💸 Kutayotgan to'lovlar",   callback_data="adm_pending")],
        [InlineKeyboardButton(text="🔓 Kirish berish",          callback_data="adm_grant")],
        [InlineKeyboardButton(text="🎟 Promo-kod yaratish",     callback_data="adm_promo")],
    ])

def kb_admin_lessons(lessons, course_key):
    rows = []
    for les in lessons:
        rows.append([
            InlineKeyboardButton(
                text=f"📖 {les[2]}-dars: {les[3]}",
                callback_data=f"adm_view_{course_key}_{les[2]}"),
            InlineKeyboardButton(
                text="🗑", callback_data=f"adm_del_{course_key}_{les[2]}"),
        ])
    rows.append([InlineKeyboardButton(text="➕ Yangi dars", callback_data=f"addlesson_{course_key}")])
    rows.append([InlineKeyboardButton(text="🔙 Admin panel", callback_data="back_adm")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb_select_course(action):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Logistika kursi",       callback_data=f"{action}_logistics")],
        [InlineKeyboardButton(text="🇨🇳 Xitoydan zakaz kursi", callback_data=f"{action}_china_order")],
        [InlineKeyboardButton(text="🔙 Orqaga",                callback_data="back_adm")],
    ])

def kb_back_adm():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Admin panel", callback_data="back_adm")]
    ])

def kb_lessons(lessons, course_key, lang="uz"):
    rows = []
    for les in lessons:
        rows.append([KeyboardButton(text=f"📖 {les[2]}-dars: {les[3]}")])
    rows.append([KeyboardButton(text=t(lang, "btn_main_menu"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

# ============================================================
# 🔧  YORDAMCHI FUNKSIYALAR
# ============================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def check_sub(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception as e:
        logging.warning(f"check_sub xatolik: {e}")
        return False

async def channel_link(bot: Bot) -> str:
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        if chat.username:
            return f"https://t.me/{chat.username}"
        if chat.invite_link:
            return chat.invite_link
    except Exception as e:
        logging.warning(f"channel_link xatolik: {e}")
    if CHANNEL_ID.startswith("@"):
        return f"https://t.me/{CHANNEL_ID[1:]}"
    return "https://t.me/"

def apply_discount(price: int, discount_percent: int) -> int:
    return int(price * (100 - discount_percent) / 100)

def fmt_price(price: int) -> str:
    return f"{price:,}".replace(",", " ")

# ============================================================
# 📋  FSM HOLATLARI
# ============================================================

class PaySt(StatesGroup):
    promo_code    = State()
    waiting_check = State()

class AddLessonSt(StatesGroup):
    course  = State()
    number  = State()
    title   = State()
    content = State()
    file    = State()

class GrantSt(StatesGroup):
    user_id = State()
    course  = State()

class PromoSt(StatesGroup):
    code      = State()
    discount  = State()
    max_uses  = State()

# ============================================================
# 🚀  HANDLERLAR
# ============================================================

router = Router()

# ---------- /start ----------

@router.message(CommandStart())
async def cmd_start(msg: Message, bot: Bot, state: FSMContext):
    await state.clear()
    u = msg.from_user
    args = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""

    # Referral tekshiruvi
    referred_by = None
    referral_discount = 0
    if args.startswith("ref_"):
        try:
            referrer_id = int(args[4:])
            if referrer_id != u.id:
                referred_by = referrer_id
        except ValueError:
            pass

    await db_add_user(u.id, u.username or "", u.full_name or "", referred_by=referred_by)

    if referred_by:
        await db_add_referral(referred_by, u.id)
        referrer = await db_get_user(referred_by)
        referrer_name = referrer[2] if referrer else "Do'stingiz"
        # Referral chegirmasini FSM ga saqlaymiz
        await state.update_data(referral_discount=REFERRAL_DISCOUNT)

    lang = await db_get_lang(u.id)

    if is_admin(u.id):
        await msg.answer(
            f"👋 Xush kelibsiz, Admin <b>{u.first_name}</b>!",
            reply_markup=kb_main(admin=True, lang=lang), parse_mode="HTML")
        return

    # Til tanlash (yangi foydalanuvchi uchun)
    user_data = await db_get_user(u.id)
    if not user_data or user_data[3] == "uz":
        # Yangi foydalanuvchi bo'lsa til tanlashni taklif qil
        await msg.answer(
            t("uz", "welcome", name=u.first_name),
            reply_markup=kb_lang_select(), parse_mode="HTML")

        if referred_by:
            referrer = await db_get_user(referred_by)
            referrer_name = referrer[2] if referrer else "Do'stingiz"
            await msg.answer(
                t(lang, "referral_welcome", name=referrer_name, discount=REFERRAL_DISCOUNT),
                parse_mode="HTML")
        return

    subbed = await check_sub(bot, u.id)
    if not subbed:
        link = await channel_link(bot)
        await msg.answer(
            t(lang, "subscribe_required"),
            reply_markup=kb_subscribe(link, lang), parse_mode="HTML")
    else:
        await msg.answer(
            f"👋 {u.first_name}!\n\n" + t(lang, "select_course"),
            reply_markup=kb_main(admin=False, lang=lang), parse_mode="HTML")

# ---------- Til tanlash ----------

@router.callback_query(F.data.startswith("lang_"))
async def cb_set_lang(cb: CallbackQuery, bot: Bot):
    lang = cb.data.replace("lang_", "")
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    await db_set_lang(cb.from_user.id, lang)
    await cb.message.delete()
    await bot.send_message(
        cb.from_user.id,
        t(lang, "lang_set"),
        parse_mode="HTML")

    subbed = await check_sub(bot, cb.from_user.id)
    if not subbed:
        link = await channel_link(bot)
        await bot.send_message(
            cb.from_user.id,
            t(lang, "subscribe_required"),
            reply_markup=kb_subscribe(link, lang), parse_mode="HTML")
    else:
        await bot.send_message(
            cb.from_user.id,
            t(lang, "select_course"),
            reply_markup=kb_main(admin=is_admin(cb.from_user.id), lang=lang),
            parse_mode="HTML")
    await cb.answer()

# ---------- Tilni o'zgartirish (tugmadan) ----------

@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Изменить язык", "🌐 Change Language"]))
async def change_lang(msg: Message):
    await msg.answer(t("uz", "choose_lang"), reply_markup=kb_lang_select())

# ---------- Obuna tekshirish ----------

@router.callback_query(F.data == "check_sub")
async def cb_check_sub(cb: CallbackQuery, bot: Bot):
    lang = await db_get_lang(cb.from_user.id)
    if await check_sub(bot, cb.from_user.id):
        try:
            await cb.message.delete()
        except Exception:
            pass
        await bot.send_message(
            cb.from_user.id,
            t(lang, "subscribed"),
            reply_markup=kb_main(admin=is_admin(cb.from_user.id), lang=lang))
    else:
        await cb.answer(t(lang, "not_subscribed"), show_alert=True)
    await cb.answer()

# ---------- Asosiy menyu tugmalari ----------

BACK_BTN_TEXTS = [
    "🔙 Asosiy menyu", "🔙 Главное меню", "🔙 Main Menu",
    "🔙 Asosiy Menu", "🔙 Bosh menyu"
]

@router.message(F.text.in_(BACK_BTN_TEXTS))
async def back_main(msg: Message, state: FSMContext):
    await state.clear()
    lang = await db_get_lang(msg.from_user.id)
    await msg.answer(t(lang, "main_menu"), reply_markup=kb_main(admin=is_admin(msg.from_user.id), lang=lang))

@router.message(F.text.in_(["👤 Profil / Hisobim", "👤 Профиль", "👤 Profile"]))
async def profile(msg: Message):
    u = msg.from_user
    lang = await db_get_lang(u.id)
    log   = await db_has_purchased(u.id, "logistics")
    china = await db_has_purchased(u.id, "china_order")
    refs  = await db_get_referral_count(u.id)
    bonus = f"{refs * REFERRAL_DISCOUNT}% discount potensial"

    await msg.answer(
        t(lang, "profile",
          name=u.full_name, uid=u.id,
          log=t(lang, "bought") if log else t(lang, "not_bought"),
          china=t(lang, "bought") if china else t(lang, "not_bought"),
          bot=BOT_USERNAME, refs=refs, bonus=bonus),
        parse_mode="HTML")

@router.message(F.text.in_(["🆘 Yordam", "🆘 Помощь", "🆘 Help"]))
async def help_msg(msg: Message):
    lang = await db_get_lang(msg.from_user.id)
    await msg.answer(t(lang, "help"), parse_mode="HTML")

# ---------- Kursni ko'rsatish ----------

async def show_course(msg: Message, bot: Bot, state: FSMContext, course_key: str):
    u = msg.from_user
    admin = is_admin(u.id)
    lang = await db_get_lang(u.id)

    if not admin and not await check_sub(bot, u.id):
        link = await channel_link(bot)
        await msg.answer(
            t(lang, "subscribe_required"),
            reply_markup=kb_subscribe(link, lang))
        return

    purchased = admin or await db_has_purchased(u.id, course_key)
    course    = await db_get_course(course_key)
    if not course:
        return

    if purchased:
        lessons = await db_get_lessons(course_key)
        if not lessons:
            await msg.answer(t(lang, "course_soon", name=course[2]),
                             reply_markup=kb_main(admin=admin, lang=lang), parse_mode="HTML")
        else:
            await state.update_data(active_course=course_key)
            await msg.answer(t(lang, "course_lessons", name=course[2]),
                             reply_markup=kb_lessons(lessons, course_key, lang), parse_mode="HTML")
    else:
        # To'lov sahifasini ko'rganini qayd etamiz (eslatma uchun)
        await db_log_payment_view(u.id, course_key)

        price_fmt = fmt_price(course[4])
        await msg.answer(
            t(lang, "course_buy", name=course[2], desc=course[3], price=price_fmt),
            reply_markup=kb_buy(course_key, lang), parse_mode="HTML")

LOGISTICS_BTN = ["📦 Logistika kursi", "📦 Логистика", "📦 Logistics Course"]
CHINA_BTN     = ["🇨🇳 Xitoydan zakaz kursi", "🇨🇳 Заказ из Китая", "🇨🇳 China Order Course"]

@router.message(F.text.in_(LOGISTICS_BTN))
async def btn_logistics(msg: Message, bot: Bot, state: FSMContext):
    await show_course(msg, bot, state, "logistics")

@router.message(F.text.in_(CHINA_BTN))
async def btn_china(msg: Message, bot: Bot, state: FSMContext):
    await show_course(msg, bot, state, "china_order")

@router.callback_query(F.data.startswith("course_"))
async def cb_course(cb: CallbackQuery, bot: Bot, state: FSMContext):
    course_key = cb.data.replace("course_", "")
    purchased  = is_admin(cb.from_user.id) or await db_has_purchased(cb.from_user.id, course_key)
    course     = await db_get_course(course_key)
    lang       = await db_get_lang(cb.from_user.id)
    if not course:
        await cb.answer()
        return

    if purchased:
        lessons = await db_get_lessons(course_key)
        if not lessons:
            await cb.message.edit_text(t(lang, "course_soon", name=course[2]), parse_mode="HTML")
        else:
            await state.update_data(active_course=course_key)
            await cb.message.delete()
            await bot.send_message(
                cb.from_user.id,
                t(lang, "course_lessons", name=course[2]),
                reply_markup=kb_lessons(lessons, course_key, lang), parse_mode="HTML")
    else:
        price_fmt = fmt_price(course[4])
        await cb.message.edit_text(
            t(lang, "course_buy", name=course[2], desc=course[3], price=price_fmt),
            reply_markup=kb_buy(course_key, lang), parse_mode="HTML")
    await cb.answer()

# ---------- Darsni ochish (ReplyKeyboard) ----------

@router.message(F.text.regexp(r"^📖 (\d+)-dars:"))
async def open_lesson_btn(msg: Message, state: FSMContext, bot: Bot):
    match = re.match(r"^📖 (\d+)-dars:", msg.text)
    if not match:
        return
    lesson_number = int(match.group(1))
    lang = await db_get_lang(msg.from_user.id)
    data = await state.get_data()
    course_key = data.get("active_course")

    if not course_key:
        await msg.answer(t(lang, "select_course_first"))
        return

    if not is_admin(msg.from_user.id) and not await db_has_purchased(msg.from_user.id, course_key):
        await msg.answer(t(lang, "no_access"))
        return

    lesson = await db_get_lesson(course_key, lesson_number)
    if not lesson:
        await msg.answer(t(lang, "lesson_not_found"))
        return

    caption = f"📖 <b>{lesson[2]}-dars: {lesson[3]}</b>"
    if lesson[4]:
        caption += f"\n\n{lesson[4]}"

    if lesson[5]:
        if lesson[6] == "video":
            await msg.answer_video(lesson[5], caption=caption, parse_mode="HTML")
        elif lesson[6] == "photo":
            await msg.answer_photo(lesson[5], caption=caption, parse_mode="HTML")
        elif lesson[6] == "document":
            await msg.answer_document(lesson[5], caption=caption, parse_mode="HTML")
        else:
            await msg.answer(caption, parse_mode="HTML")
    else:
        await msg.answer(caption, parse_mode="HTML")

# ---------- Bundle (ikkala kurs birga) ----------

@router.callback_query(F.data == "buy_bundle")
async def cb_buy_bundle(cb: CallbackQuery, state: FSMContext):
    lang = await db_get_lang(cb.from_user.id)
    log_course   = await db_get_course("logistics")
    china_course = await db_get_course("china_order")
    full_price   = log_course[4] + china_course[4]

    # Referral chegirmasini ham qo'shamiz
    state_data = await state.get_data()
    extra_discount = state_data.get("referral_discount", 0)
    promo_discount = state_data.get("promo_discount", 0)
    total_discount = BUNDLE_DISCOUNT + extra_discount + promo_discount

    bundle_price = apply_discount(full_price, total_discount)
    await state.update_data(pay_course="bundle", bundle_price=bundle_price)

    await cb.message.edit_text(
        t(lang, "bundle_desc",
          full=fmt_price(full_price),
          price=fmt_price(bundle_price),
          discount=total_discount),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_buy"), callback_data="buy_bundle_confirm")],
            [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="back_to_main")],
        ]),
        parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "buy_bundle_confirm")
async def cb_buy_bundle_confirm(cb: CallbackQuery, state: FSMContext):
    lang = await db_get_lang(cb.from_user.id)
    state_data = await state.get_data()
    bundle_price = state_data.get("bundle_price", 498000)

    await cb.message.edit_text(
        t(lang, "payment_info",
          name="📦🇨🇳 Bundle (ikkala kurs)",
          price=fmt_price(bundle_price),
          card=CARD_NUMBER,
          owner=CARD_OWNER),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_check"), callback_data="send_check_bundle")],
        ]),
        parse_mode="HTML")
    await cb.answer()

# ---------- Sotib olish (yagona kurs) ----------

@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(cb: CallbackQuery, state: FSMContext):
    course_key = cb.data.replace("buy_", "")
    if course_key in ("bundle", "bundle_confirm"):
        return  # yuqorida handle qilinadi
    lang = await db_get_lang(cb.from_user.id)
    course = await db_get_course(course_key)
    if not course:
        await cb.answer("❌ Kurs topilmadi", show_alert=True)
        return

    # Chegirmalarni hisoblaymiz
    state_data = await state.get_data()
    referral_discount = state_data.get("referral_discount", 0)
    promo_discount    = state_data.get("promo_discount", 0)
    total_discount    = referral_discount + promo_discount

    final_price = apply_discount(course[4], total_discount) if total_discount > 0 else course[4]

    discount_text = ""
    if total_discount > 0:
        discount_text = f"\n🎉 Chegirma: <b>{total_discount}%</b> | Asl narx: <s>{fmt_price(course[4])}</s> so'm\n"

    await state.update_data(pay_course=course_key, pay_price=final_price)

    await cb.message.edit_text(
        t(lang, "payment_info",
          name=course[2],
          price=fmt_price(final_price),
          card=CARD_NUMBER,
          owner=CARD_OWNER) + discount_text,
        reply_markup=kb_pay_confirm(course_key, lang), parse_mode="HTML")
    await cb.answer()

# ---------- Promo-kod kiritish ----------

@router.callback_query(F.data.startswith("send_check_"))
async def cb_send_check(cb: CallbackQuery, state: FSMContext):
    course_key = cb.data.replace("send_check_", "")
    lang = await db_get_lang(cb.from_user.id)
    await state.update_data(pay_course=course_key)
    # Avval promo-kod so'raymiz
    await cb.message.edit_text(t(lang, "promo_enter"), parse_mode="HTML")
    await state.set_state(PaySt.promo_code)
    await cb.answer()

@router.message(PaySt.promo_code)
async def handle_promo_code(msg: Message, state: FSMContext):
    lang = await db_get_lang(msg.from_user.id)
    code = msg.text.strip()

    if code.lower() == "/skip" or code == "-":
        await msg.answer("📸 " + t(lang, "send_check"))
        await state.set_state(PaySt.waiting_check)
        return

    discount, error = await db_validate_promo(code, msg.from_user.id)
    if error:
        await msg.answer(t(lang, "promo_invalid"))
        await msg.answer("📸 " + t(lang, "send_check"))
        await state.set_state(PaySt.waiting_check)
        return

    await state.update_data(promo_code=code, promo_discount=discount)
    await msg.answer(t(lang, "promo_applied", discount=discount), parse_mode="HTML")
    await msg.answer("📸 " + t(lang, "send_check"))
    await state.set_state(PaySt.waiting_check)

@router.message(PaySt.waiting_check, F.photo | F.document)
async def receive_check(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    course_key = data.get("pay_course")
    promo_code = data.get("promo_code")
    lang = await db_get_lang(msg.from_user.id)

    if msg.photo:
        file_id, ftype = msg.photo[-1].file_id, "photo"
    else:
        file_id, ftype = msg.document.file_id, "document"

    payment_id = await db_create_payment(msg.from_user.id, course_key, file_id, ftype)
    if promo_code:
        await db_use_promo(promo_code, msg.from_user.id)
    await state.clear()

    await msg.answer(
        t(lang, "check_received"),
        reply_markup=kb_main(admin=is_admin(msg.from_user.id), lang=lang))

    payment = await db_get_payment(payment_id)
    if not payment:
        return

    caption = (
        f"💸 <b>Yangi to'lov so'rovi!</b>\n\n"
        f"👤 {payment[5]} (@{payment[6] or 'yo`q'})\n"
        f"🆔 ID: <code>{payment[1]}</code>\n"
        f"📚 Kurs: <b>{payment[7]}</b>"
    )
    if promo_code:
        caption += f"\n🎟 Promo: <b>{promo_code}</b>"

    for aid in ADMIN_IDS:
        try:
            if ftype == "photo":
                await bot.send_photo(aid, photo=file_id, caption=caption,
                                     reply_markup=kb_admin_approve(payment_id), parse_mode="HTML")
            else:
                await bot.send_document(aid, document=file_id, caption=caption,
                                        reply_markup=kb_admin_approve(payment_id), parse_mode="HTML")
        except Exception as e:
            logging.warning(f"Admin {aid} ga xabar yuborishda xatolik: {e}")

# ---------- To'lovni tasdiqlash / rad etish ----------

@router.callback_query(F.data.startswith("approve_"))
async def cb_approve(cb: CallbackQuery, bot: Bot):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    request_id = int(cb.data.replace("approve_", ""))
    user_id, course_key = await db_approve_payment(request_id)
    if user_id:
        # Bundle bo'lsa ikkala kursni ham oching
        if course_key == "bundle":
            await db_grant_access(user_id, "logistics")
            await db_grant_access(user_id, "china_order")
            cname = "📦🇨🇳 Bundle (ikkala kurs)"
        else:
            course = await db_get_course(course_key)
            cname  = course[2] if course else course_key
        try:
            await cb.message.edit_caption(
                cb.message.caption + "\n\n✅ <b>TASDIQLANDI</b>", parse_mode="HTML")
        except Exception:
            pass

        lang = await db_get_lang(user_id)
        try:
            await bot.send_message(
                user_id,
                t(lang, "course_opened", name=cname),
                parse_mode="HTML")
        except Exception as e:
            logging.warning(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
        await cb.answer("✅ Tasdiqlandi!")
    else:
        await cb.answer("❌ Xatolik: to'lov topilmadi", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def cb_reject(cb: CallbackQuery, bot: Bot):
    if not is_admin(cb.from_user.id):
        await cb.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    request_id = int(cb.data.replace("reject_", ""))
    user_id = await db_reject_payment(request_id)
    try:
        await cb.message.edit_caption(
            cb.message.caption + "\n\n❌ <b>RAD ETILDI</b>", parse_mode="HTML")
    except Exception:
        pass
    if user_id:
        lang = await db_get_lang(user_id)
        try:
            await bot.send_message(user_id, t(lang, "payment_rejected"))
        except Exception as e:
            logging.warning(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
    await cb.answer("❌ Rad etildi!")

# ============================================================
# 👑  ADMIN PANEL
# ============================================================

@router.message(F.text.in_(["⚙️ Admin panel", "⚙️ Админ панель", "⚙️ Admin Panel"]))
async def admin_panel(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    await msg.answer("👑 <b>Admin paneli</b>", reply_markup=kb_admin_panel(), parse_mode="HTML")

@router.callback_query(F.data == "back_adm")
async def cb_back_adm(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("👑 <b>Admin paneli</b>",
                                reply_markup=kb_admin_panel(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(cb: CallbackQuery):
    lang = await db_get_lang(cb.from_user.id)
    await cb.message.delete()
    await cb.message.bot.send_message(
        cb.from_user.id,
        t(lang, "main_menu"),
        reply_markup=kb_main(admin=is_admin(cb.from_user.id), lang=lang))
    await cb.answer()

# --- Statistika ---

@router.callback_query(F.data == "adm_stats")
async def cb_stats(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    total   = await db_users_count()
    log_cnt = await db_purchases_count("logistics")
    chi_cnt = await db_purchases_count("china_order")
    rev     = await db_total_revenue()
    await cb.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n\n"
        f"📦 Logistika sotib olganlar: <b>{log_cnt}</b>\n"
        f"🇨🇳 Xitoy kursi sotib olganlar: <b>{chi_cnt}</b>\n\n"
        f"💰 Umumiy tushum: <b>{fmt_price(rev)} so'm</b>",
        reply_markup=kb_back_adm(), parse_mode="HTML")
    await cb.answer()

# --- Darslar ro'yxati (admin) ---

@router.callback_query(F.data.startswith("adm_lessons_"))
async def cb_adm_lessons(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    course_key = cb.data.replace("adm_lessons_", "")
    lessons    = await db_get_lessons(course_key)
    course     = await db_get_course(course_key)
    cname      = course[2] if course else course_key
    text = (f"📚 <b>{cname}</b>\n\nJami: <b>{len(lessons)} ta dars</b>"
            if lessons else f"📚 <b>{cname}</b>\n\nHali dars qo'shilmagan.")
    await cb.message.edit_text(text,
        reply_markup=kb_admin_lessons(lessons, course_key), parse_mode="HTML")
    await cb.answer()

# --- Darsni o'chirish (admin) ---

@router.callback_query(F.data.startswith("adm_del_"))
async def cb_adm_del(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    parts         = cb.data.replace("adm_del_", "").rsplit("_", 1)
    course_key    = parts[0]
    lesson_number = int(parts[1])
    await db_delete_lesson(course_key, lesson_number)
    lessons = await db_get_lessons(course_key)
    course  = await db_get_course(course_key)
    cname   = course[2] if course else course_key
    text = (f"📚 <b>{cname}</b>\n\n🗑 {lesson_number}-dars o'chirildi.\nJami: <b>{len(lessons)} ta dars</b>"
            if lessons else f"📚 <b>{cname}</b>\n\n🗑 {lesson_number}-dars o'chirildi.\nDarslar yo'q.")
    await cb.message.edit_text(text,
        reply_markup=kb_admin_lessons(lessons, course_key), parse_mode="HTML")
    await cb.answer("🗑 O'chirildi!")

# --- Dars qo'shish (admin) ---

@router.callback_query(F.data == "adm_add_lesson")
async def cb_adm_add(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("📚 Qaysi kursga dars qo'shmoqchisiz?",
                                reply_markup=kb_select_course("addlesson"))
    await state.set_state(AddLessonSt.course)
    await cb.answer()

@router.callback_query(F.data.startswith("addlesson_"))
async def cb_addlesson_course(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    course_key = cb.data.replace("addlesson_", "")
    next_num   = await db_next_lesson_number(course_key)
    await state.update_data(les_course=course_key, les_number=next_num)
    await cb.message.edit_text(
        f"Keyingi dars raqami: <b>{next_num}</b>\n\n"
        "O'zgartirish uchun raqam yuboring, aks holda <b>OK</b> yuboring:",
        parse_mode="HTML")
    await state.set_state(AddLessonSt.number)
    await cb.answer()

@router.message(AddLessonSt.number)
async def add_les_number(msg: Message, state: FSMContext):
    if msg.text.strip().upper() != "OK":
        try:
            await state.update_data(les_number=int(msg.text.strip()))
        except ValueError:
            await msg.answer("❌ Faqat raqam yoki OK!")
            return
    await msg.answer("📝 Dars sarlavhasini yuboring:")
    await state.set_state(AddLessonSt.title)

@router.message(AddLessonSt.title)
async def add_les_title(msg: Message, state: FSMContext):
    await state.update_data(les_title=msg.text.strip())
    await msg.answer("✏️ Dars matnini yuboring ('-' — bo'sh qoldirish):")
    await state.set_state(AddLessonSt.content)

@router.message(AddLessonSt.content)
async def add_les_content(msg: Message, state: FSMContext):
    content = "" if msg.text.strip() == "-" else msg.text.strip()
    await state.update_data(les_content=content)
    await msg.answer("📎 Video, rasm yoki hujjat yuboring.\nFayl bo'lmasa <b>skip</b> yuboring.",
                     parse_mode="HTML")
    await state.set_state(AddLessonSt.file)

@router.message(AddLessonSt.file)
async def add_les_file(msg: Message, state: FSMContext):
    file_id, ftype = "", ""
    if msg.video:
        file_id, ftype = msg.video.file_id, "video"
    elif msg.photo:
        file_id, ftype = msg.photo[-1].file_id, "photo"
    elif msg.document:
        file_id, ftype = msg.document.file_id, "document"
    elif msg.text and msg.text.lower() == "skip":
        pass
    else:
        await msg.answer("❌ Video, rasm, hujjat yoki 'skip' yuboring!")
        return

    data = await state.get_data()
    await db_add_lesson(data["les_course"], data["les_number"],
                        data["les_title"], data.get("les_content", ""), file_id, ftype)
    await state.clear()
    cname = COURSE_NAMES.get(data["les_course"], data["les_course"])
    await msg.answer(
        f"✅ <b>{data['les_number']}-dars</b> qo'shildi!\nKurs: {cname}",
        reply_markup=kb_main(admin=True), parse_mode="HTML")

# --- Kutayotgan to'lovlar (admin) ---

@router.callback_query(F.data == "adm_pending")
async def cb_adm_pending(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    payments = await db_pending_payments()
    text = (f"💸 <b>{len(payments)} ta kutayotgan to'lov bor.</b>\n\n"
            "Har bir to'lov uchun chek xabari alohida yuborilgan edi."
            if payments else "✅ Kutayotgan to'lov yo'q.")
    await cb.message.edit_text(text, reply_markup=kb_back_adm(), parse_mode="HTML")
    await cb.answer()

# --- Kirish berish (admin) ---

@router.callback_query(F.data == "adm_grant")
async def cb_adm_grant(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await cb.message.edit_text("👤 Foydalanuvchi Telegram ID sini yuboring:")
    await state.set_state(GrantSt.user_id)
    await cb.answer()

@router.message(GrantSt.user_id)
async def grant_user_id(msg: Message, state: FSMContext):
    try:
        uid = int(msg.text.strip())
        await state.update_data(grant_uid=uid)
        await msg.answer("📚 Qaysi kursga kirish bermoqchisiz?",
                         reply_markup=kb_select_course("grantaccess"))
        await state.set_state(GrantSt.course)
    except ValueError:
        await msg.answer("❌ Faqat raqam yuboring!")

@router.callback_query(F.data.startswith("grantaccess_"), GrantSt.course)
async def grant_course(cb: CallbackQuery, state: FSMContext, bot: Bot):
    course_key = cb.data.replace("grantaccess_", "")
    data       = await state.get_data()
    uid        = data["grant_uid"]
    await db_grant_access(uid, course_key)
    await state.clear()
    course = await db_get_course(course_key)
    cname  = course[2] if course else course_key
    await cb.message.edit_text(
        f"✅ <code>{uid}</code> ga <b>{cname}</b> kursi ochildi!",
        reply_markup=kb_back_adm(), parse_mode="HTML")
    lang = await db_get_lang(uid)
    try:
        await bot.send_message(
            uid, t(lang, "course_opened", name=cname), parse_mode="HTML")
    except Exception as e:
        logging.warning(f"Foydalanuvchi {uid} ga xabar yuborishda xatolik: {e}")
    await cb.answer("✅ Kirish berildi!")

# ============================================================
# 🎟  PROMO-KOD YARATISH (ADMIN)
# ============================================================

@router.callback_query(F.data == "adm_promo")
async def cb_adm_promo(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await cb.message.edit_text(
        "🎟 <b>Promo-kod yaratish</b>\n\nKod matnini yuboring (lotin harflari/raqamlar):\nMisol: <code>SALE20</code>",
        reply_markup=kb_back_adm(), parse_mode="HTML")
    await state.set_state(PromoSt.code)
    await cb.answer()

@router.message(PromoSt.code)
async def promo_enter_code(msg: Message, state: FSMContext):
    code = msg.text.strip().upper()
    if not re.match(r'^[A-Z0-9_]{3,20}$', code):
        await msg.answer("❌ Kod faqat lotin harflari, raqamlar va _ dan iborat bo'lsin (3-20 belgi).")
        return
    await state.update_data(promo_code=code)
    await msg.answer(f"✅ Kod: <b>{code}</b>\n\n📊 Chegirma foizini kiriting (masalan: 15):", parse_mode="HTML")
    await state.set_state(PromoSt.discount)

@router.message(PromoSt.discount)
async def promo_enter_discount(msg: Message, state: FSMContext):
    try:
        discount = int(msg.text.strip())
        if not (1 <= discount <= 100):
            raise ValueError
    except ValueError:
        await msg.answer("❌ 1 dan 100 gacha raqam kiriting!")
        return
    await state.update_data(promo_discount=discount)
    await msg.answer(f"✅ Chegirma: <b>{discount}%</b>\n\n👥 Maksimal foydalanish sonini kiriting (masalan: 50):", parse_mode="HTML")
    await state.set_state(PromoSt.max_uses)

@router.message(PromoSt.max_uses)
async def promo_enter_max_uses(msg: Message, state: FSMContext):
    try:
        max_uses = int(msg.text.strip())
        if max_uses < 1:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Musbat raqam kiriting!")
        return
    data = await state.get_data()
    code     = data["promo_code"]
    discount = data["promo_discount"]
    await db_create_promo(code, discount, max_uses)
    await state.clear()
    await msg.answer(
        f"✅ <b>Promo-kod yaratildi!</b>\n\n"
        f"🎟 Kod: <code>{code}</code>\n"
        f"💰 Chegirma: <b>{discount}%</b>\n"
        f"👥 Foydalanish: <b>{max_uses} marta</b>",
        reply_markup=kb_main(admin=True), parse_mode="HTML")

# ============================================================
# ⏰  24 SOAT ESLATMA VAZIFASI
# ============================================================

async def reminder_task(bot: Bot):
    """Har 1 soatda ishga tushadi, 24 soat o'tgan viewlarni tekshiradi"""
    while True:
        try:
            views = await db_get_unreminded_views()
            for view in views:
                user_id, course_key, view_id = view
                course = await db_get_course(course_key)
                if not course:
                    await db_mark_reminded(view_id)
                    continue
                lang = await db_get_lang(user_id)
                try:
                    await bot.send_message(
                        user_id,
                        t(lang, "reminder_24h", name=course[2]),
                        reply_markup=kb_buy(course_key, lang),
                        parse_mode="HTML")
                    logging.info(f"Eslatma yuborildi: user={user_id}, course={course_key}")
                except Exception as e:
                    logging.warning(f"Eslatma yuborishda xatolik (user={user_id}): {e}")
                await db_mark_reminded(view_id)
                await asyncio.sleep(0.5)  # Flood limit
        except Exception as e:
            logging.error(f"reminder_task xatolik: {e}")
        await asyncio.sleep(3600)  # 1 soatda bir marta

# ============================================================
# 🏁  ISHGA TUSHIRISH
# ============================================================

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Eslatma vazifasini fonda ishga tushuramiz
    asyncio.create_task(reminder_task(bot))

    print("🤖 Bot ishga tushdi!")
    print(f"✅ Yangi funksiyalar:")
    print(f"   🎟 Promo-kod tizimi")
    print(f"   ⏰ 24 soat to'lov eslatmasi")
    print(f"   🌐 Ko'p tilli interfeys (UZ/RU/EN)")
    print(f"   📦 Bundle chegirma ({BUNDLE_DISCOUNT}%)")
    print(f"   🔗 Referral tizimi ({REFERRAL_DISCOUNT}% chegirma)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())