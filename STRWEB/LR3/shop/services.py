import logging

import requests

logger = logging.getLogger(__name__)


def fetch_pet_api_highlights():
    result = {
        "cat_fact": "Кошки спят большую часть дня, чтобы экономить энергию.",
        "dog_image": "",
        "source_note": "Показаны резервные данные: внешние API временно недоступны.",
    }
    try:
        cat_response = requests.get("https://catfact.ninja/fact", timeout=3)
        cat_response.raise_for_status()
        result["cat_fact"] = cat_response.json().get("fact", result["cat_fact"])
        result["source_note"] = "Данные получены из Cat Facts API и Dog CEO API."
    except requests.RequestException as exc:
        logger.warning("Cat Facts API failed: %s", exc)

    try:
        dog_response = requests.get("https://dog.ceo/api/breeds/image/random", timeout=3)
        dog_response.raise_for_status()
        result["dog_image"] = dog_response.json().get("message", "")
        result["source_note"] = "Данные получены из Cat Facts API и Dog CEO API."
    except requests.RequestException as exc:
        logger.warning("Dog CEO API failed: %s", exc)

    return result
