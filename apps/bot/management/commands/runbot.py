from django.core.management.base import BaseCommand

from apps.bot.management._chat import Chat
from apps.bot.tg.client import TgClient
from todolist.settings import BOT_TOKEN


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.tg_client: TgClient = TgClient(BOT_TOKEN)

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1

                # Создаем экземпляр чата
                chat = Chat(message=item.message)
                chat.set_state(self.tg_client)
                chat.state.run()
                # if item.message.photo:
                #     photo = item.message.photo[-1]
                #     self.tg_client.send_photo(chat_id=item.message.chat.id, photo=photo.file_id)
                # self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text)
