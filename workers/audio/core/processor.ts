import { logger } from '../config/logger';
import { api } from '../config/api';

export const processAudioData = async (sessionId:string, userId:string) => {
    try {
        const res = await api.post('/predict/ser', { 'session_id': sessionId, 'user_id': userId }, {
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': 'wanderer1234@WERTYYY5666FF'
            }
        });
        logger.log({ level: 'info', message: `Processed audio data: ${res.data.message}` });
    } catch (error) {
        logger.log({ level: 'error', message: `Error processing audio data: ${error}` });
    }
}