// message-queue/rabbitmq.ts
import * as amqp from 'amqplib';
import { Channel, Connection } from 'amqplib';

let connection: Connection | null = null;
let channel: Channel | null = null;

async function connect(): Promise<void> {
    try {
        connection = await amqp.connect('amqp://localhost');
        channel = await connection.createChannel();
    } catch (error) {
        console.error('Error connecting to RabbitMQ:', error);
        throw error;
    }
}

function getChannel(): Channel | null {
    return channel;
}

export { connect, getChannel };