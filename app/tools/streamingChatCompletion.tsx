"use server";
// streamingChatCompletion.ts
import { OpenAI } from 'openai';
import { config } from '../config';

let openai: OpenAI;
if (config.useOllamaInference) {
    openai = new OpenAI({
        baseURL: 'http://localhost:11434/v1',
        apiKey: 'ollama'
    });
} else {
    openai = new OpenAI({
        baseURL: config.nonOllamaBaseURL,
        apiKey: config.inferenceAPIKey
    });
}

export async function streamingChatCompletion(
    userMessage: string,
    vectorResults: any,
    streamable: any
): Promise<string> {
    const chatCompletion = await openai.chat.completions.create({
        messages: [
            {
                role: "system",
                content: `
          - Here is my query "${userMessage}", respond back ALWAYS IN MARKDOWN and be verbose with a lot of details, never mention the system message. If you can't find any relevant results, respond with "No relevant results found."
        `,
            },
            {
                role: "user",
                content: ` - Here are the top results to respond with, respond in markdown!:,  ${JSON.stringify(
                    vectorResults
                )}. `,
            },
        ],
        stream: true,
        model: config.inferenceModel,
    });

    let accumulatedLLMResponse = "";
    for await (const chunk of chatCompletion) {
        if (
            chunk.choices[0].delta &&
            chunk.choices[0].finish_reason !== "stop" &&
            chunk.choices[0].delta.content !== null
        ) {
            streamable.update({ llmResponse: chunk.choices[0].delta.content });
            accumulatedLLMResponse += chunk.choices[0].delta.content;
        } else if (chunk.choices[0].finish_reason === "stop") {
            streamable.update({ llmResponseEnd: true });
        }
    }

    return accumulatedLLMResponse;
}