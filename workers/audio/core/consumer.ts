import { ConsumeMessage } from 'amqplib';
import { processAudioData } from './processor';
import { logger } from '../config/logger';
import { connect, getChannel } from '../config/rabit';

interface AudioMessage {
    sessionId: string;
    userId: string;
}

const AUDIO_QUEUE_NAME: string = 'audio_queue';
const VIDEO_QUEUE_NAME: string = 'video_queue';

export const init = async (): Promise<void> => {
    try {
        await connect();
        const channel = await getChannel();
        await channel.assertQueue(AUDIO_QUEUE_NAME, { durable: true });
        await channel.assertQueue(VIDEO_QUEUE_NAME, { durable: true });
    } catch (error) {
        logger.error('Error initializing consumer:', error);
        throw error;
    }
}

export const consumeAudioMessages = async (): Promise<void> => {
    try {
        const channel = await getChannel();
        channel.consume(AUDIO_QUEUE_NAME, async (msg: ConsumeMessage | null) => {
            if (msg !== null) {
                const data: AudioMessage = JSON.parse(msg.content.toString());
                logger.info('Received audio message:', data);
                try {
                    await processAudioData(data.sessionId, data.userId);
                    channel.ack(msg);
                } catch (error) {
                    logger.error('Error processing audio message:', error);
                    channel.nack(msg);
                }
            } else {
                logger.error('Error consuming audio message:', msg);
            }
        });
    } catch (error) {
        logger.error('Error consuming audio messages:', error);
        throw error;
    }
}


export const consumeVideoMessages = async (): Promise<void> => {
    try {
        const channel = await getChannel();
        channel.consume(VIDEO_QUEUE_NAME, async (msg: ConsumeMessage | null) => {
            if (msg !== null) {
                const data: AudioMessage = JSON.parse(msg.content.toString());
                logger.info('Received video message:', data);
                try {
                    await processAudioData(data.sessionId, data.userId);
                    channel.ack(msg);
                } catch (error) {
                    logger.error('Error processing video message:', error);
                    channel.nack(msg);
                }
            } else {
                logger.error('Error consuming video message:', msg);
            }
        });
    } catch (error) {
        logger.error('Error consuming video messages:', error);
        throw error;
    }

}