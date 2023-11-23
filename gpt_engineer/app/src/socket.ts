import { io } from 'socket.io-client';

const URL = 'http://localhost:4444';

// autoConnect intentionally left at default: on
export const socket = io(URL);
