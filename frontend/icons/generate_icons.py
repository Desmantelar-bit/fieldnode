import base64

# Simple 1x1 green pixel PNG (will be scaled by browsers)
green_pixel_png = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)

sizes = [72, 96, 128, 144, 152, 192, 384, 512]

for size in sizes:
    with open(f'icon-{size}x{size}.png', 'wb') as f:
        f.write(green_pixel_png)
    print(f'Created icon-{size}x{size}.png')