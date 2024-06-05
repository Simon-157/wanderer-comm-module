import { logger } from "./config/logger";
import { consumeAudioMessages, consumeVideoMessages, init } from "./core/consumer";


const startAudioWorker = async ()=> {
    try {
        await init();
        logger.info('Audio worker started');
        await consumeAudioMessages();
    } catch (error) {
        logger.error('Error starting audio worker:', error);
    }
}

const startVideoWorker = async () => {
    try {
        await init();
        logger.info('Video worker started');
        await consumeVideoMessages();
    } catch (error) {
        logger.error('Error starting video worker:', error);
    }
}

startAudioWorker();
startVideoWorker()