const rabbitmq = require('../config/rabbit');
import { VideoData } from '../utils/types';

const AUDIO_QUEUE_NAME = 'audio_queue';

async function init() {
    await rabbitmq.connect();
    const channel = rabbitmq.getChannel();
    await channel.assertQueue(AUDIO_QUEUE_NAME);
}

async function publishAudioMessage(data:VideoData) {
    const channel = rabbitmq.getChannel();
    channel.sendToQueue(AUDIO_QUEUE_NAME, Buffer.from(JSON.stringify(data)));
}

module.exports = { init, publishAudioMessage };
