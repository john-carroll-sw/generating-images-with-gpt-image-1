# OpenAI Image Generation & Extraction

![Demo](./demo.gif)

This repository demonstrates how to use OpenAI's Response API (with GPT-4o, and gpt-image-1 via Azure OpenAI or OpenAI) to:

- Generate images from a text prompt
- Generate images from an existing image and a prompt (image-to-image)
- Extract the main product image URL from an e-commerce product page

It provides both Python and TypeScript implementations, returning structured outputs for easy integration.

## Features

- Generate images from a prompt using GPT-4o, or gpt-image-1
- Generate images from an image and a prompt (image-to-image)
- Extracts the main product image URL from a given e-commerce product page
- Uses OpenAI tool-calling to orchestrate the extraction and generation process
- Returns a structured response with the image URL, source URL, and extraction/generation method
- Supports both Python and TypeScript (Node.js) environments

## How it Works

- For generation: The script sends a prompt (and optionally an image) to the OpenAI/Azure OpenAI API to generate a new image.
- The result is returned in a structured format, including the extraction or generation method used.

## Flow Diagram

```mermaid
flowchart TD
    A["User provides product URL<br/>or prompt (+ optional<br/>image)"] --> B(OpenAI Responses API:<br/>tool calling)
    B --> C{Tool: extract_image_url<br/>or generate_image}
    C --> D[Fetch product page HTML<br/>or send prompt/image<br/>to API]
    D --> E{Extraction or<br/>Generation strategies}
    E -->|og:image| F[Extract from Open Graph<br/>meta tag]
    E -->|product__media| G[Extract from<br/>product__media class]
    E -->|first_img| H["Extract first<br>&lt;img&gt; tag"]
    E -->|prompt| L[Generate from<br/>prompt]
    E -->|image+prompt| M[Generate from image<br/>and prompt]
    F & G & H & L & M --> I[Return structured output]
    I --> J[OpenAI returns<br>structured JSON]
    J --> K[User receives image_url,<br>source_url, found_method]
```

## Example Output

```json
{
  "image_url": "http://minecraftshop.com/cdn/shop/files/MINE-PLU1_R_MF_1200x1200.jpg?v=1729532536",
  "source_url": "https://minecraftshop.com/collections/plush/products/minecraft-goat-8-plush",
  "found_method": "og:image"
}
```

## Requirements

- Python 3.8+ (for Python version)
- Node.js 18+ (for TypeScript version)
- Access to Azure OpenAI or OpenAI API (with appropriate keys and endpoint)

## Setup

### 1. Clone the repository

```sh
git clone <repo-url>
cd get-item-image
```

### 2. Environment Variables

Copy `.env.sample` to `.env` and fill in your API keys and endpoints:

```sh
cp .env.sample .env
```

Edit `.env` and set:

- `AZURE_OPENAI_V1_API_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_MODEL`

### 3. Install Dependencies

#### Python/.py

```sh
pip install -r requirements.txt
# or manually:
pip install openai python-dotenv beautifulsoup4 requests
```

#### TypeScript/Node.js

```sh
npm install
```

## Usage

### Python

```sh
python get_item_image.py "https://minecraftshop.com/collections/plush/products/minecraft-goat-8-plush"
# or for image generation:
python get_item_image.py --generate --prompt "A cat in a spacesuit"
python get_item_image.py --generate --prompt "A cat in a spacesuit" --image path/to/input.jpg
```

### TypeScript

```sh
npx ts-node get_item_image.ts "https://minecraftshop.com/collections/plush/products/minecraft-goat-8-plush"
# or for image generation:
npx ts-node get_item_image.ts --generate --prompt "A cat in a spacesuit"
npx ts-node get_item_image.ts --generate --prompt "A cat in a spacesuit" --image path/to/input.jpg
```

## File Overview

- `get_item_image.py` — Python implementation
- `get_item_image.ts` — TypeScript/Node.js implementation
- `.env.sample` — Example environment variable file
- `demo.gif` — Demo animation

## License

MIT
