from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = TgUser
        fields = ('telegram_chat_id', 'telegram_user_ud', 'user', 'verification_code')
        read_only_fields = ('telegram_chat_id', 'telegram_user_ud', 'user')

    def validate_verification_code(self, value: str) -> str:
        try:
            self.instance = TgUser.objects.get(verification_code=value)
        except TgUser.DoesNotExist:
            raise ValidationError('Code is incorrect')
        return value

    def update(self, instance: dict, validated_data: dict):
        self.instance.user = self.context['request'].user
        return super().update(instance, validated_data)
