
from pydantic import BaseModel, Field


class Chat(BaseModel):  # Представляет информацию о чате.
    id: int
    type: str
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class MessageFrom(BaseModel):  # Представляет информацию об отправителе сообщения
    id: int
    is_bot: bool
    first_name: str
    username: str | None = None
    language_code: str | None = None


class PhotoSize(BaseModel):  # Представляет информацию о фото.
    file_id: str
    file_unique_id: str
    width: int
    height: int


class Message(BaseModel):  # Представляет информацию о сообщении.
    message_id: int
    from_: MessageFrom = Field(alias='from')
    chat: Chat
    date: int
    text: str | None = None
    photo: list[PhotoSize] | None = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Update(BaseModel):  # Представляет информацию об обновлении (новом входящем сообщении или другом событии).
    update_id: int
    message: Message | None = None


class UpdateObj(BaseModel):  # Обертка для обновления, используется при получении обновлений через webhook.
    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):  # Представляет ответ на запрос метода getUpdates.
    ok: bool
    result: list[UpdateObj]


class SendMessageResponse(BaseModel):  # Представляет ответ на запрос метода sendMessage.
    ok: bool
    result: Message = None


class SendPhotoResponse(BaseModel):  # Представляет ответ на запрос метода sendPhoto.
    ok: bool
    result: Message = None
