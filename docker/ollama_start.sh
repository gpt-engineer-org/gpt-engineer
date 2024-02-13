#!/bin/bash
ollama serve &


# Wait for ollama serve to be ready
until ollama list > /dev/null 2>&1; do
  echo "Waiting for ollama serve to be ready..."
  sleep 1
done

ollama pull $DEFAULT_MODEL

# Keep the script running
tail -f /dev/null
