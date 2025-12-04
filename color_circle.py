import json
import colorsys
from PIL import Image, ImageDraw
import io
import math

class IttenColorCircle:
    def __init__(self):
        with open('colors.json', 'r', encoding='utf-8') as f:
            self.colors = json.load(f)
        
        # Основные 12 цветов круга Иттена (средние тона)
        self.main_colors = [
            "red", "red_orange", "orange", "yellow_orange", 
            "yellow", "yellow_green", "green", "green_blue",
            "blue", "blue_violet", "violet", "red_violet"
        ]
        
        # Нейтральные цвета
        self.neutral_colors = ["white", "light_gray", "gray", "dark_gray", "black"]
        
        # Цветовые схемы
        self.schemes = {
            'complementary': 'Комплементарная (противоположные цвета)',
            'triad': 'Триада (3 равноудаленных цвета)',
            'analogous': 'Аналоговая (соседние цвета)',
            'square': 'Квадрат (4 цвета через 90°)',
            'split_complementary': 'Расщепленная комплементарная',
            'rectangle': 'Прямоугольная (тетрада)',
            'monochromatic': 'Монохроматическая (оттенки одного цвета)'
        }
        
        # Создаем словарь оттенков для каждого цвета
        self.color_shades = {}
        for color in self.main_colors:
            self.color_shades[color] = [f"{color}_{i}" for i in range(1, 6)]
    
    def get_color_info(self, color_name):
        """Получить информацию о цвете"""
        color_name = color_name.lower()
        if color_name in self.colors:
            return {
                'name': color_name,
                'hex': self.colors[color_name],
                'rgb': self.hex_to_rgb(self.colors[color_name])
            }
        
        # Проверяем, может это оттенок основного цвета
        if '_' in color_name:
            base_color = '_'.join(color_name.split('_')[:-1])
            shade_num = color_name.split('_')[-1]
            if base_color in self.main_colors and shade_num.isdigit():
                actual_name = f"{base_color}_{shade_num}"
                if actual_name in self.colors:
                    return {
                        'name': actual_name,
                        'hex': self.colors[actual_name],
                        'rgb': self.hex_to_rgb(self.colors[actual_name])
                    }
        
        return None
    
    def get_all_shades(self, base_color):
        """Получить все 5 оттенков для основного цвета"""
        if base_color in self.color_shades:
            shades = []
            for shade_name in self.color_shades[base_color]:
                info = self.get_color_info(shade_name)
                if info:
                    shades.append(info)
            return shades
        return []
    
    def hex_to_rgb(self, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb):
        """Конвертация RGB в HEX"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def find_position(self, color_name):
        """Найти позицию цвета в круге"""
        # Если это оттенок, берем основной цвет
        if '_' in color_name and color_name.split('_')[-1].isdigit():
            base_color = '_'.join(color_name.split('_')[:-1])
        else:
            base_color = color_name
        
        if base_color in self.main_colors:
            return self.main_colors.index(base_color) * 30
        return None
    
    def get_scheme(self, base_color, scheme_type):
        """Получить цветовую схему"""
        base_info = self.get_color_info(base_color)
        if not base_info:
            return None
        
        # Определяем основной цвет для расчета схемы
        if '_' in base_color and base_color.split('_')[-1].isdigit():
            main_color = '_'.join(base_color.split('_')[:-1])
        else:
            main_color = base_color
        
        position = self.find_position(main_color)
        if position is None:
            position = 0
        
        schemes = []
        
        if scheme_type == 'complementary':
            # Противоположный цвет (180°)
            opposite_pos = (position + 180) % 360
            schemes = [main_color, self.get_color_at_angle(opposite_pos)]
            
        elif scheme_type == 'triad':
            # Триада (3 цвета через 120°)
            schemes = [
                main_color,
                self.get_color_at_angle((position + 120) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
            
        elif scheme_type == 'analogous':
            # Аналоговая схема (соседние цвета ±30°)
            schemes = [
                self.get_color_at_angle((position - 30) % 360),
                main_color,
                self.get_color_at_angle((position + 30) % 360)
            ]
            
        elif scheme_type == 'square':
            # Квадрат (4 цвета через 90°)
            schemes = [
                main_color,
                self.get_color_at_angle((position + 90) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 270) % 360)
            ]
            
        elif scheme_type == 'split_complementary':
            # Расщепленная комплементарная
            schemes = [
                main_color,
                self.get_color_at_angle((position + 150) % 360),
                self.get_color_at_angle((position + 210) % 360)
            ]
            
        elif scheme_type == 'rectangle':
            # Прямоугольная схема (4 цвета)
            schemes = [
                main_color,
                self.get_color_at_angle((position + 60) % 360),
                self.get_color_at_angle((position + 180) % 360),
                self.get_color_at_angle((position + 240) % 360)
            ]
            
        elif scheme_type == 'monochromatic':
            # Монохроматическая схема - возвращаем оттенки выбранного цвета
            if main_color in self.color_shades:
                return self.get_all_shades(main_color)
            else:
                return [base_info]
        
        # Получаем информацию о цветах схемы
        result = []
        for color in schemes:
            if isinstance(color, str):
                # Используем средний тон (shade=3) для схем
                if color in self.main_colors:
                    info = self.get_color_info(color)
                else:
                    info = self.get_color_info(f"{color}_3")
                if info:
                    result.append(info)
        
        return result
    
    def get_color_at_angle(self, angle):
        """Получить цвет по углу в круге"""
        index = round(angle / 30) % 12
        return self.main_colors[index]
    
    def create_color_palette_image(self, colors, scheme_name):
        """Создать изображение палитры"""
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
    
    def create_shades_palette(self, base_color):
        """Создать палитру оттенков для одного цвета"""
        try:
            shades = self.get_all_shades(base_color)
            if not shades:
                return None
            
            width = 400
            height = 200
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            color_width = width // len(shades)
            
            # Рисуем оттенки
            for i, shade_info in enumerate(shades):
                x0 = i * color_width
                x1 = (i + 1) * color_width
                draw.rectangle([x0, 0, x1, height], fill=shade_info['rgb'])
            
            # Рамка
            draw.rectangle([0, 0, width-1, height-1], outline='black', width=3)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
        except Exception as e:
            print(f"Ошибка создания палитры оттенков: {e}")
            return None
    
    def create_itten_circle_image(self):
        """Создать изображение цветового круга Иттена"""
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
        """Создать изображение полной палитры (60 цветов)"""
        try:
            width = 800
            height = 600
            
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Создаем сетку 12x5 (12 цветов по 5 оттенков)
            cols = 12
            rows = 5
            
            color_width = width // cols
            color_height = height // rows
            
            for col_idx, main_color in enumerate(self.main_colors):
                shades = self.get_all_shades(main_color)
                for row_idx, shade_info in enumerate(shades):
                    x0 = col_idx * color_width
                    y0 = row_idx * color_height
                    x1 = x0 + color_width
                    y1 = y0 + color_height
                    
                    draw.rectangle([x0, y0, x1, y1], fill=shade_info['rgb'])
                    
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
    
    def get_main_colors_list(self):
        """Получить список основных цветов"""
        return self.main_colors
    
    def get_color_group(self, base_color):
        """Получить все цвета из группы (основной цвет + его оттенки)"""
        if base_color in self.main_colors:
            return [base_color] + self.color_shades[base_color]
        elif base_color in self.neutral_colors:
            return [base_color]
        return []
