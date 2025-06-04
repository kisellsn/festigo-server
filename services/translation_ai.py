import requests
import os

from app.config import GEMINI_API_KEY


def translate_with_gemini(prompt_text: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"].strip()

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return ""
    except (KeyError, IndexError) as e:
        print(f"❌ Parsing error: {e}, raw response: {response.text}")
        return ""

def build_translation_prompt(event_id: str, texts: dict) -> str:
    combined = []
    for key, val in texts.items():
        if val:
            combined.append(f"{key}: {val}")
    joined = "\n".join(combined)

    return (
        f"Translate each field value to Ukrainian. "
        f"If a field is written in Latin letters (transliterated Ukrainian), convert it to proper Ukrainian Cyrillic. "
        f"Return the result in the same format: 'field: translated value'. "
        f"Do not add any comments or extra text.\n\n"
        f"{joined}"
    )

import re
from deep_translator import GoogleTranslator
from app.config import city_translation_map, GEMINI_API_KEY
import requests

def replace_cities_in_text(text: str) -> str:
    if not text:
        return text

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


def translate_with_gemini(prompt_text: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        print(f"❌ Gemini request error: {e}")
        return ""
    except (KeyError, IndexError) as e:
        print(f"❌ Gemini parsing error: {e}, raw response: {response.text if 'response' in locals() else 'No response'}")
        return ""

def build_translation_prompt(event_id: str, texts: dict) -> str:
    combined = []
    for key, val in texts.items():
        if val:
            combined.append(f"{key}: {val}")
    joined = "\n".join(combined)

    return (
        f"Translate each field value to Ukrainian. "
        f"If a field is written in Latin letters (transliterated Ukrainian), convert it to proper Ukrainian Cyrillic. "
        f"If a field is already in Ukrainian or written in Cyrillic, leave it unchanged. "
        f"Return the result in the same format: 'field: translated value'. "
        f"Do not add any comments or extra text.\n\n"
        f"{joined}"
    )


def translate_event_fields(event: dict) -> dict:
    fields = {
        "name": str(event.get("name") or ""),
        "description": str(event.get("description") or ""),
        "venue_name": str(event.get("venue", {}).get("name") or ""),
        "city": str(event.get("venue", {}).get("city") or ""),
    }

    prompt = build_translation_prompt(event.get("id", ""), fields)
    translated_text = translate_with_gemini(prompt)

    if not translated_text:
        # Gemini fallback: deep_translator
        print("⚠️ Gemini failed, falling back to deep_translator")
        fallback_result = {}
        for key, val in fields.items():
            if val:
                fallback_result[key] = translate_text(val)
            else:
                fallback_result[key] = ""
        return fallback_result

    lines = translated_text.splitlines()
    result = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            result[key.strip()] = val.strip()

    missing = set(fields.keys()) - set(result.keys())
    if missing:
        print(f"⚠️ Missing keys in Gemini translation response: {missing}")
        for key in missing:
            if fields[key]:
                result[key] = translate_text(fields[key])
            else:
                result[key] = ""

    return result


if __name__ == "__main__":
    # Тестовий приклад
    sample_event = {
        "id": "sample123",
        "name": "Buy tickets to the concert in Lviv",
        "description": "Vsi hotovi do party?",
        "venue": {
            "name": "Docker pub",
            "city": "Kyiv"
        }
    }

    translated = translate_event_fields(sample_event)
    print("\n🌐 Translated fields:")
    for k, v in translated.items():
        print(f"{k}: {v}")

