# HTR-inclusive-app
Handwritten Text Recognition (HTR) with Multimodal Large Language Model (LLM) on archives of manuscripts and other visual materials of russian writers of the XX century.

# Project "In Plain Language"
**Our mission** is to make cultural heritage accessible and alive, without physical, linguistic or cognitive barriers.
This project is an interactive web application based on Streamlit, providing access to digitized autographs of russian writers of the 20th century. The main goal is to make cultural heritage accessible to a wide range of users, including people with special perception of information, offering tools for analyzing, adapting and voicing texts.

## 🌟 Key Features

* **Browsing archives:** Navigate through the catalog of autographs, grouped by authors, archive types (manuscripts, letters, etc.) and specific works/documents.
* **Display scans:** View high-quality images of manuscript pages.
* **Text recognition (OCR/HTR):** Automatically extract text from manuscript images using multimodal LLM.
* **Adaptation to "Easy Language":** Simplification of the recognized text for better understanding by people with cognitive disabilities (using the [Frequency dictionary of the modern Russian language](http://dict.ruslang.ru/freq.php?act=show&dic=freq_freq&title=%D7%E0%F1%F2%EE%F2%ED%FB%E9%20%F1%EF%E8%F1%EE%EA%20%EB%E5%EC%EC) based on the materials of the National Corpus of the Russian language).
* **TEI:** Generation of XML of the text in accordance with the Text Encoding Initiative standards for researchers.
* **Audio description:** Generation of descriptions of visual features of the manuscript (handwriting, notes, page condition) for blind and visually impaired users.
* **Speech synthesis:** Voice-over of the generated audio description in Russian (male or female) using the VITS model.
* **Search:**
    * Simple search through archive metadata.
    * Advanced search with filtering by author, archive type and keywords in metadata.
* **Inclusive interface:** Ability to switch between standard and inclusive (higher contrast, with enlarged elements) display modes.
* **Data download:** Ability to download page scans (as PDF or ZIP archive with PNG) and all generated texts/markup (TXT, XML).

## 💻 Tools

* **Application framework:** [Streamlit](https://streamlit.io/)
* **Language:** Python 3.12
* **Machine learning / NLP:**
    * [Google AI Studio](https://ai.google.dev/gemini-api/docs): For working with Google LLM's (text recognition, adaptation, TEI, audio description). In our project we used `gemini-2.0-flash-thinking-exp-01-21`
    * [Transformers](https://huggingface.co/models): For TTS (speech synthesis) we used [VITS model](https://huggingface.co/utrobinmv/tts_ru_free_hf_vits_low_multispeaker).
    * [PyTorch](https://pytorch.org/): as a backend for Transformers.
    * [RUAccent](https://github.com/Den4ikAI/ruaccent): For placing stress marks before speech synthesis.
    * Pandas: For working with local csv and xlsx files.
* **Обработка изображений:** 
    * Pillow (PIL)
