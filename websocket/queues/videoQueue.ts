import { logger } from "../config/logger";
import * as rabbitmq from '../config/rabbit'; 

const VIDEO_QUEUE_NAME = 'video_queue';

export const init = async () => {
    await rabbitmq.connect();
    const channel = rabbitmq.getChannel();
    await channel?.assertQueue(VIDEO_QUEUE_NAME, { durable: true });
    
}

export const publishVideoMessage = async (userId: string, sessionId: string) => {
    try {
        const channel = rabbitmq.getChannel();
        const message = JSON.stringify({ userId, sessionId });
        console.log('Publishing video message:', message);
        await channel?.sendToQueue(VIDEO_QUEUE_NAME, Buffer.from(message));
    } catch (error) {
        logger.error('Error publishing video message:', error);
    }
}