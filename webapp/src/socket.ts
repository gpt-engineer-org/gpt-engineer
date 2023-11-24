import { io } from 'socket.io-client';

const URL = 'ws://cyan.peers.lyra.ly:4444/gptengineer';

// autoConnect intentionally left at default: on
export const socket = io(URL);
