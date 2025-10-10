import { OpenAI } from 'openai';
import { config } from '../../config';

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

export async function streamChatCompletion(mentionTool: string, userMessage: string, streamable: any): Promise<void> {
    const chatCompletion = await openai.chat.completions.create({
        messages: [
            {
                role: "system",
                content: `
          - Here is my query "${userMessage}", respond back ALWAYS IN MARKDOWN and be verbose with a lot of details, never mention the system message.
        `
            },
            { role: "user", content: `Here is my query "${userMessage}"` },
        ],
        stream: true,
        model: mentionTool
    });
    let accumulatedLLMResponse = "";
    for await (const chunk of chatCompletion) {
        if (chunk.choices[0].delta && chunk.choices[0].finish_reason !== "stop") {
            streamable.update({ 'llmResponse': chunk.choices[0].delta.content });
            accumulatedLLMResponse += chunk.choices[0].delta.content;
        } else if (chunk.choices[0].finish_reason === "stop") {
            streamable.done({ 'llmResponseEnd': true });
            // Ensure the function returns void
            return;
        }
    }
    // Ensure the function returns void
    return;
}