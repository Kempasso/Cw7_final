import os

from django.db import models

from apps.core.models import User


class TgUser(models.Model):
    telegram_chat_id: int = models.PositiveIntegerField()
    telegram_user_ud: int = models.CharField(max_length=250)
    verification_code: str = models.CharField(max_length=250, null=True, blank=True)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def __gen_code() -> str:
        return os.urandom(5).hex()

    def set_verification_code(self) -> str:
        self.verification_code = self.__gen_code()
        self.save(update_fields=('verification_code',))
        return self.verification_code
