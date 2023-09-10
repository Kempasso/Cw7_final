import requests

from apps.bot.tg.dc import GetUpdatesResponse, SendMessageResponse, SendPhotoResponse


class TgClient:
    """Взаимодействие с API Telegram"""
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str) -> str:
        """Создание url"""
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')
        params = {'offset': offset, 'timeout': timeout}
        response = requests.get(url, params)
        return GetUpdatesResponse(**response.json())

    def send_message(self, chat_id: int, text: str, parse_mode='HTML') -> SendMessageResponse:
        url = self.get_url('sendMessage')
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        response = requests.post(url, data)
        return SendMessageResponse(**response.json())

    def send_photo(self, chat_id: int, photo) -> SendPhotoResponse:
        url = self.get_url('sendPhoto')
        data = {'chat_id': chat_id, 'photo': photo}
        response = requests.post(url, data)
        return SendPhotoResponse(**response.json())
