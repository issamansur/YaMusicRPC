# For local server
LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 5050
LOCAL_URI = f'http://{LOCAL_HOST}:{LOCAL_PORT}'

# For yandex
YANDEX_CLIENT_ID_OFFICIAL = ''
YANDEX_CLIENT_ID = 'b5e5a1ec43a946808fb0ef04c1ed0877'
YANDEX_REDIRECT_URI = f'{LOCAL_URI}/callback'
YANDEX_AUTH_URL = (
    f'https://oauth.yandex.ru/authorize?'
    f'response_type=token'
    f'&scope=music%3Acontent&scope=music%3Aread&scope=music%3Awrite'
    f'&client_id={YANDEX_CLIENT_ID}'
    f'&redirect_uri={YANDEX_REDIRECT_URI}'
)

# For discord
DISCORD_CLIENT_ID: str = '1370004230688997396'
DISCORD_REDIRECT_URI: str = f"http://127.0.0.1:5000/callback" # ISN'T USED
DISCORD_RPC_SCOPES: list[str] = ["rpc", "rpc.activities.write", "identify"] # ISN'T USED
