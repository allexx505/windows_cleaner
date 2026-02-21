"""生成电脑清理管家风格图标"""
from PIL import Image, ImageDraw
import os
import math

def generate_cleaner_icon():
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2

    # 渐变背景圆 - 深蓝到浅蓝
    for r in range(118, 0, -1):
        ratio = r / 118
        color = (
            int(30 + 40 * (1 - ratio)),
            int(80 + 70 * (1 - ratio)),
            int(180 + 50 * (1 - ratio)),
            255
        )
        draw.ellipse([center-r-10, center-r-10, center+r+10, center+r+10], fill=color)

    # 电脑显示器
    monitor_border = (80, 80, 90, 255)
    screen_color = (40, 45, 60, 255)

    # 显示器外框
    mx, my = center - 50, center - 45
    mw, mh = 100, 70
    draw.rounded_rectangle([mx, my, mx+mw, my+mh], radius=8, fill=monitor_border)
    draw.rounded_rectangle([mx+4, my+4, mx+mw-4, my+mh-8], radius=4, fill=screen_color)

    # 显示器支架
    stand_color = (100, 100, 110, 255)
    draw.rectangle([center-8, my+mh, center+8, my+mh+12], fill=stand_color)
    draw.ellipse([center-20, my+mh+8, center+20, my+mh+20], fill=stand_color)

    # 屏幕上的清理进度条
    bar_y = my + 25
    bar_x = mx + 15
    bar_w = mw - 30
    bar_h = 8
    draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+bar_h], radius=4, fill=(60, 65, 80, 255))
    
    # 进度条填充 - 绿色渐变
    progress = 0.75
    for i in range(int(bar_w * progress)):
        ratio = i / (bar_w * progress) if bar_w * progress > 0 else 0
        green = (int(50 + 150 * ratio), int(200 + 55 * (1-ratio)), int(80 + 40 * ratio), 255)
        draw.line([(bar_x + 3 + i, bar_y + 2), (bar_x + 3 + i, bar_y + bar_h - 2)], fill=green)

    # 屏幕上的小图标 - 文件清理效果
    icon_y = bar_y + 18
    for i, x in enumerate([bar_x + 8, bar_x + 28, bar_x + 48]):
        file_color = (180, 200, 220, 255) if i < 2 else (120, 130, 150, 255)
        draw.rectangle([x, icon_y, x+12, icon_y+14], fill=file_color)
        draw.polygon([(x+8, icon_y), (x+12, icon_y+4), (x+8, icon_y+4)], fill=screen_color)

    # 扫帚 - 在右下角
    broom_x, broom_y = center + 35, center + 30

    # 扫帚柄 - 倾斜
    handle_color = (139, 90, 43, 255)
    handle_dark = (100, 65, 30, 255)
    for i in range(-3, 4):
        draw.line([
            (broom_x + 15 + i*0.3, broom_y - 40),
            (broom_x - 25 + i*0.3, broom_y + 35)
        ], fill=handle_color if abs(i) < 2 else handle_dark, width=2)

    # 扫帚头刷毛
    broom_head = (255, 200, 80, 255)
    broom_dark = (200, 150, 50, 255)
    for i in range(-12, 13, 2):
        length = 25 - abs(i) * 0.8
        draw.line([
            (broom_x - 28 + i, broom_y + 30),
            (broom_x - 35 + i * 1.2, broom_y + 30 + length)
        ], fill=broom_head if i % 4 == 0 else broom_dark, width=3)

    # 扫帚绑带
    draw.arc([broom_x - 42, broom_y + 25, broom_x - 15, broom_y + 38], 0, 180, fill=(80, 50, 30, 255), width=3)

    # 闪光效果 - 表示清洁
    sparkle_color = (255, 255, 255, 240)
    sparkles = [(center - 60, center - 50), (center + 70, center - 30), (center - 40, center + 60)]
    for sx, sy in sparkles:
        for angle in range(0, 360, 90):
            rad = math.radians(angle)
            length = 8
            draw.line([
                (sx, sy),
                (sx + math.cos(rad) * length, sy + math.sin(rad) * length)
            ], fill=sparkle_color, width=2)
        for angle in range(45, 360, 90):
            rad = math.radians(angle)
            length = 5
            draw.line([
                (sx, sy),
                (sx + math.cos(rad) * length, sy + math.sin(rad) * length)
            ], fill=sparkle_color, width=1)

    # 小闪点
    for sx, sy in [(center - 75, center), (center + 55, center + 50), (center, center - 70)]:
        draw.ellipse([sx-2, sy-2, sx+2, sy+2], fill=(255, 255, 255, 200))

    return img


def main():
    img = generate_cleaner_icon()
    
    # 保存 PNG
    png_path = r'D:\code_lib\windows_cleaner\assets\app_icon.png'
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    img.save(png_path, 'PNG')
    print(f'Created PNG: {png_path}')

    # 创建 ICO
    ico_path = r'D:\code_lib\windows_cleaner\assets\app_icon.ico'
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    icons[0].save(ico_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes], append_images=icons[1:])
    print(f'Created ICO: {ico_path}')


if __name__ == '__main__':
    main()
