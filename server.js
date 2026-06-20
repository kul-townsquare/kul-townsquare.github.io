const WebSocket = require("ws");
const http = require("http");

const PORT = process.env.PORT || 8081;

// channels: Map<channelId, Map<playerId, WebSocket>>
const channels = new Map();

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.url === "/ping") {
    res.writeHead(200);
    res.end("pong");
  } else {
    res.writeHead(200);
    res.end("BotC Live Session Server");
  }
});

const wss = new WebSocket.Server({ server });

wss.on("connection", (ws, req) => {
  const parts = req.url.replace(/^\//, "").split("/");
  if (parts.length < 2 || !parts[0] || !parts[1]) {
    ws.close(1008, "Invalid path. Expected /<channel>/<playerId>");
    return;
  }

  const [channelId, playerId] = parts;

  if (!channels.has(channelId)) {
    channels.set(channelId, new Map());
  }
  const channel = channels.get(channelId);
  channel.set(playerId, ws);

  console.log(`[+] ${playerId} joined channel ${channelId} (${channel.size} in room)`);

  ws.on("message", data => {
    let command, params;
    try {
      [command, params] = JSON.parse(data);
    } catch {
      return;
    }

    if (command === "direct") {
      // params is { targetPlayerId: [command, params], ... }
      for (const [targetId, payload] of Object.entries(params)) {
        const target = channel.get(targetId);
        if (target && target.readyState === WebSocket.OPEN) {
          target.send(JSON.stringify(payload));
        }
      }
    } else {
      // broadcast to everyone else in the channel
      for (const [id, client] of channel.entries()) {
        if (id !== playerId && client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify([command, params]));
        }
      }
    }
  });

  ws.on("close", () => {
    channel.delete(playerId);
    console.log(`[-] ${playerId} left channel ${channelId} (${channel.size} remaining)`);
    if (channel.size === 0) {
      channels.delete(channelId);
    }
  });

  ws.on("error", err => {
    console.error(`Error for ${playerId} in ${channelId}:`, err.message);
  });
});

server.listen(PORT, () => {
  console.log(`WebSocket server listening on port ${PORT}`);
});
