import Portkey from 'portkey-ai';
import { config } from '../../config';

export async function portKeyAIGateway(mentionTool: string, userMessage: string, streamable: any): Promise<void> {
    if (config.usePortkey) {
        const portkey = new Portkey({
            apiKey: process.env.PORTKEY_API_KEY,
            virtualKey: process.env.PORTKEY_BEDROCK_VIRTUAL_KEY
        });

        const chatCompletion = await portkey.chat.completions.create({
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
            max_tokens: mentionTool.includes('anthropic') ? 100000 : 4096,
            model: mentionTool
        });

        let accumulatedLLMResponse = "";
        for await (const chunk of chatCompletion) {
            if (chunk.choices[0].finish_reason === "COMPLETE" || chunk.choices[0].finish_reason === "stop" || chunk.choices[0].finish_reason === "end_turn") {
                streamable.done({ 'llmResponseEnd': true });
                return;
            } else if (chunk.choices[0].delta) {
                streamable.update({ 'llmResponse': chunk.choices[0].delta.content });
                accumulatedLLMResponse += chunk.choices[0].delta.content;
            }
        }
    }
    // Ensure the function returns void
    return;
}