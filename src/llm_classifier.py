import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO
from src.config import config
from src.schemas import ModerationResult
from src.utils import clean_json

genai.configure(api_key=config.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)

def classify_text_gemini(text: str) -> ModerationResult:
    prompt = f"""
    You are a strict content moderator.
    Classify the following text into one of: toxic, spam, harassment, safe.
    Give a confidence score (0-1), explain your reasoning, and summarize what it says.
    Respond strictly in JSON with keys: content_type, classification, confidence, reason, description.

    Text: {text}
    """
    response = gemini_model.generate_content(prompt)
    json_text = clean_json(response.text)
    return ModerationResult.model_validate_json(json_text)

def classify_image_gemini(image_source: str) -> ModerationResult:
    if image_source.startswith("http"):
        img_data = requests.get(image_source).content
        image = Image.open(BytesIO(img_data))
    else:
        image = Image.open(image_source)

    prompt = """
    You are a strict content moderator.
    Look at this image and:
    1. Classify it into one of: toxic, spam, harassment, safe.
    2. Give a confidence score (0-1).
    3. Explain your reasoning.
    4. Describe what is shown in the image.
    Respond strictly in JSON with keys: content_type, classification, confidence, reason, description.
    """
    response = gemini_model.generate_content([prompt, image])
    json_text = clean_json(response.text)
    return ModerationResult.model_validate_json(json_text)