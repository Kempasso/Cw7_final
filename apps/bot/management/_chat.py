
from apps.bot.management._state import BaseTgUserState, NewUserState, UnverifiedUserState, VerifiedUserState
from apps.bot.models import TgUser
from apps.bot.tg.client import TgClient


class Chat:
    def __init__(self, message):
        self.message = message
        self.__state: BaseTgUserState | None = None

    @property
    def state(self) -> BaseTgUserState | RuntimeError:
        if self.__state:
            return self.__state
        else:
            raise RuntimeError('''State doesn't exist.''')

    def set_state(self, tg_client: TgClient):
        # Проверка наличия юзера в базе данных
        tg_user, create = TgUser.objects.get_or_create(telegram_chat_id=self.message.chat.id,
                                                       defaults={'telegram_user_ud': self.message.from_.id})
        if create:
            self.__state = NewUserState(tg_user=tg_user, tg_client=tg_client)
        elif not tg_user.user:
            self.__state = UnverifiedUserState(tg_client=tg_client, tg_user=tg_user)
        else:
            self.__state = VerifiedUserState(tg_client=tg_client, tg_user=tg_user, message=self.message)
