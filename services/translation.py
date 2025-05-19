from googletrans import Translator

async def translate_text(text: str, dest_lang: str = "uk") -> str:
    if not text:
        return ""
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest=dest_lang)
            return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text
