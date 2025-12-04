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
🎨 *Цветовой бот Иттена*

*Доступные команды:*
/start - Начало работы
/help - Справка
/scheme - Создать цветовую схему
/colors - Все цвета
/circle - Цветовой круг
/palette - Вся палитра

*Просто напишите название цвета* для создания схемы с ним.

*Примеры цветов:* red, blue, green, yellow
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
*Как пользоваться ботом:*

1. Напишите название цвета (например: `red`)
2. Или используйте команду `/scheme` для выбора из списка
3. Выберите тип цветовой схемы

*Доступные команды:*
/scheme - Выбрать цвет для схемы
/colors - Посмотреть все цвета
/circle - Показать цветовой круг
/palette - Показать всю палитру
/color [имя] - Информация о цвете

*Типы цветовых схем:*
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
    
    # Создаем текст со списком цветов
    response = "*🎨 Все доступные цвета:*\n\n"
    
    for i in range(0, len(colors), 3):
        row = colors[i:i+3]
        for color in row:
            color_display = color.replace('_', ' ').title()
            hex_code = color_circle.colors.get(color, '#000000').upper()
            rgb = color_circle.hex_to_rgb(hex_code)
            response += f"• `{color_display}` - `{hex_code}` (RGB: {rgb[0]},{rgb[1]},{rgb[2]})\n"
        response += "\n"
    
    response += "Напишите название цвета в чат для создания схемы!"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def show_itten_circle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать цветовой круг Иттена"""
    try:
        circle_img = color_circle.create_itten_circle_image()
        if circle_img:
            caption = """
*🎨 Цветовой круг Иттена*

12 основных цветов:
1. Красный (Red)
2. Оранжевый (Orange)
3. Желтый (Yellow)
4. Желто-зеленый (Yellow Green)
5. Зеленый (Green)
6. Изумрудный (Emerald)
7. Голубой (Cyan)
8. Лазурный (Azure)
9. Синий (Blue)
10. Фиолетовый (Violet)
11. Пурпурный (Magenta)
12. Малиновый (Crimson)

Используйте для подбора гармоничных сочетаний!
            """
            await update.message.reply_photo(
                photo=circle_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "Не удалось создать изображение круга.\n"
                "Но вы можете использовать команды:\n"
                "/colors - чтобы увидеть все цвета\n"
                "/scheme - чтобы создать цветовую схему"
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
*🎨 Полная палитра цветов*

Все 22 цвета расширенного круга Иттена.
Каждый квадрат - отдельный цвет.

Используйте эти цвета для создания гармоничных схем!
            """
            await update.message.reply_photo(
                photo=palette_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "Не удалось создать изображение палитры.\n"
                "Но вы можете использовать /colors чтобы увидеть список всех цветов."
            )
    except Exception as e:
        logger.error(f"Error creating palette: {e}")
        await update.message.reply_text("Не удалось создать изображение палитры.")

async def show_color_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о конкретном цвете"""
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите название цвета.\n"
            "Например: `/color red`\n"
            "Или используйте `/colors` чтобы увидеть все доступные цвета.",
            parse_mode='Markdown'
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
        import colorsys
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
        caption = f"""
*{color_display}*

*Код цвета:*
HEX: `{hex_code}`
RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`
HSV: `{int(h*360)}°, {int(s*100)}%, {int(v*100)}%`
"""
        
        if color_img:
            await update.message.reply_photo(
                photo=color_img,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(caption, parse_mode='Markdown')
        
        # Предлагаем создать схемы с этим цветом
        keyboard = [[
            InlineKeyboardButton("🎨 Создать схемы", callback_data=f"scheme_color_{color_name}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Хотите создать цветовые схемы с цветом *{color_display}*?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
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

async def choose_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор базового цвета"""
    # Создаем клавиатуру с цветами
    colors = color_circle.get_all_colors_list()
    
    # Создаем кнопки с названиями цветов
    keyboard = []
    row = []
    
    for i, color in enumerate(colors):
        color_display = color.replace('_', ' ').title()
        if len(color_display) > 12:
            color_display = color_display[:10] + ".."
        
        row.append(InlineKeyboardButton(color_display, callback_data=f"color_{color}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Выберите базовый цвет:*\n\n"
        "Или просто напишите название цвета в чат.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
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
        "🎨 *Выберите тип цветовой схемы:*",
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
    
    text = f"*🎨 Цветовая схема:* {scheme_name}\n"
    text += f"*Базовый цвет:* {base_color_display}\n\n"
    text += "*Цвета в схеме:*\n"
    
    for i, color_info in enumerate(scheme_colors, 1):
        color_name = color_info['name'].replace('_', ' ').title()
        text += f"{i}. *{color_name}*: `{color_info['hex'].upper()}`\n"
        rgb = color_info['rgb']
        text += f"   RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}\n"
    
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
            await query.edit_message_text(f"🎨 *Цветовая схема:*\n\n{text}", parse_mode='Markdown')
        
        # Оставляем сообщение с кнопкой для нового выбора
        keyboard = [[
            InlineKeyboardButton("🎨 Новый цвет", callback_data="new_color"),
            InlineKeyboardButton("📋 Новую схему", callback_data=f"new_scheme_{base_color}")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Готово! Хотите создать еще одну схему?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error creating image: {e}")
        await query.edit_message_text(f"🎨 *Цветовая схема:*\n\n{text}", parse_mode='Markdown')

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
            "🎨 Выберите тип цветовой схемы:",
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
            "🎨 Выберите тип цветовой схемы:",
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
