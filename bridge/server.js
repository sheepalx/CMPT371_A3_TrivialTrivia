const express = require("express")
const http = require("http")
const WebSocket = require("ws")
const net = require("net")
const cors = require("cors")

const app = express()
app.use(cors())

app.get("/health", (_, res) => {
  res.json({ ok: true })
})

const server = http.createServer(app)
const wss = new WebSocket.Server({ server })

const TCP_HOST = "127.0.0.1"
const TCP_PORT = 5555
const HTTP_PORT = 8080

wss.on("connection", (ws) => {
  let tcp = null
  let buffer = ""

  const sendToBrowser = (obj) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(obj))
    }
  }

  ws.on("message", (raw) => {
    let msg

    try {
      msg = JSON.parse(raw.toString())
    } catch {
      sendToBrowser({ type: "error", message: "Invalid JSON from browser" })
      return
    }

    if (msg.type === "connect_tcp") {
      if (tcp) return

      tcp = net.createConnection(
        {
          host: TCP_HOST,
          port: TCP_PORT
        },
        () => {
          sendToBrowser({ type: "bridge_connected" })
          if (msg.username) {
            tcp.write(JSON.stringify({ type: "hello", username: msg.username }) + "\n")
          }
        }
      )

      tcp.on("data", (chunk) => {
        buffer += chunk.toString("utf8")

        while (buffer.includes("\n")) {
          const idx = buffer.indexOf("\n")
          const line = buffer.slice(0, idx).trim()
          buffer = buffer.slice(idx + 1)

          if (!line) continue

          try {
            const parsed = JSON.parse(line)
            sendToBrowser(parsed)
          } catch {
            sendToBrowser({ type: "error", message: "Invalid JSON from TCP server" })
          }
        }
      })

      tcp.on("error", () => {
        sendToBrowser({ type: "error", message: "Could not connect to Python server" })
      })

      tcp.on("close", () => {
        sendToBrowser({ type: "bridge_tcp_closed" })
      })

      return
    }

    if (!tcp) {
      sendToBrowser({ type: "error", message: "TCP connection not established" })
      return
    }

    tcp.write(JSON.stringify(msg) + "\n")
  })

  ws.on("close", () => {
    if (tcp) {
      tcp.end()
      tcp.destroy()
      tcp = null
    }
  })
})

server.listen(HTTP_PORT, () => {
  console.log(`Bridge running on http://localhost:${HTTP_PORT}`)
})