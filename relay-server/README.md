# CloudSync Relay Server 🚀

A WebSocket relay server for remote desktop connections, **disguised as a legitimate file sync service**.

## 🎯 What It Does

- Creates secure WebSocket relay for remote desktop apps
- Generates 6-digit session codes for easy connection
- Disguised as "CloudSync File Service" for stealth
- Handles host-client pairing automatically
- Relays screen data and input events

## 🚀 Quick Deploy to Render

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "CloudSync relay server"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repo
   - Choose "Web Service"
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Choose free tier

3. **Your server will be live at:**
   `https://your-app-name.onrender.com`

## 🔧 Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Or start production
npm start
```

Server runs on `http://localhost:3000`

## 📡 API Endpoints

### Main Endpoints (For Disguise)
- `GET /` - Service info (looks like file sync)
- `GET /api/files` - Fake file listing
- `POST /api/sync` - Fake sync endpoint
- `GET /health` - Health check

### Session Management
- `POST /api/session/create` - Create new session
- `POST /api/session/join` - Join existing session

### WebSocket
- `ws://localhost:3000` - WebSocket connection

## 🎮 How to Use

### 1. Create Session
```javascript
POST /api/session/create
Response: { "sessionId": "ABC123" }
```

### 2. Connect Host
```javascript
// WebSocket message
{
  "type": "host",
  "sessionId": "ABC123"
}
```

### 3. Connect Client  
```javascript
// WebSocket message
{
  "type": "client", 
  "sessionId": "ABC123"
}
```

### 4. Relay Data
```javascript
// Screen data (host → client)
{
  "type": "screen_data",
  "sessionId": "ABC123", 
  "data": "base64_image_data"
}

// Input data (client → host)
{
  "type": "input_data",
  "sessionId": "ABC123",
  "data": { "mouse": { "x": 100, "y": 200 } }
}
```

## 🥷 Stealth Features

- **Appears as legitimate file sync service**
- **Fake API endpoints** that return realistic data
- **Professional naming** and branding
- **Standard web traffic** (WebSocket over HTTPS)
- **No suspicious patterns** in network logs

## 🌐 Production Considerations

- Use HTTPS/WSS in production
- Add rate limiting
- Implement authentication if needed
- Use Redis for session storage (multi-instance)
- Add logging and monitoring

## 📊 Monitoring

Visit `/health` to see:
- Active sessions
- Connected clients  
- Memory usage
- Uptime

Perfect for remote desktop apps! 🖥️✨
