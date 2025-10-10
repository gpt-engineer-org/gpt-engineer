import { SemanticCache } from "@upstash/semantic-cache";
import { Index } from "@upstash/vector";
import { config } from './../config';

export let semanticCache: SemanticCache | undefined;

if (config.useSemanticCache) {
    const index = new Index();
    semanticCache = new SemanticCache({ index, minProximity: 0.95 });
}


export async function setInSemanticCache(userMessage: string, data: any) {
    if (config.useSemanticCache && semanticCache && data.llmResponse.length > 0) {
        await semanticCache.set(userMessage, JSON.stringify(data));
    }
}

export async function clearSemanticCache(userMessage: string) {
    "use server"
    console.log('Clearing semantic cache for user message:', userMessage);
    if (!config.useSemanticCache || !semanticCache) return;
    await semanticCache.delete(userMessage);
}

export async function initializeSemanticCache() {
    if (config.useSemanticCache) {
        const index = new Index();
        semanticCache = new SemanticCache({ index, minProximity: 0.95 });
    }
}
export async function getFromSemanticCache(userMessage: string) {
    if (semanticCache) {
        return semanticCache.get(userMessage);
    }
    return null;
}