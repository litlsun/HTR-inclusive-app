from IPython.display import Markdown
import textwrap
from PIL import Image
import pandas as pd
import os
import google.generativeai as genai


TEI_rules = '''
   
<typeContent> описывает тип текста (письмо, черновик, дневник, открытка, заметки и т.д.).

<textLang> предоставляет информацию о языке/языках, используемых в рукописи.

<title> содержит название для любого вида работы:
Может включать следующие атрибуты: origin (название данного документа), mention (упомянутые названия в тексте документа).

<abbr> (аббревиатура) содержит аббревиатуру любого вида.

<date> содержит дату в любом формате.

<num> (число) содержит число, записанное в любой форме.

<measure> содержит слово или фразу, относящуюся к некоторому количеству объекта, обычно включающую число, единицу и название товара.

<corr> (исправление) содержит правильную форму отрывка, явно ошибочного в тексте копии.

<add> (дополнение) содержит буквы, слова или фразы, вставленные в исходный текст автором, переписчиком или предыдущим аннотатором или корректором.

<del> (удаление) содержит букву, слово или отрывок, удаленные, помеченные как удаленные или иным образом обозначенные как лишние или ложные в тексте копии автором, переписчиком или предыдущим аннотатором или корректором.

<handNotes> содержит один или несколько элементов <handNote>, документирующих различные почерки, идентифицированные в исходных текстах.

<figure> группирует элементы, представляющие или содержащие графическую информацию, такую ​​как иллюстрация, формула или рисунок.

<persName> (личное имя) содержит имя собственное или фразу с именем собственным, относящуюся к человеку, возможно, включая одно или несколько имен человека, фамилий, почетных званий, дополнительных имен и т. д.

<stage> (режиссура сцены) содержит любые виды сценической ремарки в драматическом тексте или фрагменте.

<move> (движение) обозначает фактическое движение одного или нескольких персонажей:
Может включать атрибуты @type характеризует движение, например, как вход или выход;
Может включать атрибуты @where, указывающие направление сценического движения;
Может включать атрибуты @perf (performance), идентифицирует выступление или выступления, в которых произошло это движение, как указано путем указания одного или нескольких элементов <performance>.

<orgName> (название организации) содержит название организации

<address> содержит адрес, например, издателя, организации или отдельного лица.

<gender> указывает гендерную идентичность человека, персоны или персонажа.

<age> указывает возраст человека.

<nationality> содержит неформальное описание настоящей или прошлой национальности или гражданства человека.

<placeName> содержит название места:
Может включать атрибуты @type указывает тип места (страна, город, поселение и т. д.).

<p> выделить абзац
    
         '''


class llm_solution:

    def __init__(self, api_key=None, model='gemini-1.5-flash', temperature=None, top_p=None, pres_penalty=None, freq_penalty=None):  

        from dotenv import load_dotenv

        load_dotenv()
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError("API key is missing. Set GOOGLE_API_KEY in the .env file or pass it explicitly.")
        
        genai.configure(api_key=self.api_key)

        self.available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        self.model = genai.GenerativeModel(model, generation_config={"temperature":temperature, "top_p":top_p, 
                                                                     "presence_penalty":pres_penalty, "frequency_penalty":freq_penalty})
        
        self.model_for_description = genai.GenerativeModel(model_name='gemini-2.0-flash-thinking-exp-01-21', 
                                                           generation_config={"temperature":temperature, "top_p":top_p, 
                                                                              "presence_penalty":pres_penalty, "frequency_penalty":freq_penalty})
        
    # Форматирование ответа LLM в более удобный для чтения вид
    def to_markdown(self, text):
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
        
    # Расшифровка текста рукописи
    def image_to_text(self, img_path):

        self.img = Image.open(img_path)

        prompt = ("Внимательно проанализируй картинку и расшифруй, что на ней написано. "
                  "Далее ещё раз перепроверь, можешь поискать совпадения в интернете, чтобы было проще верифицировать (не нужно мне их выводить). "
                  "Если ты уверен, что на предоставленном скане нет текста, а только какой-то рисунок или фотография - то напиши 'На данном скане текст не обнаружен...' . "
                  "Если ты уверен, что на предоставленном скане есть текст, то в ответе представь только расшифрованный текст с той же структурой, что и на картинке ")

        response = self.model.generate_content([prompt, self.img], stream=True)
        response.resolve()
            
        return response.text.replace("  ", " ")

    # Адаптация расшифрованного текста на ясный язык
    def text_easy_lang(self, original_text):

        vocabulary = pd.read_csv("./data/most_frequent_words.csv", header=None).iloc[:, -1].values
        self.vocabulary_for_promp = [", ".join(vocabulary)]

        prompt = ("Твоя задача адаптировать исходный текст на ясный язык, "
                  "основываясь на следующем словаре из наиболее частотных и простых русских слов. "
                  "Важно, чтобы люди с ограниченными возможностями в восприятии информации и ментальными особенностями поняли его смысл. "
                  "Постарайся использовать слова из этого словаря, но ты можешь использовать и другие слова, если необходимо сформировать связные предложения. "
                  "Также постарайся сохранить структуру и стилистику исходного текста. "
                  f"Словарь: {self.vocabulary_for_promp}. "
                  f"Исходный текст: {original_text} . "
                  "В ответе представь только адаптированный текст.")

        easy_lang = self.model.generate_content([prompt], stream=True)
        easy_lang.resolve()

        return easy_lang.text
    
    # Генерация описания к изображению (тифлокомментирование)
    def generate_description(self, img_path):

        self.img = Image.open(img_path)

        prompt = ("Проведи тифлокомментирование по картинке, опиши её в деталях. В ответе представь только тифлокомментирование")

        description = self.model_for_description.generate_content([prompt, self.img], stream=True)
        description.resolve()
        
        return description.text
    
    # Генерация TEI-разметки на расшифрованном тексте
    def tei_generation(self, original_text, img_path):

        self.img = Image.open(img_path)

        prompt = ("Тебе предоставлен расшифрованный текст рукописи и настоящий скан этой рукописи. "
                  "Для расшифрованного текста представь TEI-разметку. Можешь также опираться на предоставленный скан для дополнительной валидации и информации. "
                  "Мною был определён конкретный набор тегов и правил TEI-разметки, я хочу, чтобы ты использовал только их. " 
                  "Если ты не можешь определить или найти какую-то информацию, удовлетворяющую тегу - то просто игнорируй его. "
                  "Если ты уверен, что на предоставленном скане нет текста, а только какой-то рисунок или фотография - то напиши 'На данном скане текст не обнаружен...'. "
                  f"Вот правила TEI-разметки: {TEI_rules} "
                  f"Расшифрованный текст: {original_text} .")

        tei = self.model.generate_content([prompt, self.img], stream=True)
        tei.resolve()

        return tei.text
