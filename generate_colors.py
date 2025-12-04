import json
import colorsys
import math

def generate_60_colors():
    """Генерация 60 цветов: 12 основных цветов по 5 оттенков каждый"""
    
    # Основные 12 цветов круга Иттена (Hue значения в градусах)
    base_hues = {
        'red': 0,
        'red_orange': 30,
        'orange': 60,
        'yellow_orange': 90,
        'yellow': 120,
        'yellow_green': 150,
        'green': 180,
        'green_blue': 210,
        'blue': 240,
        'blue_violet': 270,
        'violet': 300,
        'red_violet': 330
    }
    
    colors = {}
    
    # Создаем 5 оттенков для каждого цвета
    for color_name, hue in base_hues.items():
        for shade in range(1, 6):
            # Вычисляем параметры для HSV
            h = hue / 360.0  # Hue (0-1)
            s = 1.0  # Saturation (максимальная)
            v = 1.0 - (shade - 1) * 0.2  # Value (яркость) от 1.0 до 0.2
            
            # Конвертируем HSV в RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            
            # Конвертируем в HEX
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(r * 255),
                int(g * 255),
                int(b * 255)
            ).upper()
            
            # Добавляем в словарь
            key = f"{color_name}_{shade}"
            colors[key] = hex_color
            
            # Для удобства добавляем основные цвета (shade=3 как средний тон)
            if shade == 3:
                colors[color_name] = hex_color
    
    # Добавляем черный, белый и серые оттенки
    gray_colors = {
        'white': '#FFFFFF',
        'light_gray': '#CCCCCC',
        'gray': '#888888',
        'dark_gray': '#444444',
        'black': '#000000'
    }
    colors.update(gray_colors)
    
    return colors

def save_colors_to_file(filename='colors.json'):
    """Сохранение цветов в JSON файл"""
    colors = generate_60_colors()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(colors, f, indent=2, ensure_ascii=False)
    
    print(f"Создано {len(colors)} цветов в файле {filename}")
    
    # Вывод статистики
    print("\nОсновные группы цветов:")
    color_groups = {}
    for key in colors:
        if '_' in key and key.split('_')[-1].isdigit():
            base_name = '_'.join(key.split('_')[:-1])
            if base_name not in color_groups:
                color_groups[base_name] = []
            color_groups[base_name].append(key)
    
    for group, shades in color_groups.items():
        print(f"  {group}: {len(shades)} оттенков")

if __name__ == '__main__':
    save_colors_to_file()