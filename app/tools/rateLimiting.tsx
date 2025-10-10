"use server";
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";
import { headers } from 'next/headers';
import { config } from '../config';

let ratelimit: Ratelimit | undefined;

if (config.useRateLimiting) {
    ratelimit = new Ratelimit({
        redis: Redis.fromEnv(),
        limiter: Ratelimit.slidingWindow(10, "10 m") // 10 requests per 10 minutes
    });
}

export async function checkRateLimit(streamable: any) {
    if (config.useRateLimiting && ratelimit) {
        const identifier = headers().get('x-forwarded-for') || headers().get('x-real-ip') || headers().get('cf-connecting-ip') || headers().get('client-ip') || "";
        const { success } = await ratelimit.limit(identifier);
        streamable.done({ 'status': 'rateLimitReached' });
        return success;
    }
    return true;
}