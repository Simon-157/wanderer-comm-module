import { logger } from "../config/logger";
import * as rabbitmq from '../config/rabbit'; 

const AUDIO_QUEUE_NAME = 'audio_queue';

export const init = async () => {
    await rabbitmq.connect();
    const channel = rabbitmq.getChannel();
    await channel?.assertQueue(AUDIO_QUEUE_NAME, { durable: true });
    
}

export const publishAudioMessage = async (userId: string, sessionId: string) => {
    try {
        const channel = rabbitmq.getChannel();
        const message = JSON.stringify({ userId, sessionId });
        console.log('Publishing audio message:', message);
        await channel?.sendToQueue(AUDIO_QUEUE_NAME, Buffer.from(message));
    } catch (error) {
        logger.error('Error publishing audio message:', error);
    }
}