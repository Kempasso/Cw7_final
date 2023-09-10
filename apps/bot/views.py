from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bot.serializer import TgUserSerializer
from apps.bot.tg.client import TgClient
from todolist.settings import BOT_TOKEN


class BotVerifyView(generics.UpdateAPIView):
    serializer_class = TgUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs) -> Response:
        serializer: TgUserSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer) -> None:
        tg_user = serializer.save()
        tg_client = TgClient(BOT_TOKEN)
        tg_client.send_message(chat_id=tg_user.telegram_chat_id,
                               text='''Аккаунт успешно привязан!\n
    Доступные команды:\n"/goals" — получить список целей\n"/create" — создать новую цель''')
