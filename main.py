from dotenv import load_dotenv
import os
from pdf2image import convert_from_path
from groq import Groq
import time
import base64

load_dotenv()

INPUT_DIRECTORY = "input"

# gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=groq_api_key,
)

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# get the first pdf file in the input directory
def convert_pdf_to_images():
    pdf_file = next(iter(os.listdir(INPUT_DIRECTORY)), None)

    if pdf_file is None:
        print("No PDF file found in the input directory")
        exit(1)

    # conver the pdf to multiple iamges
    print(f"Converting {pdf_file} to images")
    images = convert_from_path(f"{INPUT_DIRECTORY}/{pdf_file}")
    images_count = len(images)
    for i, image in enumerate(images):
        image.save(f"images/page_{i+1}.png", "PNG")
    print(f"Done converting {pdf_file} to images")

def get_image_paths():
    result = []

    for i in os.listdir("images"):
        if i.endswith(".png"):
            result.append(f"images/{i}")

    return result



# ocr the images into text though genimi api, and append the contents to result.md file
def ocr_images(image_paths: list[str]):
    for image_path in image_paths:

        print(f"Processing {image_path}")

        base64_image = encode_image(image_path)

        prompt = "OCR this image and write down its content into a md format. do not write anything other than the content of the image"

        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        with open("result.md", "a", encoding="utf8") as f:
            f.write(completion.choices[0].message.content)

        print(f"Parsed {image_path}")
        os.remove(image_path)
        time.sleep(5)

if __name__ == "__main__":
    
    convert_pdf_to_images() # commment this line if the previous execution was not successful and wish to continue from where it stopped

    image_paths = get_image_paths()
    ocr_images(image_paths)