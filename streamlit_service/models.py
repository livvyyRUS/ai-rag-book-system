from tortoise import fields, models
import bcrypt


class User(models.Model):
    """Модель пользователя для авторизации"""

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username

    def set_password(self, password: str) -> None:
        """Хеширует и устанавливает пароль"""
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Проверяет пароль с хешем"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self) -> dict:
        """Возвращает словарь с данными пользователя (без пароля)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
