import json
import colorsys
from PIL import Image, ImageDraw
import io
import math

class IttenColorCircle:
    def __init__(self):
        with open('colors.json', 'r', encoding='utf-8') as f:
            self.colors = json.load(f)
        
        # Основные 12 цветов круга Иттена
        self.main_colors = [
            "red", "orange", "yellow", "yellow_green", 
            "green", "emerald", "cyan", "azure",
            "blue", "violet", "magenta", "crimson"
        ]
        
        # Цветовые схемы
        self.schemes = {
            'complementary': 'Комплементарная (противоположные цвета)',
            'triad': 'Триада (3 равноудаленных цвета)',
            'analogous': 'Аналоговая (соседние цвета)',
            'square': 'Квадрат (4 цвета через 90°)',
            'split_complementary': 'Расщепленная комплементарная',
            'rectangle': 'Прямоугольная (тетрада)'
        }
        
        # Цветовые названия для круга (сокращенные)
        self.color_names = {
            "red": "Красный",
            "orange": "Оранж",
            "yellow": "Желтый",
            "yellow_green": "Желт-зел",
            "green": "Зеленый",
            "emerald": "Изумруд",
            "cyan": "Голубой",
            "azure": "Лазурный",
            "blue": "Синий",
            "violet": "Фиолет",
            "magenta": "Пурпур",
            "crimson": "Малинов",
            "red_orange": "Кр-оранж",
            "orange_yellow": "Ор-желт",
            "yellow_green2": "Желт-зел2",
            "green_emerald": "Зел-изум",
            "emerald_cyan": "Из-голуб",
            "cyan_azure": "Гол-лазур",
            "azure_blue": "Лаз-син",
            "blue_violet": "Син-фиол",
            "violet_magenta": "Фил-пурп",
            "magenta_crimson": "Пурп-мал",
            "crimson_red": "Мал-крас"
        }
    
    def get_color_info(self, color_name):
        """Получить информацию о цвете"""
        color_name = color_name.lower()
        if color_name in self.colors:
            return {
                'name': color_name,
                'hex': self.colors[color_name],
                'rgb': self.hex_to_rgb(self.colors[color_name])
            }
        return None
    
    def hex_to_rgb(self, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb):
        """Конвертация RGB в HEX"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def find_position(self, color_name):
        """Найти позицию цвета в круге"""
        if color_name in self.main_colors:
            return self.main_colors.index(color_name) * 30
        return None
    
    def get_scheme(self, base_color, scheme_type):
        """Получить цветовую схему"""
        base_info = self.get_color_info(base_color)
        if not base_info:
            return None
        
        position = self.find_position(base_color)
        if position is None:
            position = 0
        
        schemes = []
        
        if scheme_type == 'complementary':
            opposite_pos = (position + 180) % 360
            schemes = [base_color, self.get_color_at_angle(opposite_pos)]
            
        elif scheme_type == 'triad':
            schemes = [
                base_color,
                self.get_color_at_angle((position + 120) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
            
        elif scheme_type == 'analogous':
            schemes = [
                self.get_color_at_angle((position - 30) % 360),
                base_color,
                self.get_color_at_angle((position + 30) % 360)
            ]
            
        elif scheme_type == 'square':
            schemes = [
                base_color,
                self.get_color_at_angle((position + 90) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 270) % 360)
            ]
            
        elif scheme_type == 'split_complementary':
            schemes = [
                base_color,
                self.get_color_at_angle((position + 150) % 360),
                self.get_color_at_angle((position + 210) % 360)
            ]
            
        elif scheme_type == 'rectangle':
            schemes = [
                base_color,
                self.get_color_at_angle((position + 60) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
        
        result = []
        for color in schemes:
            if isinstance(color, str):
                info = self.get_color_info(color)
                if info:
                    result.append(info)
        
        return result
    
    def get_color_at_angle(self, angle):
        """Получить цвет по углу в круге"""
        index = round(angle / 30) % 12
        return self.main_colors[index]
    
    def create_color_palette_image(self, colors, scheme_name):
        """Создать изображение палитры (только цвета, без текста)"""
        try:
            width = 500
            height = 200
            color_width = width // len(colors)
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Рисуем цветные прямоугольники
            for i, color_info in enumerate(colors):
                x0 = i * color_width
                x1 = (i + 1) * color_width
                draw.rectangle([x0, 0, x1, height], fill=color_info['rgb'])
            
            # Добавляем рамку
            draw.rectangle([0, 0, width-1, height-1], outline='black', width=3)
            
            # Сохраняем в байты
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
        except Exception as e:
            print(f"Ошибка создания палитры: {e}")
            return None
    
    def create_color_preview(self, color_name):
        """Создать превью одного цвета (только цвет, без текста)"""
        try:
            color_info = self.get_color_info(color_name)
            if not color_info:
                return None
            
            width = 400
            height = 200
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Основной цвет
            draw.rectangle([0, 0, width, height], fill=color_info['rgb'])
            
            # Рамка
            draw.rectangle([0, 0, width-1, height-1], outline='black', width=3)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
        except Exception as e:
            print(f"Ошибка создания превью цвета: {e}")
            return None
    
    def create_itten_circle_image(self):
        """Создать изображение цветового круга Иттена (упрощенный вариант)"""
        try:
            size = 600
            center = size // 2
            radius = 250
            
            img = Image.new('RGB', (size, size), 'white')
            draw = ImageDraw.Draw(img)
            
            # Рисуем цветовой круг
            for i, color_name in enumerate(self.main_colors):
                color_hex = self.colors[color_name]
                rgb = self.hex_to_rgb(color_hex)
                
                # Угол для сектора (12 секторов по 30 градусов)
                start_angle = i * 30 - 15
                end_angle = (i + 1) * 30 - 15
                
                # Рисуем сектор
                draw.pieslice(
                    [center - radius, center - radius, center + radius, center + radius],
                    start_angle, end_angle,
                    fill=rgb, outline='black'
                )
            
            # Внутренний белый круг
            inner_radius = radius // 3
            draw.ellipse(
                [center - inner_radius, center - inner_radius, 
                 center + inner_radius, center + inner_radius],
                fill='white', outline='black'
            )
            
            # Текст в центре
            try:
                # Пытаемся использовать шрифт по умолчанию
                from PIL import ImageFont
                font = ImageFont.load_default()
                text = "ITTEN"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                draw.text(
                    (center - text_width//2, center - text_height//2),
                    text, fill='black', font=font
                )
            except:
                pass  # Пропускаем текст если шрифт не доступен
            
            # Рамка
            draw.rectangle([0, 0, size-1, size-1], outline='black', width=3)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
        except Exception as e:
            print(f"Ошибка создания круга Иттена: {e}")
            return None
    
    def create_extended_palette_image(self):
        """Создать изображение полной палитры (упрощенный вариант)"""
        try:
            width = 600
            height = 400
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Отображаем все цвета в виде сетки
            colors_list = list(self.colors.items())
            cols = 6
            rows = (len(colors_list) + cols - 1) // cols
            
            color_width = width // cols
            color_height = height // rows
            
            for idx, (color_name, color_hex) in enumerate(colors_list):
                row = idx // cols
                col = idx % cols
                
                x0 = col * color_width
                y0 = row * color_height
                x1 = x0 + color_width
                y1 = y0 + color_height
                
                rgb = self.hex_to_rgb(color_hex)
                draw.rectangle([x0, y0, x1, y1], fill=rgb)
                
                # Тонкая рамка для каждого цвета
                draw.rectangle([x0, y0, x1, y1], outline='black', width=1)
            
            # Внешняя рамка
            draw.rectangle([0, 0, width-1, height-1], outline='black', width=3)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
        except Exception as e:
            print(f"Ошибка создания полной палитры: {e}")
            return None
    
    def get_all_colors_list(self):
        """Получить список всех доступных цветов"""
        return list(self.colors.keys())
