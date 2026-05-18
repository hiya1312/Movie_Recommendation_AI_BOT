# vision.py
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes, OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from config import VISION_KEY, VISION_ENDPOINT

client = ComputerVisionClient(
    VISION_ENDPOINT,
    CognitiveServicesCredentials(VISION_KEY)
)

FEATURES = [
    VisualFeatureTypes.description,
    VisualFeatureTypes.tags,
    VisualFeatureTypes.objects,
    VisualFeatureTypes.brands,
    VisualFeatureTypes.color,
    VisualFeatureTypes.categories,
]

def _extract_text_read_api(image_path: str) -> str:
    """Use Azure Read API (deep-learning OCR) — handles stylized/artistic poster fonts."""
    with open(image_path, "rb") as f:
        response = client.read_in_stream(f, raw=True)

    operation_id = response.headers["Operation-Location"].split("/")[-1]

    # Poll until complete (usually 1-2 seconds)
    for _ in range(10):
        read_result = client.get_read_result(operation_id)
        if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(0.5)

    words = []
    if read_result.status == OperationStatusCodes.succeeded:
        for page in read_result.analyze_result.read_results:
            for line in page.lines:
                words.append(line.text)
    return " ".join(words).strip()

def analyse_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        result = client.analyze_image_in_stream(f, visual_features=FEATURES)

    parts = []

    # Read API OCR — deep learning, handles stylized movie poster fonts accurately
    ocr_text = _extract_text_read_api(image_path)
    if ocr_text:
        parts.append(f"Text visible in image: {ocr_text}")

    # Best caption
    if result.description and result.description.captions:
        captions = sorted(result.description.captions, key=lambda c: c.confidence, reverse=True)
        parts.append("Scene: " + captions[0].text)

    # Brands (e.g. Marvel, DC, Disney)
    if result.brands:
        brand_names = [b.name for b in result.brands if b.confidence > 0.5]
        if brand_names:
            parts.append("Brands/franchises detected: " + ", ".join(brand_names))

    # Objects in the image
    if result.objects:
        obj_names = list({o.object_property for o in result.objects})
        if obj_names:
            parts.append("Objects: " + ", ".join(obj_names))

    # Tags sorted by confidence
    if result.tags:
        top_tags = [t.name for t in sorted(result.tags, key=lambda t: t.confidence, reverse=True)[:15]]
        parts.append("Visual themes/tags: " + ", ".join(top_tags))

    # Dominant colors and mood
    if result.color:
        colors = []
        if result.color.dominant_color_foreground:
            colors.append(result.color.dominant_color_foreground)
        if result.color.dominant_color_background:
            colors.append(result.color.dominant_color_background)
        if result.color.dominant_colors:
            colors.extend(result.color.dominant_colors)
        unique_colors = list(dict.fromkeys(colors))
        if unique_colors:
            parts.append("Dominant colors: " + ", ".join(unique_colors))
        if result.color.is_bw_img:
            parts.append("Style: black and white")

    # Categories
    if result.categories:
        cat_names = [c.name for c in result.categories if c.score > 0.3]
        if cat_names:
            parts.append("Categories: " + ", ".join(cat_names))

    return " | ".join(parts) if parts else "an interesting scene"
