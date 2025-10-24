const WebSocket = require('ws');
const express = require('express');
const http = require('http');
const axios = require('axios');

const app = express();
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Construir la URL del backend a partir de variables de entorno
// Default a 'backend:5000' para compatibilidad con docker-compose local
const BACKEND_HOST = process.env.BACKEND_HOST || 'backend';
const BACKEND_PORT = process.env.BACKEND_PORT || 5000;
const BACKEND_API_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/ventas/imprimiendo`;

wss.on('connection', async ws => {
  console.log('Client connected');

  // Fetch initial data and send it to the newly connected client
  try {
    console.log(`Fetching initial data from ${BACKEND_API_URL}`);
    const response = await axios.get(BACKEND_API_URL);
    const imprimiendoVentas = response.data;
    
    console.log(`Sending initial data to the connected client.`);
    ws.send(JSON.stringify(imprimiendoVentas), (err) => {
      if (err) {
        console.error('Error sending initial data to client:', err);
      }
    });
  } catch (error) {
    console.error('Error fetching initial data:', error.message);
  }

  ws.on('close', () => {
    console.log('Client disconnected');
  });
  ws.on('error', error => {
    console.error('WebSocket error:', error);
  });
});

app.post('/broadcast', (req, res) => {
  console.log('Received POST on /broadcast');
  console.log('Request body:', JSON.stringify(req.body, null, 2));

  if (!req.body || !req.body.message) {
    console.error('Broadcast request received without a "message" payload.');
    return res.status(400).send({ error: 'Invalid payload. "message" property is required.' });
  }

  const message = req.body.message;
  console.log(`Broadcasting message to ${wss.clients.size} clients.`);
  
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      console.log('Sending message to a client.');
      client.send(JSON.stringify(message), (err) => {
        if (err) {
          console.error('Error sending message to client:', err);
        }
      });
    }
  });
  res.status(200).send('Message broadcasted');
});

server.listen(3001, () => {
  console.log('WebSocket server listening on port 3001');
});
