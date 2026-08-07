import os
from vision.windows_ocr import extract_text

image = input("Image path: ")

image = os.path.abspath(image)

print(image)

text = extract_text(image)

print(text)