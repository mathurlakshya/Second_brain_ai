from PIL import Image
import asyncio

from winsdk.windows.graphics.imaging import BitmapDecoder
from winsdk.windows.storage import StorageFile
from winsdk.windows.media.ocr import OcrEngine
from winsdk.windows.globalization import Language


async def _read_text(image_path):

    file = await StorageFile.get_file_from_path_async(image_path)

    stream = await file.open_async(0)

    decoder = await BitmapDecoder.create_async(stream)

    bitmap = await decoder.get_software_bitmap_async()

    engine = OcrEngine.try_create_from_language(
        Language("en")
    )

    result = await engine.recognize_async(bitmap)

    return result.text


def extract_text(image_path):

    return asyncio.run(
        _read_text(image_path)
    )