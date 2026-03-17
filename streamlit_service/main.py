import streamlit as st
import asyncio
from database import init_db, close_db, add_user, check_user, get_user_by_username
from jwt_tool import JWTPayload, encode_jwt, decode_jwt
from rag_client import RAGClient
import jwt as jwt_lib
from minio_client import get_bucket_name, create_bucket_if_not_exists, upload_file, list_files, delete_file

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


def check_user_sync(username: str, password: str) -> bool:
    """Синхронная обёртка для check_user"""
    return run_async(check_user(username, password))


def validate_token(jwt_token: str) -> bool:
    """Проверка валидности JWT токена"""
    try:
        decode_jwt(jwt_token)
        return True
    except (jwt_lib.ExpiredSignatureError, jwt_lib.InvalidTokenError):
        return False


def save_session_to_query_params(jwt_token: str, username: str, user_id: str):
    """Сохранение сессии в query params"""
    st.query_params["jwt_token"] = jwt_token
    st.query_params["username"] = username
    st.query_params["user_id"] = user_id


def load_session_from_query_params() -> bool:
    """Загрузка сессии из query params"""
    jwt_token = st.query_params.get("jwt_token", "")
    username = st.query_params.get("username", "")
    user_id = st.query_params.get("user_id", "")
    
    if jwt_token and username and user_id and validate_token(jwt_token):
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user_id
        st.session_state["jwt_token"] = jwt_token
        return True
    return False


def logout():
    """Выход пользователя из системы"""
    for key in ["authenticated", "username", "user_id", "jwt_token", "messages"]:
        if key in st.session_state:
            del st.session_state[key]
    # Очищаем query params
    for key in ["jwt_token", "username", "user_id"]:
        if key in st.query_params:
            del st.query_params[key]


def login_form():
    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")
        if submitted:
            user = run_async(get_user_by_username(username))
            if user is not None and check_user_sync(username, password):
                # Генерируем JWT токен с user_id в формате bucket name
                user_id = f"user-{username.replace('_', '-').lower()}"
                jwt_token = encode_jwt(payload=JWTPayload(user_id=user_id))
                # Сохраняем в сессии и query params для сохранения при перезагрузке
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["user_id"] = user_id
                st.session_state["jwt_token"] = jwt_token
                save_session_to_query_params(jwt_token, username, user_id)
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


def manage_files_page():
    """Страница управления загруженными файлами"""
    st.title("Управление файлами")
    st.write("Просмотр и удаление загруженных файлов")

    username = st.session_state["username"]
    bucket_name = get_bucket_name(username)

    try:
        # Получаем список файлов
        files = list_files(bucket_name)
        
        if not files:
            st.info("У вас пока нет загруженных файлов")
        else:
            st.write(f"**Всего файлов:** {len(files)}")
            
            # Отображаем файлы в виде таблицы
            for file_name in files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {file_name}")
                with col2:
                    if st.button("🗑️ Удалить", key=f"delete_{file_name}"):
                        try:
                            delete_file(bucket_name, file_name)
                            st.success(f"Файл '{file_name}' удалён")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка при удалении: {e}")
                st.divider()
                
    except Exception as e:
        st.error(f"Ошибка при получении списка файлов: {e}")


def upload_files_page():
    st.title("Загрузка файлов")
    st.write("Загрузите файлы для обработки в RAG систему")

    username = st.session_state["username"]
    bucket_name = get_bucket_name(username)

    # Создаем клиент RAG с user_id из сессии (согласован с именем бакета)
    rag_client = RAGClient(
        jwt_token=st.session_state["jwt_token"],
        user_id=st.session_state["user_id"]
    )

    # Загрузка файлов
    uploaded_files = st.file_uploader(
        "Выберите файлы для загрузки",
        type=["pdf", "txt", "docx", "md"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"Выбрано файлов: {len(uploaded_files)}")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")

    if st.button("Загрузить и обработать файлы"):
        if not uploaded_files:
            st.warning("Сначала выберите файлы")
        else:
            try:
                with st.spinner("Обработка файлов..."):
                    # Создаем бакет для пользователя
                    create_bucket_if_not_exists(bucket_name)
                    
                    # Загружаем файлы в Minio
                    for file in uploaded_files:
                        upload_file(bucket_name, file.name, file.getvalue())
                    
                    # Генерируем Chroma DB
                    result = run_async(rag_client.generate_chroma_db())
                    st.success(f"Файлы обработаны! Статус: {result.status}")
            except Exception as e:
                st.error(f"Ошибка при обработке файлов: {e}")


def chat_page():
    st.title("Чат с RAG ботом")
    st.write("Задавайте вопросы по загруженным документам")

    username = st.session_state["username"]

    # Создаем клиент RAG с user_id из сессии (согласован с именем бакета)
    rag_client = RAGClient(
        jwt_token=st.session_state["jwt_token"],
        user_id=st.session_state["user_id"]
    )

    # Инициализация истории чата
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Отображение истории чата
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Поле ввода сообщения
    if prompt := st.chat_input("Введите ваш вопрос..."):
        # Добавляем сообщение пользователя
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Получаем ответ от бота
        with st.chat_message("assistant"):
            with st.spinner("Печатает..."):
                try:
                    result = run_async(rag_client.chat(prompt))
                    response = result.text
                    st.write(response)
                    st.session_state["messages"].append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Ошибка при получении ответа: {e}")
                    st.session_state["messages"].append({"role": "assistant", "content": "Извините, произошла ошибка при обработке вашего запроса."})

    # Кнопка очистки истории
    if st.button("Очистить историю чата"):
        st.session_state["messages"] = []
        st.rerun()


def main_app():
    # Проверка валидности токена
    if not validate_token(st.session_state["jwt_token"]):
        st.warning("Сессия истекла. Пожалуйста, войдите снова.")
        logout()
        st.rerun()

    # Боковая панель навигации
    with st.sidebar:
        st.write(f"Пользователь: **{st.session_state['username']}**")
        page = st.radio(
            "Навигация",
            ["Загрузка файлов", "Управление файлами", "Чат с ботом"],
            index=0
        )
        st.divider()
        if st.button("Выйти"):
            logout()
            st.rerun()

    # Отображение выбранной страницы
    if page == "Загрузка файлов":
        upload_files_page()
    elif page == "Управление файлами":
        manage_files_page()
    else:
        chat_page()


def main():
    # Попытка восстановить сессию из query params при перезагрузке страницы
    if "authenticated" not in st.session_state:
        if load_session_from_query_params():
            main_app()
            return
    
    if "authenticated" not in st.session_state:
        auth_screen()
    else:
        # Проверка валидности токена перед входом в приложение
        if "jwt_token" in st.session_state and not validate_token(st.session_state["jwt_token"]):
            st.warning("Сессия истекла. Пожалуйста, войдите снова.")
            logout()
            auth_screen()
        else:
            main_app()


if __name__ == "__main__":
    main()
