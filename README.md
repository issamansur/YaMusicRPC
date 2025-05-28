![Лицензия](https://img.shields.io/badge/Лицензия-MIT-blue)
![Совместимость с Python](https://img.shields.io/badge/Python-3.8--3.13-blue)
![Версия библиотеки](https://img.shields.io/badge/pip-1.1.1-blue)
[![PyPi downloads](https://img.shields.io/pypi/dm/yamusicrpc.svg)](https://pypi.org/project/yamusicrpc/)
[![Build and Release YaMusicRPC App](https://github.com/issamansur/YaMusicRPC/actions/workflows/build-app.yml/badge.svg)](https://github.com/issamansur/YaMusicRPC/actions/workflows/build-app.yml)

# <p align="center"> YaMusicRPC (+App) </p>

**YaMusicRPC** — это Python-библиотека для интеграции статуса прослушивания Яндекс.Музыки в Discord Rich Presence.

Помимо этого на основе библиотеки разработано кроссплатформенное приложение **YaMusicRPC**,
которое позволит стримить в Discord прослушиваемую музыку в Яндекс Музыке.

## Возможности

- Авторизация через OAuth Яндекс.Музыки
- Получение информации о текущем треке
- Отправка статуса прослушивания в Discord через IPC
- Асинхронная работа

## Установка

```sh
git clone https://github.com/issamansur/YaMusicRPC.git
cd YaMusicRPC
python3 -m pip install -r ./yamusicrpc/requirements.txt
```

## Быстрый старт

Пример использования находится в [`examples/main.py`](examples/main.py):

```py
import asyncio
from yamusicrpc import ActivityManager

async def main():
    activity_manager = ActivityManager()
    await activity_manager.start()

asyncio.run(main())
```

## Как это работает

1. При запуске открывается браузер для авторизации в Яндекс.Музыке.
2. После успешной авторизации токен автоматически сохраняется.
3. Библиотека отслеживает текущий трек и отправляет информацию в Discord Rich Presence.

## Требования

- Python 3.9+
- Discord Desktop Client (должен быть запущен)
- Аккаунт Яндекс.Музыки

## Лицензия

**YaMusicRPC** распространяется под лицензией MIT. За более детальной информацией о лицензии обратитесь к файлу LICENSE.

## Авторы

**YaMusicRPC** разрабатывается **@issamansur** или/и командой 'EDEXADE, inc.'

## Благодарности

### Помощь в разработке

- [Группа по Яндекс](https://t.me/yandex_music_api) - за поддержку и быстрые ответы
- [Артём Б.](https://artembay.ru) — за помощь со способом редиректа через Yandex API;
- [Мипоха](https://mipoh.ru) — за помощь со способом получения текущего трека;
- [Артём М.](https://github.com/TheKing-OfTime) - за помощь со способом отображения обложки трека и кнопок в активности;

### Помощь в тестировании

- [Александр П.]()
