import { logger } from '../config/logger';
import { serApi, ferApi } from '../config/api';
import exp from 'constants';

export const processAudioData = async (sessionId:string, userId:string, callbackUrl:string = "") => {
    try {
        const res = await serApi.post('/predictions/ser', { 'sessionId': sessionId, 'userId': userId, 'callbackUrl': callbackUrl}, {
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


export const processVideoData = async (sessionId:string, userId:string, callbackUrl:string = "") => {
    try {
        const res = await ferApi.post('/predictions/fer', { 'sessionId': sessionId, 'userId': userId , 'callbackUrl': callbackUrl}, {
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': 'wanderer1234@WERTYYY5666FF'
            }
        });
        logger.log({ level: 'info', message: `Processed video data: ${res.data.message}` });
    } catch (error) {
        logger.log({ level: 'error', message: `Error processing video data: ${error}` });
    }
}