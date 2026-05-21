@echo off
echo Creating FieldNode PWA icons...

REM Create minimal PNG files (1x1 transparent pixel)
echo iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQIHWNgAAIAAAUAAY27m/MAAAAASUVORK5CYII= > temp.b64

certutil -decode temp.b64 icon-72x72.png >nul 2>&1
certutil -decode temp.b64 icon-96x96.png >nul 2>&1
certutil -decode temp.b64 icon-128x128.png >nul 2>&1
certutil -decode temp.b64 icon-144x144.png >nul 2>&1
certutil -decode temp.b64 icon-152x152.png >nul 2>&1
certutil -decode temp.b64 icon-192x192.png >nul 2>&1
certutil -decode temp.b64 icon-384x384.png >nul 2>&1
certutil -decode temp.b64 icon-512x512.png >nul 2>&1

del temp.b64

echo Icons created successfully!
echo Note: These are placeholder icons. For production, replace with proper FieldNode branded icons.