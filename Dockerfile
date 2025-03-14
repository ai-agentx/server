version: '3'

services:
  agent-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    volumes:
      - ./app:/app
    restart: unless-stopped
