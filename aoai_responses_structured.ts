import dotenv from "dotenv";
dotenv.config();

import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.AZURE_OPENAI_API_KEY,
  baseURL: process.env.AZURE_OPENAI_V1_API_ENDPOINT,
  defaultQuery: { "api-version": "preview" },
});

async function extractEvent() {
  const response = await client.responses.create({
    model: process.env.AZURE_OPENAI_API_MODEL!,
    input: [
      { role: "system", content: "Extract the event information." },
      { role: "user", content: "Alice and Bob are going to a science fair on Friday." },
    ],
    text: {
      format: {
        type: "json_schema",
        name: "calendar_event",
        schema: {
          type: "object",
          properties: {
            name: { type: "string" },
            date: { type: "string" },
            participants: { type: "array", items: { type: "string" } },
          },
          required: ["name", "date", "participants"],
          additionalProperties: false,
        },
        strict: true,
      },
    },
  });

  const event = JSON.parse(response.output_text);
  console.log(event);
}

extractEvent();
