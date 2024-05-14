import * as amqp from 'amqplib';
import { Channel, Connection } from 'amqplib';
import { logger } from './logger';

let connection: Connection;
let channel: Channel;

export const connect = async () => {
    try {
        connection = await amqp.connect('amqp://localhost');
        channel = await connection.createChannel();
    } catch (error) {
        logger.error('Error connecting to RabbitMQ:', error);
        throw error;
    }
}

export const getChannel = async (): Promise<amqp.Channel> => {
    return channel;
}

