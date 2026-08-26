from PIL import Image
import easyocr

# Load ONCE
reader = easyocr.Reader(
    ["en"],
    gpu=False,
    verbose=False
)


def extract_text(image_path):

    try:
        # Resize large screenshots before OCR.
        # This significantly reduces CPU processing time.
        image = Image.open(image_path)

        max_width = 1600

        if image.width > max_width:

            ratio = max_width / image.width

            new_size = (
                max_width,
                int(image.height * ratio)
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

            resized_path = image_path + "_ocr.png"

            image.save(resized_path)

            image_path = resized_path

        result = reader.readtext(
            image_path,

            detail=0,

            decoder="greedy",

            canvas_size=1280,

            mag_ratio=1.0,

            batch_size=4,

            workers=0,

            min_size=15,

            text_threshold=0.6,

            low_text=0.3,

            link_threshold=0.4,

            paragraph=False
        )

        text = "\n".join(
            item.strip()
            for item in result
            if item and item.strip()
        )

        # Remove temporary resized image
        if image_path.endswith("_ocr.png"):

            try:
                import os
                os.remove(image_path)
            except Exception:
                pass

        return text

    except Exception as e:

        print(
            f"⚠️ OCR error: "
            f"{type(e).__name__}: {e}"
        )

        return ""
