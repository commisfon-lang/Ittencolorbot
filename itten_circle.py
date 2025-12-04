import json
import colorsys
from PIL import Image, ImageDraw
import io

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
        width = 400
        height = 200
        color_width = width // len(colors)
        
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Рисуем цветные прямоугольники
        for i, color_info in enumerate(colors):
            x0 = i * color_width
            x1 = (i + 1) * color_width
            draw.rectangle([x0, 0, x1, height - 40], fill=color_info['rgb'])
            
            # Добавляем название цвета и HEX
            color_name = color_info['name'].replace('_', ' ').title()
            hex_code = color_info['hex'].upper()
            
            # Центрируем текст
            text_x = x0 + color_width // 2
            draw.text((text_x - 30, height - 35), color_name[:10], fill='black')
            draw.text((text_x - 30, height - 20), hex_code, fill='black')
        
        # Добавляем название схемы
        draw.text((10, 10), scheme_name, fill='black', stroke_width=1, stroke_fill='white')
        
        # Сохраняем в байты
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def get_all_colors_list(self):
        """Получить список всех доступных цветов"""
        return list(self.colors.keys())