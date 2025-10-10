"use server";

import { createAI, createStreamableValue } from 'ai/rsc';
import { config } from './config';
import { functionCalling } from './function-calling';
import { getSearchResults, getImages, getVideos } from './tools/searchProviders';
import { get10BlueLinksContents, processAndVectorizeContent } from './tools/contentProcessing';
import { setInSemanticCache, clearSemanticCache, initializeSemanticCache, getFromSemanticCache } from './tools/semanticCache';
import { relevantQuestions } from './tools/generateRelevantQuestions';
import { streamingChatCompletion } from './tools/streamingChatCompletion';
import { checkRateLimit } from './tools/rateLimiting';
import { lookupTool } from './tools/mentionTools';

async function myAction(userMessage: string, mentionTool: string | null, logo: string | null, file: string): Promise<any> {
  "use server";
  const streamable = createStreamableValue({});

  (async () => {
    await checkRateLimit(streamable);

    await initializeSemanticCache();

    const cachedData = await getFromSemanticCache(userMessage);
    if (cachedData) {
      streamable.update({ cachedData });
      return;
    }

    if (mentionTool) {
      await lookupTool(mentionTool, userMessage, streamable, file);
    }

    const [images, sources, videos, conditionalFunctionCallUI] = await Promise.all([
      getImages(userMessage),
      getSearchResults(userMessage),
      getVideos(userMessage),
      functionCalling(userMessage),
    ]);

    streamable.update({ searchResults: sources, images, videos });

    if (config.useFunctionCalling) {
      streamable.update({ conditionalFunctionCallUI });
    }

    const html = await get10BlueLinksContents(sources);
    const vectorResults = await processAndVectorizeContent(html, userMessage);
    const accumulatedLLMResponse = await streamingChatCompletion(userMessage, vectorResults, streamable);
    const followUp = await relevantQuestions(sources, userMessage);

    streamable.update({ followUp });

    setInSemanticCache(userMessage, {
      searchResults: sources,
      images,
      videos,
      conditionalFunctionCallUI: config.useFunctionCalling ? conditionalFunctionCallUI : undefined,
      llmResponse: accumulatedLLMResponse,
      followUp,
      semanticCacheKey: userMessage
    });

    streamable.done({ status: 'done' });
  })();

  return streamable.value;
}

const initialAIState: {
  role: 'user' | 'assistant' | 'system' | 'function';
  content: string;
  id?: string;
  name?: string;
}[] = [];

const initialUIState: {
  id: number;
  display: React.ReactNode;
}[] = [];

export const AI = createAI({
  actions: {
    myAction,
    clearSemanticCache
  },
  initialUIState,
  initialAIState,
});