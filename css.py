# Пользовательские стили для обычного режима
NORMAL_CSS = """
<style>
/* Общий фон страницы */
body {
    background-color: #F5F5DC; /* светло-бежевый */
    color: #4A3C30; /* темно-бежевый */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Заголовки */
h1, h2, h3, h4 {
    color: #6F4E37; /* коричневый акцент */
}

/* Блоки/карточки */
.block {
    background-color: #FFF8DC; /* светло-пергаментный */
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

/* Кнопки */
.stButton>button {
    background-color: #6F4E37; /* коричневый */
    color: #FFF8DC; /* светло-пергаментный */
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #4A3C30; /* темно-бежевый */
}

/* Кнопки загрузки */
.stDownloadButton>button {
    font-size: 1.2rem;
    padding: 1rem 2rem;
    background-color: #6F4E37;
    color: #FFF8DC;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
.stDownloadButton>button:hover {
    background-color: #4A3C30;
}

/* Прочие элементы (selectbox, textinput и т.д.) */
.stSelectbox, .stTextInput, .stDownloadButton {
    font-size: 1rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Текстовые поля */
.stTextArea textarea {
    background-color: #FFF8DC; /* светло-пергаментный */
    color: #4A3C30; /* темно-бежевый */
    border: 1px solid #D2B48C; /* рамка под пергамент */
    border-radius: 5px;
    padding: 10px;
}

/* Стили для изображений, на которые можно нажать */
.clickable-image {
    cursor: pointer;
    transition: transform 0.2s; /* Плавное изменение при наведении */
    display: inline-block; /* Добавлено для корректного отображения */
}

.clickable-image:hover {
    transform: scale(1.05); /* Увеличение при наведении */
}
</style>
"""
