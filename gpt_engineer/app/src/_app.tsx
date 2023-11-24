import React, { useState, useEffect } from 'react';
import { socket } from './socket';
import { ConnectionState } from './components/ConnectionState';
import { ConnectionManager } from './components/ConnectionManager';
import { Events } from "./components/Events";

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [GPTEvents, setGPTEvents] = useState([]);

  useEffect(() => {
    function onConnect() {
			console.log("Socket.IO is connected");
      setIsConnected(true);
    }

    function onDisconnect() {
			console.log("Socket.IO is disconnected");
      setIsConnected(false);
    }

    function onGPTEvent(value) {
			console.log(`GPT event ${value}`);
      setGPTEvents(previous => [...previous, value]);
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('event', onGPTEvent);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('event', onGPTEvent);
    };
  }, []);

  return (
    <div className="App">
      <ConnectionState isConnected={ isConnected } />
      <Events events={ GPTEvents } />
      <ConnectionManager />
      <MyForm />
    </div>
  );
