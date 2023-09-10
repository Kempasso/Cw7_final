from typing import Optional

from apps.bot.models import TgUser
from apps.bot.tg.client import TgClient
from apps.bot.tg.dc import Message
from apps.goals.models import Goal, GoalCategory
from todolist.settings import env

URL_SIGNUP = env('URL_SIGNUP')
URL_LOGIN = env('URL_LOGIN')


class BaseTgUserState:

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        self.tg_user = tg_user
        self.tg_client = tg_client
        self._text: str | None = None

    def get_verification_code(self) -> str:
        """Получение кода верификации"""
        return self.tg_user.set_verification_code()

    def send_message(self, text: Optional[str]) -> None:
        """Отправка сообщения пользователю"""
        self.tg_client.send_message(
            chat_id=int(self.tg_user.telegram_chat_id),
            text=text, parse_mode='HTML'
        )

    def run(self) -> None:
        self.send_message(text=self._text)


class NewUserState(BaseTgUserState):
    """Класс юзера впервые активировавшего бота"""
    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)
        self._text = f'Добро пожаловать в TaskTG бот\n\nЕсли вы не зарегистрированы, пройдите регистрацию ' \
                     f'<a href="{URL_SIGNUP}">по ссылке</a>' \
                     f'\nили войдите в аккаунт <a href="{URL_LOGIN}">по ссылке</a>' \
                     f' \n и подтвердите, его. ' \
                     f'Для подтверждения необходимо ввести код: \n{self.get_verification_code()}'


class UnverifiedUserState(BaseTgUserState):
    """Класс юзера активировавшего бота, но не прошедшего верификацию"""
    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)
        self._text = 'Если вы не зарегистрированы, пройдите регистрацию ' \
                     f'<a href="{URL_SIGNUP}">по ссылке</a>' \
                     f'\nили войдите в аккаунт <a href="{URL_LOGIN}">по ссылке</a>' \
                     f' \n и подтвердите, его. ' \
                     f'Для подтверждения необходимо ввести код: \n{self.get_verification_code()}'


class VerifiedUserState(BaseTgUserState):
    """Класс юзера прошедшего верификацию"""
    user_state_create: bool = False  # Состояние пользователя, создает ли он Цель
    category_for_create_goal: GoalCategory | None = None  # Категория в которой будет создаваться Цель

    def __init__(self, tg_user: TgUser, tg_client: TgClient, message: Message):
        self.message = message
        super().__init__(tg_user, tg_client)

    def run(self):
        if self.message.text.startswith('/'):
            self._command_execution()
        elif VerifiedUserState.user_state_create:
            self._create_goal()
        else:
            text = 'Команда должна начинаться с "/"'
            self._message_execution(text)

    def _command_execution(self):
        """Выбор действия в зависимости от полученной команды"""
        user_id = self.tg_user.user_id
        list_categories = list(GoalCategory.objects.select_related('user').filter(board__participants__user_id=user_id,
                                                                                  is_deleted=False))
        match self.message.text:
            case '/goals':
                self._get_goals()
            case '/create':
                self._choices_category()
            case '/cancel':
                VerifiedUserState.user_state_create = False
            case value if value in [f'/{cat.title}' for cat in list_categories]:
                self._get_data_from_category(value)
            case _:
                self._message_execution()

    def _get_data_from_category(self, mes_text: str):
        """Получение данных выбранной категории для создания цели"""
        VerifiedUserState.category_for_create_goal = GoalCategory.objects.select_related('user').filter(
            title=mes_text[1:], is_deleted=False).first()
        VerifiedUserState.user_state_create = True
        self.send_message(text='Введите название цели\nДля отмены введите /cancel')

    def _create_goal(self):
        """Создание новой цели"""
        category = VerifiedUserState.category_for_create_goal
        Goal.objects.create(user_id=self.tg_user.user.id,
                            category_id=category.id,
                            title=self.message.text)
        self.tg_client.send_message(self.message.chat.id, text=f'Вы создали цель - {self.message.text}\n в категории -'
                                                               f' {category.title}')
        VerifiedUserState.user_state_create = False

    def _message_execution(self, text: str | None = None):
        """Вывод сообщения пользователю"""
        self.tg_client.send_message(self.message.chat.id, text='Не известная команда')
        self.tg_client.send_message(self.message.chat.id, text=text)
        self.tg_client.send_message(self.message.chat.id,
                                    text='Доступные команды:\n'
                                         '\n/goals — получить список целей\n/create — создать новую цель')

    def _get_goals(self):
        """Получение целей пользователя"""
        user_id = self.tg_user.user_id
        list_goals = list(Goal.objects.select_related('user').filter(user_id=user_id,
                                                                     category__is_deleted=False).exclude(
            status=Goal.Status.archived).values_list('title', flat=True))
        if list_goals:
            self.tg_client.send_message(self.message.chat.id, text='\n\n'.join(list_goals))
        else:
            self.tg_client.send_message(self.message.chat.id, text='У вас нет созданных целей')

    def _choices_category(self):
        """Выбор категории из списка"""
        user_id = self.tg_user.user_id
        list_category = list(GoalCategory.objects.select_related('user').filter(board__participants__user_id=user_id,
                                                                                is_deleted=False))
        categories = [f'/{cat.title}' for cat in list_category]
        if list_category:
            self.tg_client.send_message(self.message.chat.id, text='Выберете категорию для создания цели')
            self.tg_client.send_message(self.message.chat.id, text='\n\n'.join(categories))
        else:
            self.tg_client.send_message(self.message.chat.id, text='У вас нет категорий для создания целей')
