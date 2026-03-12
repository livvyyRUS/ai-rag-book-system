import streamlit as st
import asyncio
from database import init_db, close_db, add_user, check_user, get_user_by_username

# Инициализация БД при старте приложения
@st.cache_resource
def initialize_database():
    """Инициализация БД один раз при первом запуске"""
    asyncio.run(init_db())
    return True

_ = initialize_database()


def run_async(coro):
    """Запуск асинхронной функции"""
    return asyncio.run(coro)


def login_form():
    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")
        if submitted:
            if run_async(check_user(username, password)):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Вход выполнен успешно!")
                st.rerun()
            else:
                st.error("Неверное имя пользователя или пароль")


def register_form():
    with st.form("register_form"):
        new_username = st.text_input("Новое имя пользователя")
        new_password = st.text_input("Новый пароль", type="password")
        confirm_password = st.text_input("Подтвердите пароль", type="password")
        submitted = st.form_submit_button("Зарегистрироваться")
        if submitted:
            if new_password != confirm_password:
                st.error("Пароли не совпадают")
            elif len(new_password) < 6:
                st.error("Пароль должен быть не менее 6 символов")
            else:
                if run_async(add_user(new_username, new_password)):
                    st.success("Регистрация успешна! Теперь вы можете войти.")
                else:
                    st.error("Пользователь с таким именем уже существует")


def auth_screen():
    st.title("Добро пожаловать!")
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    with tab1:
        login_form()
    with tab2:
        register_form()


def main_app():
    st.title(f"Приложение для {st.session_state['username']}")
    st.write("Здесь находится защищённый контент.")

    # Пример получения пользователя из БД
    user = run_async(get_user_by_username(st.session_state["username"]))
    if user:
        st.write(f"**Email:** {user.email or 'Не указан'}")
        st.write(f"**Дата регистрации:** {user.created_at}")

    if st.button("Выйти"):
        del st.session_state["authenticated"]
        del st.session_state["username"]
        st.rerun()


def main():
    if "authenticated" not in st.session_state:
        auth_screen()
    else:
        main_app()


if __name__ == "__main__":
    main()
