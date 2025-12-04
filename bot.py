import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from color_circle import IttenColorCircle
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация цветового круга
color_circle = IttenColorCircle()

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🎨 *Бот для подбора цветов по кругу Иттена*

*Основные команды:*
/start - Начало работы
/help - Справка по командам
/scheme - Подобрать цветовую схему
/colors - Список доступных цветов с визуализацией
/info - Информация о круге Иттена
/circle - Показать цветовой круг Иттена
/palette - Показать полную палитру цветов
/color [название] - Информация о конкретном цвете

*Примеры цветов:* red, blue, green, yellow, violet, orange

Для выбора цвета просто напишите его название в чат!
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
*Доступные команды:*

/scheme - Подобрать цветовую схему
Выберите базовый цвет и тип схемы, чтобы получить гармоничную палитру

/colors - Показать все доступные цвета
Полный список цветов из расширенного круга Иттена

/circle - Показать цветовой круг Иттена
Визуальное представление 12-секторного круга

/palette - Показать полную палитру
Все цвета с кодами HEX и RGB

/color [название] - Информация о цвете
Подробная информация о конкретном цвете

/info - Информация о цветовом круге Иттена
Теория и принципы использования

*Просто напишите название цвета в чат*, чтобы начать создание схемы с ним.

*Типы схем:*
• Комплементарная - противоположные цвета
• Триада - 3 равноудаленных цвета
• Аналоговая - соседние цвета
• Квадрат - 4 цвета через 90°
• Расщепленная комплементарная
• Прямоугольная
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def show_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все доступные цвета"""
    colors = color_circle.get_all_colors_list()
    
    # Разделяем цвета на группы по 6 для лучшего отображения
    color_groups = [colors[i:i+6] for i in range(0, len(colors), 6)]
    
    response = "*Доступные цвета:*\n\n"
    for group in color_groups:
        for color in group:
            color_display = color.replace('_', ' ').title()
            hex_code = color_circle.colors.get(color, '#000000').upper()
            response += f"• {color_display} - `{hex_code}`\n"
        response += "\n"
    
    response += "\nНапишите название цвета в чат или используйте /color [название] для получения информации."
    
    # Пробуем создать простое изображение со списком цветов
    try:
        colors_img = color_circle.create_simple_color_list()
        if colors_img:
            await update.message.reply_photo(
                photo=colors_img,
                caption=response,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error creating colors list: {e}")
        await update.message.reply_text(response, parse_mode='Markdown')

async def show_itten_circle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать цветовой круг Иттена"""
    try:
        circle_img = color_circle.create_itten_circle_image()
        if circle_img:
            caption = """
*Цветовой круг Иттена*

12-секторный круг показывает основные цветовые отношения:
• 3 первичных цвета (красный, желтый, синий)
• 3 вторичных (оранжевый, зеленый, фиолетовый)
• 6 третичных цветов

Используйте круг для понимания цветовых гармоний!
            """
            await update.message.reply_photo(
                photo=circle_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "Не удалось создать изображение круга. "
                "Пожалуйста, попробуйте позже или используйте другие команды."
            )
    except Exception as e:
        logger.error(f"Error creating circle: {e}")
        await update.message.reply_text("Не удалось создать изображение круга.")

async def show_full_palette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать полную палитру"""
    try:
        palette_img = color_circle.create_extended_palette_image()
        if palette_img:
            caption = """
*Полная палитра цветов*

Все цвета расширенного круга Иттена с их:
• Названиями
• HEX-кодами
• RGB значениями

Используйте эти цвета для создания гармоничных схем!
            """
            await update.message.reply_photo(
                photo=palette_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            # Альтернатива: отправить текстовый список
            colors = color_circle.get_all_colors_list()
            response = "*Полная палитра цветов:*\n\n"
            for color in colors:
                color_display = color.replace('_', ' ').title()
                hex_code = color_circle.colors.get(color, '#000000').upper()
                response += f"• {color_display} - `{hex_code}`\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error creating palette: {e}")
        await update.message.reply_text("Не удалось создать изображение палитры.")

async def show_color_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о конкретном цвете"""
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите название цвета.\n"
            "Например: /color red\n"
            "Или используйте /colors чтобы увидеть все доступные цвета."
        )
        return
    
    color_name = ' '.join(context.args).lower().replace(' ', '_')
    color_info = color_circle.get_color_info(color_name)
    
    if not color_info:
        await update.message.reply_text(
            f"Цвет '{color_name}' не найден.\n"
            "Используйте /colors чтобы увидеть все доступные цвета."
        )
        return
    
    # Создаем и отправляем изображение с информацией о цвете
    try:
        color_img = color_circle.create_color_preview(color_name)
        
        color_display = color_name.replace('_', ' ').title()
        hex_code = color_info['hex'].upper()
        rgb = color_info['rgb']
        
        # Конвертация в HSV
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
        caption = f"""
*{color_display}*

*Код цвета:*
HEX: `{hex_code}`
RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`
HSV: `{int(h*360)}°, {int(s*100)}%, {int(v*100)}%`

*Использование:*
Этот цвет находится в позиции {color_circle.find_position(color_name) or 'N/A'}° в круге Иттена.
        """
        
        if color_img:
            await update.message.reply_photo(
                photo=color_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(caption, parse_mode='Markdown')
        
        # Показываем примеры использования цвета
        keyboard = [[
            InlineKeyboardButton("🎨 Схемы с этим цветом", callback_data=f"scheme_color_{color_name}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Хотите создать цветовые схемы с этим цветом?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error creating color preview: {e}")
        
        color_display = color_name.replace('_', ' ').title()
        hex_code = color_info['hex'].upper()
        rgb = color_info['rgb']
        
        await update.message.reply_text(
            f"*{color_display}*\n\n"
            f"HEX: `{hex_code}`\n"
            f"RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`\n\n"
            "Для создания схем используйте /scheme",
            parse_mode='Markdown'
        )

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о круге Иттена"""
    info_text = """
*Цветовой круг Иттена*

Иоганнес Иттен (1888-1967) - швейцарский художник и теоретик цвета, разработавший 12-частный цветовой круг, который стал основой для изучения цвета.

*Структура круга:*
1. Первичные цвета (3): красный, желтый, синий
2. Вторичные цвета (3): оранжевый, зеленый, фиолетовый
3. Третичные цвета (6): красно-оранжевый, желто-оранжевый, желто-зеленый, сине-зеленый, сине-фиолетовый, красно-фиолетовый

*Принципы гармонии:*
• Контраст дополнительных цветов
• Контраст холодного и теплого
• Симультанный контраст
• Контраст насыщения
• Контраст светлого и темного

Используйте /scheme чтобы создать гармоничные цветовые сочетания!
    """
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def choose_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор базового цвета"""
    # Создаем клавиатуру с цветами (группируем по 3 в ряд)
    colors = color_circle.get_all_colors_list()
    keyboard = []
    row = []
    
    for i, color in enumerate(colors):
        color_display = color.replace('_', ' ').title()
        # Сокращаем длинные названия
        if len(color_display) > 10:
            color_display = color_display[:8] + ".."
        row.append(InlineKeyboardButton(color_display, callback_data=f"color_{color}"))
        
        if len(row) == 4 or i == len(colors) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 Выберите базовый цвет или напишите его название в чат:",
        reply_markup=reply_markup
    )

async def choose_scheme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор типа схемы после выбора цвета"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем выбранный цвет
    color_name = query.data.split('_')[1]
    context.user_data['base_color'] = color_name
    
    # Создаем клавиатуру с типами схем
    keyboard = []
    for scheme_type, scheme_name in color_circle.schemes.items():
        keyboard.append([
            InlineKeyboardButton(scheme_name, callback_data=f"scheme_{scheme_type}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    color_display = color_name.replace('_', ' ').title()
    await query.edit_message_text(
        f"Выбран цвет: *{color_display}*\n\n"
        "Теперь выберите тип цветовой схемы:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_scheme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать выбранную цветовую схему"""
    query = update.callback_query
    await query.answer()
    
    scheme_type = query.data.split('_')[1]
    base_color = context.user_data.get('base_color', 'red')
    
    # Получаем схему
    scheme_colors = color_circle.get_scheme(base_color, scheme_type)
    
    if not scheme_colors:
        await query.edit_message_text("Ошибка при создании схемы. Попробуйте еще раз.")
        return
    
    # Создаем текст с информацией
    base_color_display = base_color.replace('_', ' ').title()
    scheme_name = color_circle.schemes.get(scheme_type, scheme_type)
    
    text = f"*Цветовая схема:* {scheme_name}\n"
    text += f"*Базовый цвет:* {base_color_display}\n\n"
    text += "*Цвета в схеме:*\n"
    
    for i, color_info in enumerate(scheme_colors, 1):
        color_name = color_info['name'].replace('_', ' ').title()
        text += f"{i}. *{color_name}*: `{color_info['hex'].upper()}`\n"
    
    # Создаем изображение палитры
    try:
        img_bytes = color_circle.create_color_palette_image(scheme_colors, scheme_name)
        
        if img_bytes:
            # Отправляем изображение и текст
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img_bytes,
                caption=text,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(f"Текстовая информация:\n\n{text}", parse_mode='Markdown')
        
        # Оставляем сообщение с кнопкой для нового выбора
        keyboard = [[
            InlineKeyboardButton("🎨 Новый цвет", callback_data="new_color"),
            InlineKeyboardButton("📋 Новую схему", callback_data=f"new_scheme_{base_color}")
        ], [
            InlineKeyboardButton("🔄 С другим базовым", callback_data=f"scheme_color_{base_color}")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Готово! Хотите создать еще одну схему?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error creating image: {e}")
        await query.edit_message_text(f"Текстовая информация:\n\n{text}", parse_mode='Markdown')

async def handle_special_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка специальных callback-команд"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_circle":
        # Показываем цветовой круг
        try:
            circle_img = color_circle.create_itten_circle_image()
            if circle_img:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=circle_img,
                    caption="Цветовой круг Иттена"
                )
        except Exception as e:
            logger.error(f"Error creating circle: {e}")
            await query.edit_message_text("Не удалось создать изображение круга.")
    
    elif query.data.startswith("scheme_color_"):
        # Создание схемы с определенным цветом
        color_name = query.data.split('_')[2]
        context.user_data['base_color'] = color_name
        
        # Создаем клавиатуру с типами схем
        keyboard = []
        for scheme_type, scheme_name in color_circle.schemes.items():
            keyboard.append([
                InlineKeyboardButton(scheme_name, callback_data=f"scheme_{scheme_type}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        color_display = color_name.replace('_', ' ').title()
        await query.edit_message_text(
            f"Создание схемы с цветом: *{color_display}*\n\n"
            "Выберите тип цветовой схемы:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_new_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок нового выбора"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "new_color":
        await choose_color(update, context)
    elif query.data.startswith("new_scheme"):
        base_color = query.data.split('_')[2]
        context.user_data['base_color'] = base_color
        await choose_scheme(update, context)

async def handle_color_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстового ввода цвета"""
    user_input = update.message.text.strip().lower().replace(' ', '_')
    
    # Проверяем, есть ли такой цвет
    color_info = color_circle.get_color_info(user_input)
    
    if color_info:
        context.user_data['base_color'] = user_input
        
        # Создаем клавиатуру с типами схем
        keyboard = []
        for scheme_type, scheme_name in color_circle.schemes.items():
            keyboard.append([
                InlineKeyboardButton(scheme_name, callback_data=f"scheme_{scheme_type}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        color_display = user_input.replace('_', ' ').title()
        await update.message.reply_text(
            f"Выбран цвет: *{color_display}*\n\n"
            "Теперь выберите тип цветовой схемы:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # Предлагаем выбрать цвет из списка
        keyboard = [[
            InlineKeyboardButton("🎨 Выбрать цвет из списка", callback_data="show_color_list")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Цвет '{user_input}' не найден. Используйте /colors чтобы увидеть все доступные цвета.",
            reply_markup=reply_markup
        )

async def show_color_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список цветов по кнопке"""
    query = update.callback_query
    await query.answer()
    
    await choose_color(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз или используйте /start"
        )

def main():
    """Запуск бота"""
    # Получаем токен бота
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("Не найден TELEGRAM_BOT_TOKEN в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("colors", show_colors))
    application.add_handler(CommandHandler("circle", show_itten_circle))
    application.add_handler(CommandHandler("palette", show_full_palette))
    application.add_handler(CommandHandler("color", show_color_info))
    application.add_handler(CommandHandler("info", show_info))
    application.add_handler(CommandHandler("scheme", choose_color))
    
    # Регистрируем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(choose_scheme, pattern="^color_"))
    application.add_handler(CallbackQueryHandler(show_scheme, pattern="^scheme_"))
    application.add_handler(CallbackQueryHandler(handle_special_commands, pattern="^(show_circle|scheme_color_)"))
    application.add_handler(CallbackQueryHandler(handle_new_choice, pattern="^new_"))
    application.add_handler(CallbackQueryHandler(show_color_list, pattern="^show_color_list$"))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_color_input))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🎨 Бот запущен...")
    print("Доступные команды:")
    print("/start - Начало работы")
    print("/scheme - Создание цветовой схемы")
    print("/circle - Цветовой круг Иттена")
    print("/palette - Полная палитра")
    print("/color [название] - Информация о цвете")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
