export const mentionToolConfig = {
    useMentionQueries: true,
    mentionTools: [
        // Groq Models
        { id: 'llama3-70b-8192', name: 'Groq Llama3-70b-8192', logo: 'https://asset.brandfetch.io/idxygbEPCQ/idzCyF-I44.png?updated=1668515712972', functionName: 'streamChatCompletion', enableRAG: true },
        { id: 'llama3-8b-8192', name: 'Groq Llama3-8b-8192', logo: 'https://asset.brandfetch.io/idxygbEPCQ/idzCyF-I44.png?updated=1668515712972', functionName: 'streamChatCompletion', enableRAG: true },
        { id: 'mixtral-8x7b-32768', name: 'Groq Mixtral-8x7b-32768', logo: 'https://asset.brandfetch.io/idxygbEPCQ/idzCyF-I44.png?updated=1668515712972', functionName: 'streamChatCompletion', enableRAG: true },
        // AI Gateway + Portkey --- ANTHROPIC
        { id: 'anthropic.claude-3-sonnet-20240229-v1:0', name: 'Anthropic Claude 3 Sonnet', logo: 'https://asset.brandfetch.io/idmJWF3N06/idq0tv4tfX.svg?updated=1693981852273', functionName: 'portKeyAIGateway', enableRAG: true },
        { id: 'anthropic.claude-3-haiku-20240307-v1:0', name: 'Anthropic Claude 3 Haiku', logo: 'https://asset.brandfetch.io/idmJWF3N06/idq0tv4tfX.svg?updated=1693981852273', functionName: 'portKeyAIGateway', enableRAG: true },
        // AI Gateway + Portkey --- COHERE
        { id: 'cohere.command-text-v14', name: 'Cohere Command', logo: 'https://asset.brandfetch.io/idyni_Sw9h/idsvG5y-ZU.png?updated=1710782726843', functionName: 'portKeyAIGateway' },
        { id: 'cohere.command-light-text-v14', name: 'Cohere Command Light', logo: 'https://asset.brandfetch.io/idyni_Sw9h/idsvG5y-ZU.png?updated=1710782726843', functionName: 'portKeyAIGateway' },
        // AI Gateway + Portkey --- Mistral Large
        { id: 'mistral.mistral-large-2402-v1:0', name: 'Mistral Large', logo: 'https://asset.brandfetch.io/iduUavnR6m/id_83EF0Fl.jpeg?updated=1717360232737', functionName: 'portKeyAIGateway', enableRAG: true },
        // AI Gateway + Together.AI --- QWEN
        { id: 'Qwen/Qwen2-72B-Instruct', name: 'Qwen2 - 72B', logo: 'https://avatars.githubusercontent.com/u/141221163?s=200&v=4', functionName: 'portKeyAIGatewayTogetherAI', enableRAG: true },
        // FAL.AI - Stable Diffusion 3 Medium
        { id: 'fal-ai/stable-diffusion-v3-medium', name: 'fal.ai Stable Diffusion 3 ', logo: 'https://avatars.githubusercontent.com/u/74778219?s=200&v=4', functionName: 'falAiStableDiffusion3Medium' },
        // Bright Data - Targeted Web Scraping
        { id: 'bright-data-web-unlock', name: 'Bright Data - Web Unlock / Puppeteer', logo: './bright-data-logo.png', functionName: 'brightDataWebScraper', enableRAG: false },
    ],
};
