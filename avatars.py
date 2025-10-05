from PIL import Image, ImageDraw, ImageFont

def generate_empty_images_grid(rows: int, cols: int, labels: list[list[str]], sizew: int = 128, sizeh: int = 128, padding: int = 10):
    image = Image.new("RGB", (cols * sizew + (cols + 1) * padding, rows * sizeh + (rows + 1) * padding), "black")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=20)

    for r in range(rows):
        for c in range(cols):
            background, foreground = ("red", "black") #if (r + c) % 2 == 0 else ("gray", "black")

            draw.rectangle([c * sizew + (c + 1) * padding, r * sizeh + (r + 1) * padding, (c + 1) * sizew + (c + 1) * padding, (r + 1) * sizeh + (r + 1) * padding], fill=background, outline=foreground, width=2)
            text = labels[r][c] if r < len(labels) and c < len(labels[r]) else ""
            bbox = font.getbbox(text)
            # text_width = bbox[2] - bbox[0]
            # text_height = bbox[3] - bbox[1]
            draw.text((c * sizew + (c + 1) * padding + sizew / 2, r * sizeh + (r + 1) * padding + sizeh / 2), text, fill=foreground, font=font, align="center", anchor="mm")
    return image


# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate(local_path):
    client = genai.Client(
        api_key=os.environ.get("API_KEY")
    )

    model = "gemini-2.5-flash-image"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(
                    data=open(local_path, mode="rb").read(),
                    mime_type='image/jpeg',
                ),
                types.Part.from_bytes(data=open("b3e5db5a3bf1399f74500a6209462794.jpg", "rb").read(), mime_type="image/jpeg"),
                types.Part.from_text(text="Replace each red grid cell with portrait with adjusted person age and mood based on cell description. Use original portrait background"),

            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.15,
        response_modalities=[
            "IMAGE",
        ],
        image_config=types.ImageConfig(
            aspect_ratio="4:3",
        ),
    )

    file_index = 0
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    for candidate in response.candidates:
        if candidate.content.parts[0].inline_data and candidate.content.parts[0].inline_data.data:
            file_index += 1
            inline_data = candidate.content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            import datetime
            name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            save_binary_file(f"{name}{file_extension}", data_buffer)
            return f"{name}{file_extension}"

if __name__ == "__main__":
    ages = [20, 40, 60, 80]
    moods = ["Happy Face", "Neutral Face", "Crying Face"]
    rows = len(moods)
    cols = len(ages)
    
    labels = [
        [f"{age} years old\n{mood}" for age in ages]
        for mood in moods
    ]
    image = generate_empty_images_grid(rows, cols, labels, sizew=296, sizeh=288, padding=0)
    # image.show()
    image.save("avatars_grid.png")
    out = generate("avatars_grid.png")
    # generate(out)