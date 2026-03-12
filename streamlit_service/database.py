import os
from tortoise import Tortoise
from models import User


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    db_url = os.getenv(
        "DATABASE_URL",
        "postgres://user:password@localhost:5432/streamlit_db"
    )
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["models"]},
        _enable_global_fallback=True,
    )
    await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения к базе данных"""
    await Tortoise.close_connections()


async def add_user(username: str, password: str, email: str = None) -> bool:
    """
    Добавление нового пользователя

    Returns:
        True если пользователь успешно создан, False если пользователь уже существует
    """
    exists = await User.filter(username=username).exists()
    if exists:
        return False

    user = User(username=username, email=email, is_active=True)
    user.set_password(password)
    await user.save()
    return True


async def check_user(username: str, password: str) -> bool:
    """
    Проверка учетных данных пользователя

    Returns:
        True если логин/пароль верны и пользователь активен, False иначе
    """
    user = await User.filter(username=username).first()
    if not user or not user.is_active:
        return False
    return user.check_password(password)


async def get_user_by_username(username: str) -> User | None:
    """Получение пользователя по имени"""
    return await User.filter(username=username).first()


async def get_user_by_id(user_id: int) -> User | None:
    """Получение пользователя по ID"""
    return await User.filter(id=user_id).first()


async def update_user_password(user: User, new_password: str) -> None:
    """Обновление пароля пользователя"""
    user.set_password(new_password)
    await user.save()


async def deactivate_user(user: User) -> None:
    """Деактивация пользователя"""
    user.is_active = False
    await user.save()


async def get_all_users() -> list[User]:
    """Получение всех пользователей"""
    return await User.all()
