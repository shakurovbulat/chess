from PIL import Image

def remove_white_pixels(file_name):
    # Открываем изображение
    image = Image.open(file_name)
    image = image.convert("RGBA")  # Преобразуем изображение в формат с альфа-каналом

    # Получаем данные пикселей
    pixels = image.load()

    # Проходим по каждому пикселю
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            # Проверяем, является ли пиксель белым
            if r == 255 and g == 255 and b == 255:
                # Устанавливаем альфа-канал в 0 (прозрачный)
                pixels[x, y] = (r, g, b, 0)

    # Сохраняем измененное изображение под тем же именем
    image.save(file_name)

# Пример использования функции
remove_white_pixels("chess_progect/close.png")
