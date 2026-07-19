import google.generativeai as genai
import base64
import json
from decimal import Decimal
from io import BytesIO
from PIL import Image
import os

from .config import MAX_IMAGE_DIMENSION
from .models import ParsedBill, BillItem


def prepare_image(raw_bytes: bytes) -> str:
    """Resize image to fit within MAX_IMAGE_DIMENSION, return base64 JPEG."""
    img = Image.open(BytesIO(raw_bytes))

    # Resize if longest edge exceeds MAX_IMAGE_DIMENSION
    if max(img.size) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(img.size)
        new_size = tuple(int(d * scale) for d in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Convert to RGB if necessary (for JPEG encoding)
    if img.mode in ("RGBA", "P"):
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = rgb_img

    # Re-encode as JPEG and return base64
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def parse_bill_image(raw_bytes: bytes) -> ParsedBill:
    """Call Google Gemini vision API to extract bill items."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set. Please set your Google Gemini API key.")

    genai.configure(api_key=api_key)
    # Use gemini-3.5-flash which is the latest and supports vision
    model = genai.GenerativeModel("gemini-3.5-flash")
    image_b64 = prepare_image(raw_bytes)

    prompt = """You are a receipt parser. Analyze this image carefully and extract all line items from the restaurant bill/receipt.

Return ONLY a valid JSON object (no markdown, no explanation) in this exact format:
{
  "items": [
    {"name": "item name", "unit_price": 10.00, "quantity": 1},
    {"name": "another item", "unit_price": 5.00, "quantity": 2}
  ],
  "subtotal": 20.00,
  "tax": 2.00,
  "tip": 4.00,
  "total": 26.00
}

IMPORTANT:
- Look for every dish, drink, or food item listed on the receipt
- Extract the item name and unit price (the price per single item)
- Include quantity if multiple units are listed
- Extract subtotal, tax, tip/service charge, and total from the receipt
- If any field is missing from the receipt, use null
- Return ONLY the JSON object, nothing else
- Do not include markdown code blocks
- Do not include any explanatory text

Examples of what to extract:
- "Burger 10.50" → {"name": "Burger", "unit_price": 10.50, "quantity": 1}
- "Fries x2 5.00" → {"name": "Fries", "unit_price": 5.00, "quantity": 2}
- "Coffee 3.25" → {"name": "Coffee", "unit_price": 3.25, "quantity": 1}"""

    try:
        # Send image to Gemini
        image_data = {
            "mime_type": "image/jpeg",
            "data": image_b64,
        }

        response = model.generate_content([prompt, image_data])

        if not response.text:
            raise ValueError("No response from Gemini API.")

        # Parse the JSON response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        data = json.loads(response_text)

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse bill data from Gemini: {e}")
    except Exception as e:
        raise ValueError(f"Gemini API error: {str(e)}")

    # Validate and convert to Decimal for money fields
    try:
        items = [
            BillItem(
                name=item["name"],
                unit_price=Decimal(str(item["unit_price"])),
                quantity=int(item["quantity"]),
            )
            for item in data.get("items", [])
        ]

        return ParsedBill(
            items=items,
            subtotal=Decimal(str(data["subtotal"])) if data.get("subtotal") is not None else None,
            tax=Decimal(str(data["tax"])) if data.get("tax") is not None else None,
            tip=Decimal(str(data["tip"])) if data.get("tip") is not None else None,
            total=Decimal(str(data["total"])) if data.get("total") is not None else None,
        )
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid bill data: {e}")
