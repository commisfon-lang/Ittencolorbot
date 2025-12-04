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
        BotCommand("colors", "Список всех цветов (60+)"),
        BotCommand("circle", "Цветовой круг Иттена"),
        BotCommand("palette", "Полная палитра (60 цветов)"),
        BotCommand("color", "Информация о цвете"),
        BotCommand("shades", "Показать оттенки цвета"),
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🎨 *Расширенный цветовой бот Иттена*

Теперь с 60+ цветами! (12 основных цветов × 5 оттенков)

*Используйте меню команд или кнопки ниже:*
    """
    
    # Создаем клавиатуру главного меню
    keyboard = [
        [
            InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
            InlineKeyboardButton("🌈 60 цветов", callback_data="main_colors")
        ],
        [
            InlineKeyboardButton("🔵 Цветовой круг", callback_data="main_circle"),
            InlineKeyboardButton("🎨 Все оттенки", callback_data="main_palette")
        ],
        [
            InlineKeyboardButton("🔄 Оттенки цвета", callback_data="main_shades"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ],
        [
            InlineKeyboardButton("🎯 Инфо о цвете", callback_data="main_color_info")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu - главное меню"""
    menu_text = """
🎨 *Главное меню (60+ цветов)*

Выберите нужный раздел:
    """
    
    # Создаем клавиатуру главного меню
    keyboard = [
        [
            InlineKeyboardButton("🎨 Создать цветовую схему", callback_data="main_scheme"),
            InlineKeyboardButton("🌈 Все 60+ цветов", callback_data="main_colors")
        ],
        [
            InlineKeyboardButton("🔵 Цветовой круг Иттена", callback_data="main_circle"),
            InlineKeyboardButton("🎨 Полная палитра", callback_data="main_palette")
        ],
        [
            InlineKeyboardButton("🔄 Показать оттенки цвета", callback_data="main_shades"),
            InlineKeyboardButton("🎯 Информация о цвете", callback_data="main_color_info")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="main_help"),
            InlineKeyboardButton("ℹ️ О круге Иттена", callback_data="main_info")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(menu_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🎨 *Помощь и инструкции*

*Новые возможности: 60+ цветов!*
- 12 основных цветов круга Иттена
- 5 оттенков для каждого цвета (от светлого к темному)
- Всего более 60 цветов

*Как пользоваться ботом:*

1. *Создание цветовой схемы:*
   - Используйте команду `/scheme`
   - Или напишите название цвета в чат
   - Выберите тип цветовой схемы

2. *Работа с оттенками:*
   - `/shades [цвет]` - показать все 5 оттенков цвета
   - `/color [цвет]` - информация о цвете
   - `/palette` - полная палитра 60 цветов

3. *Просмотр цветов:*
   - `/colors` - список всех цветов
   - `/circle` - цветовой круг
   - `/palette` - сетка 60 цветов

4. *Типы цветовых схем:*
   • Комплементарная - противоположные цвета
   • Триада - 3 равноудаленных цвета
   • Аналоговая - соседние цвета
   • Квадрат - 4 цвета через 90°
   • Расщепленная комплементарная
   • Прямоугольная
   • Монохроматическая (оттенки одного цвета)

*Примеры цветов:*
- Основные: `red`, `blue`, `green`, `yellow`
- Оттенки: `red_1` (светлый), `red_3` (средний), `red_5` (темный)
- Нейтральные: `white`, `gray`, `black`

*Быстрый старт:* просто напишите название цвета в чат!
    """
    
    keyboard = [[
        InlineKeyboardButton("🎨 Главное меню", callback_data="main_menu"),
        InlineKeyboardButton("🚀 Начать создание схемы", callback_data="main_scheme")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_shades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать оттенки конкретного цвета"""
    if not context.args:
        # Показываем список основных цветов для выбора
        main_colors = color_circle.get_main_colors_list()
        
        keyboard = []
        row = []
        for i, color in enumerate(main_colors):
            color_display = color.replace('_', ' ').title()
            row.append(InlineKeyboardButton(color_display, callback_data=f"shades_{color}"))
            
            if len(row) == 2 or i == len(main_colors) - 1:
                keyboard.append(row)
                row = []
        
        keyboard.append([
            InlineKeyboardButton("🏠 В меню", callback_data="main_menu"),
            InlineKeyboardButton("❓ Помощь", callback_data="main_help")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎨 *Выберите цвет для просмотра оттенков:*\n\n"
            "Или напишите `/shades [цвет]` (например: `/shades red`)",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    color_name = ' '.join(context.args).lower().replace(' ', '_')
    await show_color_shades(update, context, color_name)

async def show_color_shades(update: Update, context: ContextTypes.DEFAULT_TYPE, color_name):
    """Показать оттенки выбранного цвета"""
    # Проверяем, существует ли цвет
    color_info = color_circle.get_color_info(color_name)
    
    if not color_info:
        # Пробуем найти основной цвет
        base_color = color_name.split('_')[0] if '_' in color_name else color_name
        if base_color in color_circle.main_colors:
            color_info = color_circle.get_color_info(base_color)
    
    if not color_info:
        await update.message.reply_text(
            f"Цвет '{color_name}' не найден.\n"
            "Используйте `/colors` чтобы увидеть все доступные цвета."
        )
        return
    
    # Определяем основной цвет
    if '_' in color_name and color_name.split('_')[-1].isdigit():
        base_color = '_'.join(color_name.split('_')[:-1])
    else:
        base_color = color_name
    
    # Получаем все оттенки
    shades = color_circle.get_all_shades(base_color)
    
    if not shades:
        await update.message.reply_text(
            f"Для цвета '{base_color}' нет оттенков.\n"
            "Этот цвет не входит в основные 12 цветов."
        )
        return
    
    # Создаем изображение с оттенками
    try:
        shades_img = color_circle.create_shades_palette(base_color)
        
        color_display = base_color.replace('_', ' ').title()
        caption = f"🎨 *5 оттенков цвета {color_display}:*\n\n"
        
        for i, shade_info in enumerate(shades, 1):
            shade_name = shade_info['name'].replace('_', ' ').title()
            hex_code = shade_info['hex'].upper()
            rgb = shade_info['rgb']
            caption += f"{i}. *{shade_name}*\n"
            caption += f"   HEX: `{hex_code}`\n"
            caption += f"   RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`\n\n"
        
        keyboard = [[
            InlineKeyboardButton("🎨 Создать схему с этим цветом", callback_data=f"scheme_color_{base_color}"),
            InlineKeyboardButton("🔙 Выбрать другой цвет", callback_data="main_shades")
        ], [
            InlineKeyboardButton("🏠 В меню", callback_data="main_menu"),
            InlineKeyboardButton("🌈 Все цвета", callback_data="main_colors")
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if shades_img:
            await update.message.reply_photo(
                photo=shades_img,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(caption, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error showing shades: {e}")
        
        color_display = base_color.replace('_', ' ').title()
        await update.message.reply_text(
            f"Не удалось создать изображение оттенков для цвета {color_display}.\n"
            f"Но вы можете создать схемы с этим цветом."
        )

async def show_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все доступные цвета (60+)"""
    main_colors = color_circle.get_main_colors_list()
    
    response = "🎨 *Все доступные цвета (60+):*\n\n"
    response += "*12 основных цветов (средние тона):*\n"
    
    for i, color in enumerate(main_colors, 1):
        color_display = color.replace('_', ' ').title()
        hex_code = color_circle.colors.get(color, '#000000').upper()
        response += f"{i}. `{color_display}` - `{hex_code}`\n"
    
    response += "\n*5 оттенков для каждого цвета:*\n"
    response += "  • `[цвет]_1` - самый светлый\n"
    response += "  • `[цвет]_2` - светлый\n"
    response += "  • `[цвет]_3` - средний (основной)\n"
    response += "  • `[цвет]_4` - темный\n"
    response += "  • `[цвет]_5` - самый темный\n\n"
    
    response += "*Пример:* Для красного (red) доступны:\n"
    response += "`red_1`, `red_2`, `red_3`, `red_4`, `red_5`\n\n"
    
    response += "*Нейтральные цвета:*\n"
    for neutral in color_circle.neutral_colors:
        hex_code = color_circle.colors.get(neutral, '#000000').upper()
        neutral_display = neutral.replace('_', ' ').title()
        response += f"• `{neutral_display}` - `{hex_code}`\n"
    
    response += "\nИспользуйте `/shades [цвет]` чтобы увидеть все оттенки цвета."
    
    keyboard = [[
        InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
        InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades")
    ], [
        InlineKeyboardButton("🌈 Полная палитра", callback_data="main_palette"),
        InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

async def show_itten_circle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать цветовой круг Иттена"""
    try:
        circle_img = color_circle.create_itten_circle_image()
        if circle_img:
            caption = """
🎨 *Цветовой круг Иттена (12 основных цветов)*

1. Красный (Red) - 0°
2. Красно-оранжевый (Red-Orange) - 30°
3. Оранжевый (Orange) - 60°
4. Желто-оранжевый (Yellow-Orange) - 90°
5. Желтый (Yellow) - 120°
6. Желто-зеленый (Yellow-Green) - 150°
7. Зеленый (Green) - 180°
8. Зелено-синий (Green-Blue) - 210°
9. Синий (Blue) - 240°
10. Сине-фиолетовый (Blue-Violet) - 270°
11. Фиолетовый (Violet) - 300°
12. Красно-фиолетовый (Red-Violet) - 330°

Каждый цвет имеет 5 оттенков от светлого к темному.
            """
            
            keyboard = [[
                InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
                InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades")
            ], [
                InlineKeyboardButton("🌈 Полная палитра", callback_data="main_palette"),
                InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
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
    """Показать полную палитру (60 цветов)"""
    try:
        palette_img = color_circle.create_extended_palette_image()
        if palette_img:
            caption = """
🎨 *Полная палитра цветов (60 цветов)*

Сетка 12×5 цветов:
- 12 столбцов = основные цвета круга Иттена
- 5 строк = оттенки от светлого к темному

*Как читать палитру:*
• Горизонтальные строки - оттенки одного цвета
• Вертикальные столбцы - разные цвета на круге

Используйте эти цвета для создания гармоничных схем!
            """
            
            keyboard = [[
                InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
                InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades")
            ], [
                InlineKeyboardButton("🔵 Цветовой круг", callback_data="main_circle"),
                InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
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

# Остальные функции (show_color_info, choose_color, choose_scheme, show_scheme, 
# handle_main_menu, handle_special_commands, handle_new_choice, handle_color_input)
# остаются примерно такими же, но с учетом новых возможностей

# Для экономии места, я покажу только ключевые изменения:

async def choose_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор базового цвета"""
    # Предлагаем выбрать из основных цветов
    main_colors = color_circle.get_main_colors_list()
    
    keyboard = []
    row = []
    
    for i, color in enumerate(main_colors):
        color_display = color.replace('_', ' ').title()
        row.append(InlineKeyboardButton(color_display, callback_data=f"color_{color}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Добавляем опцию выбора оттенков
    keyboard.append([
        InlineKeyboardButton("🔄 Показать оттенки цвета", callback_data="main_shades"),
        InlineKeyboardButton("🌈 Все цвета", callback_data="main_colors")
    ])
    
    keyboard.append([
        InlineKeyboardButton("🏠 В меню", callback_data="main_menu"),
        InlineKeyboardButton("❓ Помощь", callback_data="main_help")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Выберите базовый цвет (средний тон):*\n\n"
        "Или напишите название цвета с оттенком (например: `red_3`)\n"
        "Или просто название цвета (например: `red`)",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# В обработчике текстового ввода добавляем поддержку оттенков:
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
            InlineKeyboardButton("🔄 Показать оттенки этого цвета", 
                               callback_data=f"shades_{user_input.split('_')[0]}"),
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
        # Проверяем, может это основной цвет без оттенка
        if user_input in color_circle.main_colors:
            context.user_data['base_color'] = user_input
            
            keyboard = []
            for scheme_type, scheme_name in color_circle.schemes.items():
                keyboard.append([
                    InlineKeyboardButton(scheme_name, callback_data=f"scheme_{scheme_type}")
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔄 Показать оттенки этого цвета", 
                                   callback_data=f"shades_{user_input}"),
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
            # Цвет не найден
            keyboard = [[
                InlineKeyboardButton("🎨 Выбрать цвет из списка", callback_data="main_scheme"),
                InlineKeyboardButton("🌈 Посмотреть все цвета", callback_data="main_colors")
            ], [
                InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Цвет '{user_input}' не найден.\n\n"
                "Доступные форматы:\n"
                "• Основной цвет: `red`, `blue`, `green`\n"
                "• Оттенок: `red_1`, `red_2`, `red_3`, `red_4`, `red_5`\n\n"
                "Используйте `/colors` чтобы увидеть все доступные цвета.",
                reply_markup=reply_markup
            )

# Добавляем обработку кнопок оттенков в handle_main_menu:
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок главного меню"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_menu":
        await menu_command(query, context)
        
    elif query.data == "main_scheme":
        await choose_color(query, context)
        
    elif query.data == "main_colors":
        await show_colors(query, context)
        
    elif query.data == "main_circle":
        await show_itten_circle(query, context)
        
    elif query.data == "main_palette":
        await show_full_palette(query, context)
        
    elif query.data == "main_shades":
        await show_shades(query, context)
        
    elif query.data == "main_help":
        await help_command(query, context)
        
    elif query.data == "main_info":
        await show_info(query, context)
        
    elif query.data == "main_color_info":
        await show_color_info_from_menu(query, context)
        
    elif query.data.startswith("shades_"):
        color_name = query.data.split('_', 1)[1]
        await show_color_shades(query, context, color_name)

async def show_color_info_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о цвете из меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[
        InlineKeyboardButton("📋 Посмотреть все цвета", callback_data="main_colors"),
        InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme")
    ], [
        InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades"),
        InlineKeyboardButton("🏠 В меню", callback_data="main_menu")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 *Информация о цвете*\n\n"
        "Напишите название цвета после команды `/color`\n"
        "*Примеры:*\n"
        "• `/color red` - информация о красном\n"
        "• `/color red_3` - информация о среднем оттенке красного\n\n"
        "Или используйте кнопки ниже.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Добавляем show_info функцию
async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о круге Иттена"""
    info_text = """
🎨 *Цветовой круг Иттена (расширенный)*

*Иоганнес Иттен (1888-1967)* - швейцарский художник и теоретик цвета.

*Структура расширенного круга:*
• 12 основных цветов (через 30°)
• 5 оттенков для каждого цвета (от светлого к темному)
• Всего 60 цветов + нейтральные

*Основные цвета:*
1. Красный (0°)
2. Красно-оранжевый (30°)
3. Оранжевый (60°)
4. Желто-оранжевый (90°)
5. Желтый (120°)
6. Желто-зеленый (150°)
7. Зеленый (180°)
8. Зелено-синий (210°)
9. Синий (240°)
10. Сине-фиолетовый (270°)
11. Фиолетовый (300°)
12. Красно-фиолетовый (330°)

*Новая функция: монохроматические схемы*
Теперь можно создавать схемы из оттенков одного цвета!

Используйте /scheme чтобы создать гармоничные цветовые сочетания!
    """
    
    keyboard = [[
        InlineKeyboardButton("🎨 Создать схему", callback_data="main_scheme"),
        InlineKeyboardButton("🔵 Посмотреть круг", callback_data="main_circle")
    ], [
        InlineKeyboardButton("🔄 Показать оттенки", callback_data="main_shades"),
        InlineKeyboardButton("🏠 Меню", callback_data="main_menu")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)

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
    application.add_handler(CommandHandler("shades", show_shades))
    application.add_handler(CommandHandler("scheme", choose_color))
    
    # Регистрируем обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(choose_scheme, pattern="^color_"))
    application.add_handler(CallbackQueryHandler(show_scheme, pattern="^scheme_"))
    application.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^main_"))
    application.add_handler(CallbackQueryHandler(handle_special_commands, pattern="^scheme_color_"))
    application.add_handler(CallbackQueryHandler(handle_new_choice, pattern="^new_"))
    application.add_handler(CallbackQueryHandler(show_color_shades, pattern="^shades_"))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_color_input))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Устанавливаем команды меню при запуске
    application.post_init = post_init
    
    # Запускаем бота
    print("=" * 50)
    print("🎨 Бот 'Расширенный цветовой круг Иттена' запущен!")
    print("=" * 50)
    print("\nДоступные команды в меню:")
    print("/start - Запустить бота")
    print("/menu - Главное меню")
    print("/help - Помощь и инструкции")
    print("/scheme - Создать цветовую схему")
    print("/colors - Список всех цветов (60+)")
    print("/circle - Цветовой круг Иттена")
    print("/palette - Полная палитра (60 цветов)")
    print("/color [цвет] - Информация о цвете")
    print("/shades [цвет] - Показать оттенки цвета")
    print("\n" + "=" * 50)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
