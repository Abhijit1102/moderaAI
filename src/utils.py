import io
import re
import asyncio
import cloudinary
import cloudinary.uploader
from src.config import config

import hashlib

def hash_string(content: str) -> str:
    """
    Hashes the input string using SHA-256 and returns the hexadecimal digest.

    Args:
        content (str): The input string to hash.

    Returns:
        str: The SHA-256 hash of the input string in hex format.
    """
    # Encode the string to bytes
    content_bytes = content.encode('utf-8')
    # Create a sha256 hash object
    sha256_hash = hashlib.sha256()
    # Update the hash object with the bytes
    sha256_hash.update(content_bytes)
    # Get the hexadecimal digest
    return sha256_hash.hexdigest()


# Configure Cloudinary
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
)

async def upload_image_to_cloudinary(image_bytes: bytes) -> str:
    """
    Upload image bytes asynchronously to Cloudinary and return secure URL.
    """
    try:
        file_obj = io.BytesIO(image_bytes)
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_obj,
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")

def clean_json(text: str) -> str:
    """
    Remove markdown json code fences from Gemini's response.
    """
    cleaned = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
    return cleaned


import hashlib

def hash_string(content: str) -> str:
    """
    Hashes the input string using SHA-256 and returns the hexadecimal digest.

    Args:
        content (str): The input string to hash.

    Returns:
        str: The SHA-256 hash of the input string in hex format.
    """
    content_bytes = content.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content_bytes)
    return sha256_hash.hexdigest()

