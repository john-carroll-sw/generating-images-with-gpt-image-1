import requests
import json
import os
import sys
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_V1_API_ENDPOINT"),
    default_query={"api-version": "preview"}, 
)

# Add a structured response schema for the image extraction
image_schema = {
    "type": "object",
    "properties": {
        "image_url": {"type": "string"},
        "source_url": {"type": "string"},
        "found_method": {"type": "string", "description": "How the image was found (og:image, product__media, first_img)"}
    },
    "required": ["image_url", "source_url", "found_method"],
    "additionalProperties": False
}

# Update extract_image_url to return structured output
def extract_image_url(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Amazon-specific extraction
    if 'amazon.' in product_url:
        # Try to get the main image from the dynamic image data attribute
        img_tag = soup.find('img', id='landingImage')
        data_image = img_tag['data-a-dynamic-image'] if img_tag and img_tag.has_attr('data-a-dynamic-image') else None
        if data_image:
            try:
                images = json.loads(data_image)
                first_image = next(iter(images.keys()), None)
                if first_image:
                    url = first_image if first_image.startswith('http') else f'https:{first_image}'
                    return {
                        "image_url": url,
                        "source_url": product_url,
                        "found_method": "amazon:data-a-dynamic-image"
                    }
            except Exception:
                pass
        # Fallback: look for og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return {
                "image_url": og_image['content'],
                "source_url": product_url,
                "found_method": "og:image"
            }
        # Fallback: look for first large image in the page
        for img in soup.find_all('img', src=True):
            src = img['src']
            if 'images' in src and src.endswith('.jpg'):
                if src.startswith('//'):
                    src = 'https:' + src
                return {
                    "image_url": src,
                    "source_url": product_url,
                    "found_method": "amazon:img[src]"
                }

    # Generic strategies
    strategies = [
        (soup.find('meta', property='og:image'), 'content', 'og:image'),
        (soup.find('img', {'class': 'product__media'}), 'src', 'product__media'),
        (soup.find('img'), 'src', 'first_img'),
    ]
    for tag, attr, method in strategies:
        val = tag[attr] if tag and tag.has_attr(attr) else None
        if val and val.startswith('//'):
            val = 'https:' + val
        if val:
            return {
                "image_url": val,
                "source_url": product_url,
                "found_method": method
            }
    return {
        "image_url": None,
        "source_url": product_url,
        "found_method": "not_found"
    }

tools = [{
    "type": "function",
    "name": "extract_image_url",
    "description": "Extract the main image URL from an e-commerce product page URL.",
    "parameters": {
        "type": "object",
        "properties": {
            "product_url": {"type": "string"}
        },
        "required": ["product_url"],
        "additionalProperties": False
    },
    "strict": True
}]

def main():
    if len(sys.argv) < 2:
        print('Usage: python get_item_image.py <product_url>')
        sys.exit(1)
    product_url = sys.argv[1]

    input_messages = [{"role": "user", "content": f"Get the image for {product_url}"}]

    response = client.responses.create(
        model=os.environ["AZURE_OPENAI_API_MODEL"],
        input=input_messages,
        tools=tools,
        temperature=0.0,
    )

    tool_call = response.output[0]
    args = json.loads(tool_call.arguments)

    # When calling extract_image_url, return the structured response as JSON
    result = extract_image_url(args["product_url"])

    input_messages.append(tool_call)  # append model's function call message
    input_messages.append({                               # append result message
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": json.dumps(result)
    })

    response_2 = client.responses.create(
        model=os.environ["AZURE_OPENAI_API_MODEL"],
        input=input_messages,
        tools=tools,
        text={
            "format": {
                "type": "json_schema",
                "name": "image_extraction_result",
                "schema": image_schema,
                "strict": True
            }
        }
    )

    result = json.loads(response_2.output_text)
    print(result)

if __name__ == "__main__":
    main()