
import { config } from '../config';
import { OpenAI } from 'openai';

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

interface SearchResult {
    title: string;
    link: string;
    favicon: string;
}

export const relevantQuestions = async (sources: SearchResult[], userMessage: String): Promise<any> => {
    return await openai.chat.completions.create({
        messages: [
            {
                role: "system",
                content: `
            You are a Question generator who generates an array of 3 follow-up questions in JSON format.
            The JSON schema should include:
            {
              "original": "The original search query or context",
              "followUp": [
                "Question 1",
                "Question 2", 
                "Question 3"
              ]
            }
            `,
            },
            {
                role: "user",
                content: `Generate follow-up questions based on the top results from a similarity search: ${JSON.stringify(sources)}. The original search query is: "${userMessage}".`,
            },
        ],
        model: config.inferenceModel,
        response_format: { type: "json_object" },
    });
};