import * as fal from "@fal-ai/serverless-client";

export async function falAiStableDiffusion3Medium(mentionTool: string, userMessage: string, streamable: any): Promise<void> {
    const result = await fal.subscribe("fal-ai/stable-diffusion-v3-medium", {
        input: {
            prompt: userMessage,
            sync_mode: true
        },
        logs: true,
        onQueueUpdate: (update) => {
            if (update.status === "IN_PROGRESS" && update.logs) {
                update.logs.map((log) => log.message).forEach(console.log);
            }
        },
    });

    if ((result as any).images && (result as any).images.length > 0) {
        const imageUrl = (result as any).images[0].url;
        const response = await fetch(imageUrl);
        const buffer = await response.arrayBuffer();
        let base64data = Buffer.from(buffer).toString('base64');
        base64data = `data:image/png;base64,${base64data}`;
        streamable.done({ 'falBase64Image': base64data });
    } else {
        streamable.done({ 'llmResponseEnd': true });
    }
    // Ensure the function returns void
    return;
}