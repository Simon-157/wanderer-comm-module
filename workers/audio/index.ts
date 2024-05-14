import { logger } from "./config/logger";
import { consumeAudioMessages, init } from "./core/consumer";


async function startAudioWorker() {
    try {
        await init();
        logger.info('Audio worker started');
        await consumeAudioMessages();
    } catch (error) {
        logger.error('Error starting audio worker:', error);
    }
}

startAudioWorker();
