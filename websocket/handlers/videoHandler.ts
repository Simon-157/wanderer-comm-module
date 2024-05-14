import { VideoData } from "../utils/types";
const videoQueue = require('../queues/videoQueue');

export const handleVideoData = (data: VideoData) => {
    videoQueue.publishVideoMessage(data);
}
