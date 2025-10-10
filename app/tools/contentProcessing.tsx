
import { config } from '../config';
import cheerio from 'cheerio';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { Document as DocumentInterface } from 'langchain/document';
import { OpenAIEmbeddings } from '@langchain/openai';
import { OllamaEmbeddings } from "@langchain/community/embeddings/ollama";
let embeddings: OllamaEmbeddings | OpenAIEmbeddings;
if (config.useOllamaEmbeddings) {
    embeddings = new OllamaEmbeddings({
        model: config.embeddingsModel,
        baseUrl: "http://localhost:11434"
    });
} else {
    embeddings = new OpenAIEmbeddings({
        modelName: config.embeddingsModel
    });
}

interface SearchResult {
    title: string;
    link: string;
    favicon: string;
}
interface ContentResult extends SearchResult {
    html: string;
}


//  Fetch contents of top 10 search results
export async function get10BlueLinksContents(sources: SearchResult[]): Promise<ContentResult[]> {
    async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = 800): Promise<Response> {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            const response = await fetch(url, { ...options, signal: controller.signal });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            if (error) {
                console.log(`Skipping ${url}!`);
            }
            throw error;
        }
    }
    function extractMainContent(html: string): string {
        try {
            const $ = cheerio.load(html);
            $("script, style, head, nav, footer, iframe, img").remove();
            return $("body").text().replace(/\s+/g, " ").trim();
        } catch (error) {
            console.error('Error extracting main content:', error);
            throw error;
        }
    }
    const promises = sources.map(async (source): Promise<ContentResult | null> => {
        try {
            const response = await fetchWithTimeout(source.link, {}, 800);
            if (!response.ok) {
                throw new Error(`Failed to fetch ${source.link}. Status: ${response.status}`);
            }
            const html = await response.text();
            const mainContent = extractMainContent(html);
            return { ...source, html: mainContent };
        } catch (error) {
            // console.error(`Error processing ${source.link}:`, error);
            return null;
        }
    });
    try {
        const results = await Promise.all(promises);
        return results.filter((source): source is ContentResult => source !== null);
    } catch (error) {
        console.error('Error fetching and processing blue links contents:', error);
        throw error;
    }
}
// rocess and vectorize content using LangChain
export async function processAndVectorizeContent(
    contents: ContentResult[],
    query: string,
    textChunkSize = config.textChunkSize,
    textChunkOverlap = config.textChunkOverlap,
    numberOfSimilarityResults = config.numberOfSimilarityResults,
): Promise<DocumentInterface[]> {
    const allResults: DocumentInterface[] = [];
    try {
        for (let i = 0; i < contents.length; i++) {
            const content = contents[i];
            if (content.html.length > 0) {
                try {
                    const splitText = await new RecursiveCharacterTextSplitter({ chunkSize: textChunkSize, chunkOverlap: textChunkOverlap }).splitText(content.html);
                    const vectorStore = await MemoryVectorStore.fromTexts(splitText, { title: content.title, link: content.link }, embeddings);
                    const contentResults = await vectorStore.similaritySearch(query, numberOfSimilarityResults);
                    allResults.push(...contentResults);
                } catch (error) {
                    console.error(`Error processing content for ${content.link}:`, error);
                }
            }
        }
        return allResults;
    } catch (error) {
        console.error('Error processing and vectorizing content:', error);
        throw error;
    }
}