import json
import colorsys
from PIL import Image, ImageDraw, ImageFont
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
            # Противоположный цвет (180°)
            opposite_pos = (position + 180) % 360
            schemes = [base_color, self.get_color_at_angle(opposite_pos)]
            
        elif scheme_type == 'triad':
            # Триада (3 цвета через 120°)
            schemes = [
                base_color,
                self.get_color_at_angle((position + 120) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
            
        elif scheme_type == 'analogous':
            # Аналоговая схема (соседние цвета ±30°)
            schemes = [
                self.get_color_at_angle((position - 30) % 360),
                base_color,
                self.get_color_at_angle((position + 30) % 360)
            ]
            
        elif scheme_type == 'square':
            # Квадрат (4 цвета через 90°)
            schemes = [
                base_color,
                self.get_color_at_angle((position + 90) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 270) % 360)
            ]
            
        elif scheme_type == 'split_complementary':
            # Расщепленная комплементарная
            schemes = [
                base_color,
                self.get_color_at_angle((position + 150) % 360),
                self.get_color_at_angle((position + 210) % 360)
            ]
            
        elif scheme_type == 'rectangle':
            # Прямоугольная схема (4 цвета)
            schemes = [
                base_color,
                self.get_color_at_angle((position + 60) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
        
        # Получаем информацию о цветах схемы
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
        """Создать изображение палитры"""
        width = 500
        height = 250
        color_width = width // len(colors)
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Рисуем цветные прямоугольники
        for i, color_info in enumerate(colors):
            x0 = i * color_width
            x1 = (i + 1) * color_width
            draw.rectangle([x0, 0, x1, height - 60], fill=color_info['rgb'])
            
            # Добавляем название цвета и HEX
            color_name = color_info['name'].replace('_', ' ').title()
            hex_code = color_info['hex'].upper()
            rgb = color_info['rgb']
            
            # Центрируем текст
            text_x = x0 + color_width // 2
            
            # Определяем цвет текста (белый или черный) на основе яркости фона
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            text_color = 'black' if brightness > 128 else 'white'
            
            # Используем простой шрифт
            try:
                font = ImageFont.truetype("arial.ttf", 10)
            except:
                font = ImageFont.load_default()
            
            draw.text((text_x - 40, height - 55), color_name[:12], fill=text_color, font=font)
            draw.text((text_x - 25, height - 40), hex_code, fill=text_color, font=font)
            
            # RGB значения
            rgb_text = f"RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}"
            draw.text((text_x - 35, height - 25), rgb_text, fill=text_color, font=font)
        
        # Добавляем название схемы
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 14)
        except:
            font_bold = ImageFont.load_default()
            
        draw.text((10, 10), scheme_name, fill='black', font=font_bold, stroke_width=1, stroke_fill='white')
        
        # Добавляем рамку
        draw.rectangle([0, 0, width-1, height-1], outline='gray', width=2)
        
        # Сохраняем в байты
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=100)
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def create_color_preview(self, color_name):
        """Создать превью одного цвета с информацией"""
        color_info = self.get_color_info(color_name)
        if not color_info:
            return None
        
        width = 400
        height = 300
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Основной цвет
        draw.rectangle([50, 50, width-50, 150], fill=color_info['rgb'])
        
        # Текстовая информация
        color_display = color_name.replace('_', ' ').title()
        hex_code = color_info['hex'].upper()
        rgb = color_info['rgb']
        
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 20)
            font_normal = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_normal = ImageFont.load_default()
        
        # Название цвета
        draw.text((width//2 - 100, 160), f"Цвет: {color_display}", fill='black', font=font_large)
        
        # HEX и RGB
        draw.text((width//2 - 60, 190), f"HEX: {hex_code}", fill='black', font=font_normal)
        draw.text((width//2 - 70, 210), f"RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}", fill='black', font=font_normal)
        
        # Конвертация в HSV
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        hsv_text = f"HSV: {int(h*360)}°, {int(s*100)}%, {int(v*100)}%"
        draw.text((width//2 - 70, 230), hsv_text, fill='black', font=font_normal)
        
        # Рамка
        draw.rectangle([0, 0, width-1, height-1], outline='gray', width=2)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=100)
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def create_itten_circle_image(self):
        """Создать изображение цветового круга Иттена"""
        size = 500
        center = size // 2
        radius = 200
        
        img = Image.new('RGB', (size, size), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()
        
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
            
            # Название цвета
            angle_rad = math.radians(i * 30)
            text_x = center + int((radius + 30) * math.cos(angle_rad))
            text_y = center + int((radius + 30) * math.sin(angle_rad))
            
            color_display = color_name.replace('_', '\n').title()
            draw.text((text_x - 15, text_y - 10), color_display, fill='black', font=font)
        
        # Центральная точка
        draw.ellipse([center-5, center-5, center+5, center+5], fill='gray')
        
        # Заголовок
        try:
            font_title = ImageFont.truetype("arialbd.ttf", 16)
        except:
            font_title = ImageFont.load_default()
        
        draw.text((center - 100, 20), "Цветовой круг Иттена", fill='black', font=font_title)
        
        # Легенда
        legend_y = size - 80
        draw.rectangle([50, legend_y, 70, legend_y+20], fill=self.hex_to_rgb('#FF0000'))
        draw.text((75, legend_y), "Основные цвета (12 секторов)", fill='black', font=font)
        
        # Рамка
        draw.rectangle([0, 0, size-1, size-1], outline='black', width=2)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=100)
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def create_extended_palette_image(self):
        """Создать изображение полной палитры"""
        width = 600
        height = 400
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_small = ImageFont.truetype("arial.ttf", 8)
            font_title = ImageFont.truetype("arialbd.ttf", 16)
        except:
            font_small = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        # Заголовок
        draw.text((width//2 - 100, 10), "Полная палитра цветов", fill='black', font=font_title)
        
        # Отображаем все цвета
        colors_list = list(self.colors.items())
        cols = 6
        rows = (len(colors_list) + cols - 1) // cols
        
        color_width = 90
        color_height = 60
        margin = 10
        
        for idx, (color_name, color_hex) in enumerate(colors_list):
            row = idx // cols
            col = idx % cols
            
            x0 = margin + col * (color_width + margin)
            y0 = 50 + row * (color_height + margin)
            x1 = x0 + color_width
            y1 = y0 + color_height
            
            rgb = self.hex_to_rgb(color_hex)
            draw.rectangle([x0, y0, x1, y1], fill=rgb)
            
            # Определяем цвет текста на основе яркости
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            text_color = 'black' if brightness > 128 else 'white'
            
            # Название цвета
            color_display = color_name.replace('_', ' ').title()
            draw.text((x0 + 5, y0 + 5), color_display, fill=text_color, font=font_small)
            
            # HEX код
            draw.text((x0 + 5, y0 + 20), color_hex.upper(), fill=text_color, font=font_small)
            
            # RGB значения
            rgb_text = f"{rgb[0]},{rgb[1]},{rgb[2]}"
            draw.text((x0 + 5, y0 + 35), rgb_text, fill=text_color, font=font_small)
        
        # Рамка
        draw.rectangle([0, 0, width-1, height-1], outline='gray', width=2)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=100)
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def get_all_colors_list(self):
        """Получить список всех доступных цветов"""
        return list(self.colors.keys())
