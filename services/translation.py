# from googletrans import Translator
#
# async def translate_text(text: str, dest_lang: str = "uk") -> str:
#     if not text:
#         return ""
#     try:
#         async with Translator() as translator:
#             result = await translator.translate(text, dest=dest_lang)
#             return result.text
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text
import re

from deep_translator import GoogleTranslator
from app.config import city_translation_map


def replace_cities_in_text(text: str) -> str:
    if not text:
        return text

    # Створюємо регулярний вираз, що матиме всі ключі
    pattern = r'\b(' + '|'.join(re.escape(city) for city in city_translation_map.keys()) + r')\b'

    def replacer(match):
        city_en = match.group(0)
        return translate_city(city_en)

    return re.sub(pattern, replacer, text)

def translate_text(text: str) -> str:
    try:
        translated = GoogleTranslator(source="en", target="uk").translate(text)
        return replace_cities_in_text(translated)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_city(city: str) -> str:
    return city_translation_map.get(city.strip(), city)



if __name__ == "__main__":
    print(translate_text("Find the price and buy a ticket to the event - Mysterium, Vinnytsia"))


