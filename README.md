# 🌐 Kody Browser

**Kody Browser** — это легкий, быстрый и приватный веб-браузер, написанный на Python с использованием движка Chromium (PyQt6 WebEngine). Он создан для тех, кто ценит минимализм, красивый интерфейс и контроль над своей приватностью.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-WebEngine-green?style=flat-square&logo=qt)
![License](https://img.shields.io/badge/License-MIT-orange?style=flat-square)

---

##  Особенности

*   🎨 **Современный интерфейс:** Плавные скругления, минималистичный дизайн и две встроенные темы (Catppuccin Dark и Clean Light).
*   🛡️ **Приватность:** Встроенный базовый блокировщик рекламы и трекеров. Поддержка DNS-over-HTTPS (Cloudflare) для шифрования DNS-запросов.
*   🌍 **Гибкий поиск:** Возможность выбирать поисковую систему (Google, DuckDuckGo, Yandex, Bing) прямо из панели инструментов.
*   ⚙️ **Настройки:** Интуитивное окно настроек для смены темы, поисковика, главной страницы и настройки прокси (SOCKS5).
*   💾 **Сохранение сессий:** Браузер использует дисковый кэш и сохраняет куки, поэтому вам не придется каждый раз заново авторизовываться на сайтах.
*   🚀 **Легковесность:** Никакого Electron и лишних фреймворков — только чистый Python и Qt.

---

Установите зависимости (в Arch Linux):
```bash
sudo pacman -S python-pyqt6 python-pyqt6-webengine
