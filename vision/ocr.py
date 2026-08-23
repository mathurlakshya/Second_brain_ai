import easyocr

# Load OCR model ONCE when the application starts.
# Do NOT create this inside extract_text().
reader = easyocr.Reader(
    ["en"],
    gpu=False,
    verbose=False
)


def extract_text(image_path):
    try:
        result = reader.readtext(
            image_path,

            # Faster recognition
            detail=0,
            decoder="greedy",

            # Reduce the amount of image processing
            canvas_size=1280,
            mag_ratio=1.0,

            # CPU-friendly settings
            batch_size=4,
            workers=0,

            # Ignore extremely tiny text
            min_size=15,

            # Detection thresholds
            text_threshold=0.6,
            low_text=0.3,
            link_threshold=0.4,

            # Don't perform paragraph grouping here
            paragraph=False
        )

        if not result:
            return ""

        return "\n".join(
            text.strip()
            for text in result
            if text and text.strip()
        )

    except Exception as e:
        print(f"⚠️ OCR error: {type(e).__name__}: {e}")
        return ""
