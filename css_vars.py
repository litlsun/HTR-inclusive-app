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


# Пользовательские стили для инклюзивного режима
ACCESSIBLE_CSS = """
<style>
/* Высокая контрастность */
body {
    background-color: #FFFFFF;
    color: #000000;
    font-family: Arial, sans-serif;
}
/* Кнопки */
.stButton>button {
    background-color: #2D2A26; /* Измененный цвет кнопок */
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 600;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #47423E; /* Измененный цвет при наведении */
}

/* Кнопки загрузки */
.stDownloadButton>button {
    font-size: 18px;
    padding: 1rem 2rem;
    background-color: #2D2A26; /* Измененный цвет кнопок */
    color: #FFFFFF;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    cursor: pointer;
}
.stDownloadButton>button:hover {
    background-color: #47423E; /* Измененный цвет при наведении */
}

/* Увеличенный размер шрифта для прочих элементов */
.stSelectbox, .stTextInput, .stDownloadButton {
    font-size: 18px;
    font-family: Arial, sans-serif;
}
.css-1d391kg, .css-1lcbmhc, .css-18e3th9, .css-1vbd788 {
    font-size: 18px;
}

/* Текстовые поля */
.stTextArea textarea {
    background-color: #faebd7; /* пергаментный цвет */
    color: #000000;
    border: 2px solid #d2b48c; /* рамка под пергамент */
    border-radius: 5px;
    padding: 10px;
}
</style>
"""