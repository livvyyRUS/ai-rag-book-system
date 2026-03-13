import asyncio
import os

# Устанавливаем DATABASE_URL перед импортом database
os.environ['DATABASE_URL'] = 'postgres://admin:password@host.docker.internal:5432/database_pg'

from database import init_db, close_db, add_user, check_user, get_user_by_username

async def test_auth():
    # Инициализация БД
    print("Инициализация БД...")
    await init_db()
    
    # Проверка подключения
    print("\nПроверка таблицы пользователей...")
    from models import User
    all_users = await User.all()
    print(f"Всего пользователей в БД: {len(all_users)}")
    for user in all_users:
        print(f"  - {user.username} (active: {user.is_active})")
    
    # Тест проверки пользователя
    test_username = "admin"
    test_password = "admin123"
    
    print(f"\nПроверка логина/пароля для '{test_username}'...")
    user = await get_user_by_username(test_username)
    if user:
        print(f"Пользователь найден: {user.username}, id={user.id}, active={user.is_active}")
        print(f"password_hash: {user.password_hash[:20]}...")
        is_valid = await check_user(test_username, test_password)
        print(f"Проверка пароля '{test_password}': {'УСПЕШНА' if is_valid else 'НЕУСПЕШНА'}")
    else:
        print(f"Пользователь '{test_username}' НЕ найден в БД!")
        print("\nПопробуем создать тестового пользователя...")
        created = await add_user(test_username, test_password)
        if created:
            print(f"Пользователь '{test_username}' успешно создан!")
            # Проверим ещё раз
            user = await get_user_by_username(test_username)
            print(f"Теперь пользователь найден: {user.username}, id={user.id}")
            is_valid = await check_user(test_username, test_password)
            print(f"Проверка пароля: {'УСПЕШНА' if is_valid else 'НЕУСПЕШНА'}")
        else:
            print(f"Не удалось создать пользователя '{test_username}'")
    
    await close_db()
    print("\nГотово!")

if __name__ == "__main__":
    asyncio.run(test_auth())
