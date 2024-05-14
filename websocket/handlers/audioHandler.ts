const audioQueue = require('../queues/audioQueue');

export const handleAudioData = (data: Buffer) =>{
    audioQueue.publishAudioMessage(data);
}

