import { io } from 'socket.io-client';

const URL = 'http://localhost:4000';

// autoConnect intentionally left at default: on
export const socket = io(URL);
