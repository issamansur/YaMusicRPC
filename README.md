![Лицензия](https://img.shields.io/badge/Лицензия-MIT-blue)

# <p align="center"> YaMusicRPC </p>

**YaMusicRPC** — это Python-библиотека для интеграции статуса прослушивания Яндекс.Музыки в Discord Rich Presence.

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

- Python 3.8+
- Discord Desktop Client (должен быть запущен)
- Аккаунт Яндекс.Музыки

## Скрипты

- `utils/install_requirements.sh` — установка зависимостей
- `utils/starter.sh` — запуск примера

## Лицензия

**YaMusicRPC** распространяется под лицензией MIT. За более детальной информацией о лицензии обратитесь к файлу LICENSE.

## Авторы

**YaMusicRPC** разрабатывается **@issamansur** или/и командой 'EDEXADE, inc.'

## Благодарности

- [Группа по Яндекс](https://t.me/yandex_music_api) - за поддержку и быстрые ответы
- [Артём Б.](https://artembay.ru) — за помощь со способом редиректа через Yandex API;
- [Мипоха](https://mipoh.ru) — за помощь со способом получения текущего трека;
- [Артём М.](https://github.com/TheKing-OfTime) - за помощь со способом отображения обложки трека и кнопок в активности;