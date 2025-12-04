import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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

# Команды для меню
async def set_commands(application: Application):
    """Установка меню команд"""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь и инструкции"),
        BotCommand("menu", "Главное меню"),
        BotCommand("scheme", "Создать цветовую схему"),
        BotCommand("colors", "Список всех цветов"),
        BotCommand("circle", "Цветовой круг Иттена"),
        BotCommand("palette", "Полная палитра цветов"),
        BotCommand("color", "Информация о цвете"),
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🎨 *Цветовой бот Иттена*

Добро пожаловать! Я помогу вам создавать гармоничные цветовые схемы на основе цветового круга Иттена.

*Используйте меню команд или кнопки ниже для навигации:*
    """
    
    # Создаем клавиатуру главного меню
    keyboard = [
        [
            InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
            InlineKeyboardButton("📋 Все цвета", callback_data="main_colors")
        ],
        [
            InlineKeyboardButton("🔵 Цветовой круг", callback_data="main_circle"),
            InlineKeyboardButton("🌈 Вся палитра", callback_data="main_palette")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="main_help"),
            InlineKeyboardButton("ℹ️ О круге Иттена", callback_data="main_info")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu - главное меню"""
    menu_text = """
🎨 *Главное меню*

Выберите нужный раздел:
    """
    
    # Создаем клавиатуру главного меню
    keyboard = [
        [
            InlineKeyboardButton("🎨 Создать цветовую схему", callback_data="main_scheme"),
            InlineKeyboardButton("📋 Список всех цветов", callback_data="main_colors")
        ],
        [
            InlineKeyboardButton("🔵 Цветовой круг Иттена", callback_data="main_circle"),
            InlineKeyboardButton("🌈 Полная палитра", callback_data="main_palette")
        ],
        [
            InlineKeyboardButton("🎯 Информация о цвете", callback_data="main_color_info"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ],
        [
            InlineKeyboardButton("ℹ️ О круге Иттена", callback_data="main_info")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(menu_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🎨 *Помощь и инструкции*

*Как пользоваться ботом:*

1. *Создание цветовой схемы:*
   - Используйте команду `/scheme`
   - Или напишите название цвета в чат
   - Выберите тип цветовой схемы

2. *Просмотр цветов:*
   - `/colors` - все доступные цвета
   - `/circle` - цветовой круг
   - `/palette` - полная палитра
   - `/color [название]` - информация о цвете

3. *Типы цветовых схем:*
   • Комплементарная - противоположные цвета
   • Триада - 3 равноудаленных цвета
   • Аналоговая - соседние цвета
   • Квадрат - 4 цвета через 90°
   • Расщепленная комплементарная
   • Прямоугольная

*Примеры цветов:* red, blue, green, yellow, orange, violet

*Быстрый старт:* просто напишите название цвета в чат!
    """
    
    keyboard = [[
        InlineKeyboardButton("🎨 Главное меню", callback_data="main_menu"),
        InlineKeyboardButton("🚀 Начать создание схемы", callback_data="main_scheme")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

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
            response += f"• `{color_display}` - `{hex_code}`\n"
        response += "\n"
    
    response += "Напишите название цвета в чат для создания схемы!"
    
    keyboard = [[
        InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
        InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

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
            
            keyboard = [[
                InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
                InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
            ]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_photo(
                photo=circle_img,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
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
            
            keyboard = [[
                InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
                InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
            ]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_photo(
                photo=palette_img,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
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
        # Если цвет не указан, показываем инструкцию
        keyboard = [[
            InlineKeyboardButton("📋 Посмотреть все цвета", callback_data="main_colors"),
            InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Пожалуйста, укажите название цвета после команды.\n"
            "*Пример:* `/color red`\n"
            "Или используйте `/colors` чтобы увидеть все доступные цвета.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    color_name = ' '.join(context.args).lower().replace(' ', '_')
    color_info = color_circle.get_color_info(color_name)
    
    if not color_info:
        keyboard = [[
            InlineKeyboardButton("📋 Посмотреть все цвета", callback_data="main_colors"),
            InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Цвет '{color_name}' не найден.\n"
            "Используйте /colors чтобы увидеть все доступные цвета.",
            reply_markup=reply_markup
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
        keyboard = [[
            InlineKeyboardButton("🎨 Создать схемы", callback_data=f"scheme_color_{color_name}"),
            InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if color_img:
            await update.message.reply_photo(
                photo=color_img,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(caption, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error creating color preview: {e}")
        
        color_display = color_name.replace('_', ' ').title()
        hex_code = color_info['hex'].upper()
        rgb = color_info['rgb']
        
        keyboard = [[
            InlineKeyboardButton("🎨 Создать схемы", callback_data=f"scheme_color_{color_name}"),
            InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"*{color_display}*\n\n"
            f"HEX: `{hex_code}`\n"
            f"RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`\n\n"
            "Для создания схем используйте /scheme",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о круге Иттена"""
    info_text = """
🎨 *Цветовой круг Иттена*

*Иоганнес Иттен (1888-1967)* - швейцарский художник и теоретик цвета, разработавший 12-частный цветовой круг, который стал основой для изучения цвета.

*Структура круга:*
1. *Первичные цвета* (3): красный, желтый, синий
2. *Вторичные цвета* (3): оранжевый, зеленый, фиолетовый
3. *Третичные цвета* (6): красно-оранжевый, желто-оранжевый, желто-зеленый, сине-зеленый, сине-фиолетовый, красно-фиолетовый

*Принципы гармонии:*
• Контраст дополнительных цветов
• Контраст холодного и теплого
• Симультанный контраст
• Контраст насыщения
• Контраст светлого и темного

Используйте /scheme чтобы создать гармоничные цветовые сочетания!
    """
    
    keyboard = [[
        InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
        InlineKeyboardButton("🔵 Посмотреть круг", callback_data="main_circle"),
        InlineKeyboardButton("🔙 Меню", callback_data="main_menu")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)

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
    
    # Кнопки навигации
    keyboard.append([
        InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu"),
        InlineKeyboardButton("❓ Помощь", callback_data="main_help")
    ])
    
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
    
    # Кнопки навигации
    keyboard.append([
        InlineKeyboardButton("🔙 Выбрать другой цвет", callback_data="main_scheme"),
        InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
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
            # Кнопки для навигации
            keyboard = [[
                InlineKeyboardButton("🎨 Новая схема", callback_data=f"new_scheme_{base_color}"),
                InlineKeyboardButton("🔄 Другой цвет", callback_data="new_color")
            ], [
                InlineKeyboardButton("🏠 В меню", callback_data="main_menu"),
                InlineKeyboardButton("📋 Все цвета", callback_data="main_colors")
            ]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем изображение и текст
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img_bytes,
                caption=text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Удаляем предыдущее сообщение с выбором схемы
            await query.delete_message()
        else:
            await query.edit_message_text(f"🎨 *Цветовая схема:*\n\n{text}", parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error creating image: {e}")
        await query.edit_message_text(f"🎨 *Цветовая схема:*\n\n{text}", parse_mode='Markdown')

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок главного меню"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        await menu_command(query, context)
        
    elif query.data == "main_scheme":
        await choose_color(query, context)
        
    elif query.data == "main_colors":
        # Показываем список цветов
        colors = color_circle.get_all_colors_list()
        
        response = "*🎨 Все доступные цвета:*\n\n"
        
        for i in range(0, len(colors), 3):
            row = colors[i:i+3]
            for color in row:
                color_display = color.replace('_', ' ').title()
                hex_code = color_circle.colors.get(color, '#000000').upper()
                response += f"• `{color_display}` - `{hex_code}`\n"
            response += "\n"
        
        response += "Напишите название цвета в чат для создания схемы!"
        
        keyboard = [[
            InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
            InlineKeyboardButton("🎯 Информация о цвете", callback_data="main_color_info"),
            InlineKeyboardButton("🔙 Меню", callback_data="main_menu")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    elif query.data == "main_circle":
        await show_itten_circle(query, context)
        
    elif query.data == "main_palette":
        await show_full_palette(query, context)
        
    elif query.data == "main_help":
        await help_command(query, context)
        
    elif query.data == "main_info":
        await show_info(query, context)
        
    elif query.data == "main_color_info":
        keyboard = [[
            InlineKeyboardButton("📋 Посмотреть все цвета", callback_data="main_colors"),
            InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
            InlineKeyboardButton("🔙 Меню", callback_data="main_menu")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎯 *Информация о цвете*\n\n"
            "Напишите название цвета после команды `/color`\n"
            "*Пример:* `/color red`\n\n"
            "Или используйте кнопку ниже чтобы посмотреть все цвета.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def handle_special_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка специальных callback-команд"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("scheme_color_"):
        # Создание схемы с определенным цветом
        color_name = query.data.split('_')[2]
        context.user_data['base_color'] = color_name
        
        # Создаем клавиатуру с типами схем
        keyboard = []
        for scheme_type, scheme_name in color_circle.schemes.items():
            keyboard.append([
                InlineKeyboardButton(scheme_name, callback_data=f"scheme_{scheme_type}")
            ])
        
        # Кнопки навигации
        keyboard.append([
            InlineKeyboardButton("🔙 Назад", callback_data="main_colors"),
            InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
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
        
        # Кнопки навигации
        keyboard.append([
            InlineKeyboardButton("🔙 Выбрать другой цвет", callback_data="main_scheme"),
            InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
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
            InlineKeyboardButton("🎨 Выбрать цвет из списка", callback_data="main_scheme"),
            InlineKeyboardButton("📋 Посмотреть все цвета", callback_data="main_colors")
        ], [
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Цвет '{user_input}' не найден. Используйте /colors чтобы увидеть все доступные цвета.",
            reply_markup=reply_markup
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        keyboard = [[
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз.",
            reply_markup=reply_markup
        )

async def post_init(application: Application):
    """Функция для инициализации после запуска"""
    await set_commands(application)

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
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("colors", show_colors))
    application.add_handler(CommandHandler("circle", show_itten_circle))
    application.add_handler(CommandHandler("palette", show_full_palette))
    application.add_handler(CommandHandler("color", show_color_info))
    application.add_handler(CommandHandler("scheme", choose_color))
    
    # Регистрируем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(choose_scheme, pattern="^color_"))
    application.add_handler(CallbackQueryHandler(show_scheme, pattern="^scheme_"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^main_"))
    application.add_handler(CallbackQueryHandler(handle_special_commands, pattern="^scheme_color_"))
    application.add_handler(CallbackQueryHandler(handle_new_choice, pattern="^new_"))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_color_input))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Устанавливаем команды меню при запуске
    application.post_init = post_init
    
    # Запускаем бота
    print("=" * 50)
    print("🎨 Бот 'Цветовой круг Иттена' запущен!")
    print("=" * 50)
    print("\nДоступные команды в меню:")
    print("/start - Запустить бота")
    print("/menu - Главное меню")
    print("/help - Помощь и инструкции")
    print("/scheme - Создать цветовую схему")
    print("/colors - Список всех цветов")
    print("/circle - Цветовой круг Иттена")
    print("/palette - Полная палитра цветов")
    print("/color [название] - Информация о цвете")
    print("\n" + "=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
