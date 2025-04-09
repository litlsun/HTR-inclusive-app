import os
import io
import zipfile
import re
import pandas as pd
from PIL import Image

import streamlit as st
from css import NORMAL_CSS  

from llm import llm_solution, TEI_rules
from speech_generator import generate_speech

# Выбор модели
model_name = "gemini-2.0-flash-thinking-exp-01-21"


# -----------------------
# Первичная настройка страницы 
# -----------------------
st.set_page_config(page_title="Проект «Понятным языком»",
                   page_icon="📜",
                   layout="centered")


# -----------------------
# Вспомогательные функции 
# -----------------------
# Путь к архиву
DATASET_DIR = "./data/Authors_Manusripts"

# Базовая проверка существования директории
if not os.path.exists(DATASET_DIR):
    try:
        from googledrivedownloader import download_file_from_google_drive as gdd
        gdd(file_id='1ZW4TRvfuRm8heBQACvqTkWnz5LTx6Oba',  # Позволяет установить небольшой образец архива из Гугл Диска
            dest_path='./data/Authors_Manusripts.zip',
            unzip=True)
        print(f"INFO: Directory {DATASET_DIR} created.") 
    except OSError as e:
        st.error(f"Не удалось создать директорию {DATASET_DIR}: {e}")
        st.stop()  

def list_authors():
    return sorted([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])

def list_archive_types(author):
    path = os.path.join(DATASET_DIR, author)

    if not os.path.isdir(path):
        return []
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

def list_archives(author, archive_type):
    path = os.path.join(DATASET_DIR, author, archive_type)
    # Проверка существования пути 
    if not os.path.isdir(path):
        return []
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

def load_metadata(author, archive_type, archive_title):
    meta_path = os.path.join(DATASET_DIR, author, archive_type, archive_title, "meta_data.xlsx")
    if os.path.exists(meta_path):
        try:
            return pd.read_excel(meta_path, index_col=0)
        except Exception: 
             return None
    return None

def get_image_paths(author, archive_type, archive_title):
    folder = os.path.join(DATASET_DIR, author, archive_type, archive_title)
    # проверка существования папки
    if not os.path.isdir(folder):
        return []
    try:
        images = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.png')])
        return images
    except Exception: 
        return []

def download_images_zip(author, archive_type, archive_title):
    folder = os.path.join(DATASET_DIR, author, archive_type, archive_title)
    buffer = io.BytesIO()
    # проверка существования папки
    if not os.path.isdir(folder):
        buffer.seek(0)
        return buffer
    try:
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for file in os.listdir(folder):
                if file.lower().endswith('.png'):
                    file_path = os.path.join(folder, file)
                    # Проверка, что это файл, перед добавлением
                    if os.path.isfile(file_path):
                        zip_file.write(file_path, arcname=file)
    except Exception:
         buffer = io.BytesIO() # очистка буфера при ошибке
    buffer.seek(0)
    return buffer

def download_pdf(author, archive_type, archive_title):
    images_paths = get_image_paths(author, archive_type, archive_title)
    images = []
    for img_path in images_paths:
        if os.path.isfile(img_path):
            try:
                with Image.open(img_path) as img:
                    images.append(img.convert("RGB"))
            except Exception:
                continue
    
    buffer = io.BytesIO()
    if images:
        try: 
            images[0].save(buffer, save_all=True, append_images=images[1:], format="PDF")
        except Exception:
             buffer = io.BytesIO() 
    buffer.seek(0)
    return buffer

def download_metadata(author, archive_type, archive_title):
    meta_path = os.path.join(DATASET_DIR, author, archive_type, archive_title, "meta_data.xlsx")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "rb") as f:
                buffer = io.BytesIO(f.read())
            buffer.seek(0)
            return buffer
        except Exception:
            return None
    return None

# Callback функция для навигации из поиска 
def select_archive_callback(author, archive_type, archive):
    """Обновляет session_state для выбора архива."""
    st.session_state["selected_archive"] = {
        "author": author,
        "archive_type": archive_type,
        "archive": archive
    }
    # Убрать выбор изображения, если он был, при переходе к новому архиву
    if "selected_image" in st.session_state:
        st.session_state.pop("selected_image")


# -----------------------
# Основное приложение
# -----------------------
def main_app():
    # Задать стиль
    st.markdown(NORMAL_CSS, unsafe_allow_html=True)

# -----------------------
# Страница отдельного скана автографа 
# -----------------------
    if "selected_image" in st.session_state:
        details = st.session_state["selected_image"]
        # .get для безопасного доступа к ключам словаря
        image_index = details.get("image_index", -1)
        image_path = details.get("image_path")

        # Проверка, что путь к изображению существует
        if not image_path or not os.path.isfile(image_path):
            st.error("Ошибка: Путь к изображению не найден.")
            # кнопка для возврата, если изображение потеряно
            if st.button("⬅️ Вернуться к архиву"):
                 if "selected_image" in st.session_state: st.session_state.pop("selected_image")
                 st.rerun()
            return # Выход из main_app, если изображение не доступно

        st.header(f"Страница {image_index + 1}")
        try:
            st.image(image_path, use_container_width=True, caption=f"Страница {image_index + 1}")
        except Exception as e:
             st.error(f"Не удалось отобразить изображение: {e}")
             return # Выход, если ошибка отображения

        st.subheader("Доступность")
        # Инициализация LLM 
        try:
             llm_sol = llm_solution(model=model_name) 
        except NameError:
             st.error("Класс llm_solution не найден. Проверьте импорт.")
             llm_sol = None
        except Exception as e:
             st.error(f"Ошибка инициализации LLM: {e}")
             llm_sol = None

        # Инициализация ключей в session_state, если их нет 
        if "ocr_text_results" not in st.session_state: st.session_state["ocr_text_results"] = {}
        if "easy_text_results" not in st.session_state: st.session_state["easy_text_results"] = {}
        if "tei_text_results" not in st.session_state: st.session_state["tei_text_results"] = {}
        if "desc_text_results" not in st.session_state: st.session_state["desc_text_results"] = {}

        image_key = image_path # Ключ для результатов

        # Функция для скачивания текста 
        def download_text(text, filename, mime, label="📄", help_text="Скачать текст"):
             # Проверка типа и кодирование
             try:
                 data = text.encode('utf-8') if isinstance(text, str) else bytes(text)
             except Exception as e:
                 st.error(f"Ошибка кодирования текста для скачивания: {e}")
                 data = b"" # Пустые байты в случае ошибки

             # уникальный ключ для download_button
             download_key = f"download_{filename.replace('.', '_').replace(os.sep, '_')}"
             st.download_button(label=label,
                                data=data,
                                file_name=filename,
                                mime=mime,
                                key=download_key,
                                help=help_text)

        # Кнопки и логика LLM 
        if llm_sol:
            if st.button("Расшифровать текст"):
                with st.spinner("Обработка изображения, подождите..."):
                    try:
                        ocr_text = llm_sol.image_to_text(image_path)
                        st.session_state["ocr_text_results"][image_key] = ocr_text
                    except Exception as e:
                        st.error(f"Ошибка OCR: {e}")


            if image_key in st.session_state["ocr_text_results"]:
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.text_area("Расшифрованный текст", value=st.session_state["ocr_text_results"][image_key], height=350, key=f"ocr_{image_key}")
                with col2:
                    # байты в функцию скачивания
                    try:
                        ocr_bytes = st.session_state["ocr_text_results"][image_key].encode('utf-8')
                    except:
                        ocr_bytes = b""
                    download_text(ocr_bytes, f"ocr_{os.path.basename(image_key)}.txt", "text/plain")

                # Кнопки зависят от наличия OCR текста
                if st.button("Адаптировать на ясный язык"):
                    with st.spinner("Адаптация текста, подождите..."):
                        try:
                            easy_text = llm_sol.text_easy_lang(st.session_state["ocr_text_results"][image_key])
                            st.session_state["easy_text_results"][image_key] = easy_text
                        except Exception as e:
                            st.error(f"Ошибка адаптации: {e}")


                if image_key in st.session_state["easy_text_results"]:
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.text_area("Текст на ясном языке", value=st.session_state["easy_text_results"][image_key].replace("**", ""), height=350, key=f"easy_{image_key}")
                    with col2:
                         try:
                             easy_bytes = st.session_state["easy_text_results"][image_key].encode('utf-8')
                         except:
                             easy_bytes = b""
                         download_text(easy_bytes, f"easy_{os.path.basename(image_key)}.txt", "text/plain")

                if st.button("Сгенерировать TEI-разметку"):
                     with st.spinner("Генерация TEI-разметки, подождите..."):
                         try:
                             tei_text = llm_sol.tei_generation(st.session_state["ocr_text_results"][image_key], image_path)
                             st.session_state["tei_text_results"][image_key] = tei_text
                         except Exception as e:
                             st.error(f"Ошибка генерации TEI: {e}")


                if image_key in st.session_state["tei_text_results"]:
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.code(st.session_state["tei_text_results"][image_key], language="xml")
                    with col2:
                         try:
                             tei_bytes = st.session_state["tei_text_results"][image_key].encode('utf-8')
                         except:
                             tei_bytes = b""
                         download_text(tei_bytes, f"tei_{os.path.basename(image_key)}.xml", "text/xml", label="&lt;/&gt;", help_text="Скачать xml")

            if st.button("Тифлокомментирование"):
                 with st.spinner("Генерация описания, подождите..."):
                     try:
                        desc_text = llm_sol.generate_description(image_path)
                        # Очистка 
                        cleaned_desc = re.sub(" +", " ", re.sub(r"\*", "", desc_text)).strip() 
                        st.session_state["desc_text_results"][image_key] = cleaned_desc
                     except Exception as e:
                         st.error(f"Ошибка тифлокомментирования: {e}")

            if image_key in st.session_state["desc_text_results"]:
                desc_text = st.session_state["desc_text_results"][image_key]

                # состояние для аудио
                if f"speech_audio_{image_key}" not in st.session_state:
                    st.session_state[f"speech_audio_{image_key}"] = None
                if f"show_audio_player_{image_key}" not in st.session_state:
                    st.session_state[f"show_audio_player_{image_key}"] = False

                col1, col2 = st.columns([9, 1])
                with col1:
                    st.text_area("Тифлокомментирование", value=desc_text, height=350, key=f"desc_{image_key}")
                with col2:
                    try:
                         desc_bytes = desc_text.encode('utf-8')
                    except:
                         desc_bytes = b""
                    download_text(desc_bytes, f"desc_{os.path.basename(image_key)}.txt", "text/plain")

                    if st.button("🔊", key=f"speak_desc_{image_key}", help="Озвучить тифлокомментарий"):
                        if desc_text:
                            with st.spinner(""):
                                try:
                                    speech_output, sampling_rate = generate_speech(desc_text)
                                    st.session_state[f"speech_audio_{image_key}"] = (speech_output, sampling_rate)
                                    st.session_state[f"show_audio_player_{image_key}"] = True # Показать плеер
                                    st.rerun() 
                                except ImportError as e:
                                    st.error(f"Ошибка импорта при генерации речи: {e}. Убедитесь, что все зависимости установлены.")
                                except Exception as e:
                                    st.error(f"Ошибка генерации речи: {e}")
                                    st.session_state[f"speech_audio_{image_key}"] = None
                                    st.session_state[f"show_audio_player_{image_key}"] = False
                        else:
                            st.warning("Нет текста для озвучивания.")

                # аудиоплеер под колонками, если аудио было сгенерировано
                if st.session_state[f"show_audio_player_{image_key}"]:
                    audio_data = st.session_state.get(f"speech_audio_{image_key}")
                    if audio_data is not None:
                        speech_output, sampling_rate = audio_data
                        st.audio(speech_output, sample_rate=sampling_rate, format='audio/wav')
                    else:

                        st.warning("Аудио было запрошено, но данные отсутствуют.")
                        st.session_state[f"show_audio_player_{image_key}"] = False 

        if st.button("⬅️ Вернуться к архиву"):
            st.session_state.pop("selected_image")
            st.rerun()

# -----------------------
# Страница отдельного архива (автографа) 
# -----------------------
    elif "selected_archive" in st.session_state:
        details = st.session_state["selected_archive"]
        author = details.get("author", "N/A")
        archive_type = details.get("archive_type", "N/A")
        archive = details.get("archive", "N/A")

        st.header(f"{author} - {archive_type} - {archive}")

        # кнопка возврата к общему списку/поиску 
        if st.button("⬅️ Вернуться к выбору архива", key="back_to_main_from_archive"):
             st.session_state.pop("selected_archive")
             # Очистка изображения
             if "selected_image" in st.session_state:
                 st.session_state.pop("selected_image")
             st.rerun()

        meta = load_metadata(author, archive_type, archive)
        if meta is not None:
            st.subheader("Метаданные")
            st.dataframe(meta) 
        else:
            st.write("Метаданные отсутствуют.") 

        st.subheader("Скан автографа")
        images = get_image_paths(author, archive_type, archive)
        if images:
            num_columns = 4 
            cols = st.columns(num_columns)
            for i, img_path in enumerate(images):
                 with cols[i % num_columns]:
                     # Проверка существования файла перед использованием
                     if os.path.isfile(img_path):
                         try:
                            st.image(img_path, width=500) 
                         except Exception as e:
                             st.warning(f"Ошибка загр. стр. {i+1}: {e}")
                         button_key = f"page_{archive.replace(' ','_')}_{i}"
                         if st.button(f"Страница {i+1}", key=button_key, help="Нажмите, чтобы открыть скан"):
                             st.session_state["selected_image"] = {
                                 "author": author,
                                 "archive_type": archive_type,
                                 "archive": archive,
                                 "image_index": i,
                                 "image_path": img_path
                             }
                             st.rerun()
                     else:
                          st.warning(f"Стр. {i+1} не найдена.")
        else:
            st.info("Нет изображений в данном архиве.") 

        st.subheader("Скачать автограф")
        # st.container для группировки кнопок
        download_container = st.container()
        with download_container:
            # CSS grid для равномерного распределения кнопок
            st.markdown(
                """
                <style>
                .download-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr); /* 3 колонки */
                    gap: 1rem; /* Расстояние между кнопками */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div class='download-grid'>", unsafe_allow_html=True)

            pdf_buffer = download_pdf(author, archive_type, archive)
            st.download_button("Скачать PDF 📑", data=pdf_buffer, file_name=f"{archive}.pdf", mime="application/pdf", key=f"pdf_{archive}")

            zip_buffer = download_images_zip(author, archive_type, archive)
            st.download_button("Скачать PNG архив 🎞️", data=zip_buffer, file_name=f"{archive}.zip", mime="application/zip", key=f"zip_{archive}")

            meta_buffer = download_metadata(author, archive_type, archive)
            if meta_buffer:
                st.download_button("Скачать метаданные 🗂️", data=meta_buffer, file_name=f"meta_{archive}.csv", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"meta_{archive}")
            else:
                st.write("Метаданные отсутствуют.")

            st.markdown("</div>", unsafe_allow_html=True)

    # Если ни архив, ни изображение не выбраны, показываем меню 
    else:
        st.title("Архив автографов писателей 20 века")
        st.write("Просматривайте автографы, читайте их расшифровку, адаптацию на ясный язык и тифлокомментарий. "
                 "Для исследователей также доступна TEI-разметка и метаданные.")

        # Меню навигации в боковой панели 
        if 'menu_selection' not in st.session_state:
            st.session_state.menu_selection = "Домой" # Значение по умолчанию

        menu_options = ["Домой", "Поиск", "О проекте"]
        try:
            # индекс на основе сохраненного значения
            current_index = menu_options.index(st.session_state.menu_selection)
        except ValueError:
            current_index = 0 # По умолчанию "Домой", если значение некорректно
            st.session_state.menu_selection = "Домой"

        menu = st.sidebar.radio("Навигация",
                                menu_options,
                                index=current_index,
                                key="sidebar_navigation") # ключ для стабильности
        # Обновление сохраненного значения после выбора пользователя
        st.session_state.menu_selection = menu

# -----------------------
# Раздел «Домой»: навигация по каталогам 
# -----------------------
        if menu == "Домой":
            st.header("Навигация по архивам")
            authors = list_authors()
            if not authors:
                st.error("Не найдено ни одного автора в каталоге.")
            else:
                selected_author = st.selectbox("Выберите автора", authors)
                if selected_author: # Проверка, что автор выбран
                    archive_types = list_archive_types(selected_author)
                    if not archive_types:
                        st.warning("Нет архивов для данного автора.")
                    else:
                        selected_archive_type = st.selectbox("Выберите тип архива", archive_types)
                        if selected_archive_type: # Проверка, что тип выбран
                            archives = list_archives(selected_author, selected_archive_type)
                            if not archives:
                                st.warning("Нет архивов для данного типа.")
                            else:
                                selected_archive = st.selectbox("Выберите архив", archives)
                                if selected_archive: # Проверка, что архив выбран

                                    st.button("Открыть архив",
                                              key="open_archive_home_button", # Добавлен ключ
                                              on_click=select_archive_callback,
                                              args=(selected_author, selected_archive_type, selected_archive))

# -----------------------
# Раздел «Поиск»: простой и расширенный поиск 
# -----------------------
        elif menu == "Поиск":
            st.header("Поиск архивов")
            tab1, tab2 = st.tabs(["Простой поиск", "Расширенный поиск"])

            with tab1:
                st.subheader("Простой поиск")
                search_query = st.text_input("Введите поисковый запрос (по тексту метаданных)")
                if st.button("Найти (простой поиск)"):
                    results = []
                    # проверка на пустой запрос
                    if search_query:
                        with st.spinner("Выполняется поиск..."): 
                            for author in list_authors():
                                for arch_type in list_archive_types(author):
                                    for archive in list_archives(author, arch_type):
                                        meta = load_metadata(author, arch_type, archive)
                                        if meta is not None:
                                            try: # обработка ошибок на случай не-строковых данных
                                                meta_str = meta.to_string().lower()
                                                if search_query.lower() in meta_str:
                                                    results.append({"author": author,
                                                                    "archive_type": arch_type,
                                                                    "archive": archive})
                                            except AttributeError:
                                                continue
                    # Логика отображения результатов 
                    if results:
                        st.success(f"Найдено {len(results)} результатов:")
                        for idx, res in enumerate(results):
                             button_label = f"{res['author']} - {res['archive_type']} - {res['archive']}"
                             button_key = f"res_{res['author']}_{res['archive_type']}_{res['archive']}_{idx}"
                             st.button(button_label,
                                       key=button_key,
                                       on_click=select_archive_callback,
                                       args=(res['author'], res['archive_type'], res['archive']))

                    elif search_query: 
                         st.info("По вашему запросу ничего не найдено.")
                    else: # Если запрос пустой
                         st.info("Введите запрос для поиска.")


            with tab2:
                st.subheader("Расширенный поиск")
                # Логика выбора автора/типа/года 
                selected_author_ext = st.selectbox("Автор", [""] + list_authors(), key="adv_author")
                if selected_author_ext:
                    archive_types_ext = list_archive_types(selected_author_ext)
                else:
                    archive_types_ext = []
                selected_archive_type_ext = st.selectbox("Тип архива", [""] + archive_types_ext, key="adv_archive_type")
                selected_year_ext = st.text_input("Поиск по метаданным (дата, название, тип документа и т.д.)", key="adv_year")

                if st.button("Найти (расширенный поиск)"):
                    results = []
                    with st.spinner("Выполняется поиск..."): 
                        authors_list = [selected_author_ext] if selected_author_ext else list_authors()
                        for author in authors_list:
                            arch_types = [selected_archive_type_ext] if selected_archive_type_ext else list_archive_types(author)
                            # Пропуск, если выбранный тип не существует для автора
                            if selected_archive_type_ext and not arch_types:
                                continue
                            for arch_type in arch_types:
                                for archive in list_archives(author, arch_type):
                                    meta = load_metadata(author, arch_type, archive)
                                    if meta is not None:
                                         # Условие поиска по году 
                                        cond = True
                                        if selected_year_ext:
                                             try: # Добавлена обработка ошибок
                                                 meta_str = meta.to_string().lower()
                                                 if selected_year_ext.lower() not in meta_str: # Поиск подстроки года
                                                     cond = False
                                             except AttributeError:
                                                 cond = False 

                                        if cond:
                                            results.append({"author": author,
                                                            "archive_type": arch_type,
                                                            "archive": archive})
                    # Логика отображения результатов 
                    if results:
                        st.success(f"Найдено {len(results)} результатов:")
                        for idx, res in enumerate(results): # idx для уникальности ключа
                            button_label = f"{res['author']} / {res['archive_type']} / {res['archive']}"
                            button_key = f"adv_{res['author']}_{res['archive_type']}_{res['archive']}_{idx}"
                            st.button(
                                button_label,
                                key=button_key,
                                on_click=select_archive_callback,
                                args=(res['author'], res['archive_type'], res['archive'])
                             )
   
                    else:

                        st.info("По вашему запросу ничего не найдено.")

# -----------------------
# Раздел «О проекте» 
# -----------------------
        elif menu == "О проекте":
            st.header("О проекте")
            st.markdown("""
                Данное веб-приложение разработано для обеспечения доступа к оцифрованным автографам
                русскоязычных писателей XX века.

                **Ключевые особенности:**
                * Просмотр сканов рукописей.
                * Автоматическая расшифровка текста (OCR).
                * Адаптация текста на "Ясный язык".
                * Генерация TEI-разметки для исследователей.
                * Тифлокомментирование для описания визуальных деталей.
                * Синтез речи для озвучивания описаний.
                * Поиск по архивам и метаданным.

                **Наша миссия** — сделать культурное наследие доступным и живым,
                преодолевая физические, языковые и когнитивные барьеры, и предоставить удобные
                инструменты как для обычных читателей, так и для исследователей.
            """)
            st.info("Для навигации по архивам используйте раздел 'Домой' или 'Поиск'.")
            
            # Сноска в разделе "О проекте" 
            st.markdown(
                """
                <div style="font-size: 0.9rem; margin-top: 2rem; color: #6F4E37;">
                    <p>
                        <span style="font-weight: bold;">*</span> 
                        <span style="font-style: italic;">Ясный язык</span> — это система, которая делает тексты простыми и понятными для всех. Он использует короткие предложения, избегает сложных терминов и помогает людям с дислексией, нейроотличиями или с базовым знанием языка легко усваивать информацию.
                    </p>
                    <p>
                        <span style="font-weight: bold;">*</span> 
                        <span style="font-style: italic;">Тифлокомментарий</span> - это целевая информация, специально подготовленная для слепых (слабовидящих) для замещения (или дополнения) визуальной информации, которую воспринимает зрячий и которая из-за слепоты недоступна (или малодоступна) слепым (слабовидящим).
                    </p>
                </div>
                """,
                unsafe_allow_html=True
                )


if __name__ == "__main__":
    main_app()
