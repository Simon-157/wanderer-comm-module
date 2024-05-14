import express from 'express';
import http from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { storage } from './config/firebase';
import { ref, uploadBytes, uploadString } from 'firebase/storage';
import { init, publishAudioMessage } from './queues/audioQueue';
import { logger } from './config/logger';

const app = express();
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: "http://localhost:5173",
    optionsSuccessStatus: 200,
  }
});

const PORT: number = process.env.PORT ? parseInt(process.env.PORT) : 4000;

init();
io.on('connection', (socket: Socket) => {
  console.log('Client connected');

  socket.on('audio', async (data: any) => {
    
      // check data size in bytes
      logger.log({ level: 'info', message: `Audio data size: ${data.length} bytes` }); 

      const fileName = `audio_${Date.now()}`;
      const storageRef = ref(storage, `${"re4552425ifjjfj4"}/${fileName}.wav`);
      try {
        await uploadBytes(storageRef, data, {
          contentType: 'audio/wav',
          contentEncoding: 'audio/wav',
          contentLanguage: 'en',

          customMetadata: {
            'audio_file_name': fileName,
            'audio_file_type': 'wav',
            'audio_file_session_id': 're4552425ifjjfj4',
            'audio_file_user_id': 're4552425ifjjfj4',   
            'audio_file_extension': '.wav'

          }
        });
        socket.emit('audioUploaded', fileName + '.wav');
        logger.info('Audio file uploaded:', fileName);
      } catch (error) {
        logger.error('Error uploading audio file:', error);
      }
  });

socket.on('frame', async (data: any) => {
  if (!data || typeof data !== 'object') {
    console.error('Invalid frame data received:', data);
    socket.emit('error', 'Invalid frame data received');
    return;
  }

  const { sessionId, userId, frameData } = data;

  if (!sessionId || !userId || !frameData) {
    console.error('Missing required data fields:', data);
    socket.emit('error', 'Missing required data fields');
    return;
  }

  try {
    const fileName = `frame_${Date.now()}.jpg`; 
    const fileRef = ref(storage, `${sessionId}/${fileName}`); 

    const imageBuffer = Buffer.from(frameData, 'base64'); 

    await uploadString(fileRef, imageBuffer.toString('base64'), 'base64', {
      contentType: 'image/jpeg'
    });

    console.log('Frame saved to Firebase Storage:', fileName);
    socket.emit('frameSaved', { sessionId, fileName });
  } catch (error) {
    console.error('Error saving frame:', error);
    socket.emit('error', 'Error saving frame');
  }
});


  socket.on('session_ended', async (data: any) => {
    const sessionId = data.sessionId;
    const userId = data.userId;
    await publishAudioMessage(userId, sessionId);

    socket.emit('sessionEnded', sessionId);

    // disconnect from session
    socket.disconnect();
    console.log('Session ended:', sessionId);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

server.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
