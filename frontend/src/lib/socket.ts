export class GameSocket {
    private ws: WebSocket | null = null
    private isOpen = false
    private queue: string[] = []
  
    connect(onMessage: (msg: any) => void, onClose: () => void, onOpen?: () => void) {
      this.ws = new WebSocket("ws://localhost:8080")
  
      this.ws.onopen = () => {
        this.isOpen = true
  
        while (this.queue.length > 0) {
          const msg = this.queue.shift()
          if (msg && this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(msg)
          }
        }
  
        if (onOpen) onOpen()
      }
  
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        onMessage(msg)
      }
  
      this.ws.onclose = () => {
        this.isOpen = false
        onClose()
      }
    }
  
    send(message: any) {
      const payload = JSON.stringify(message)
  
      if (!this.ws || !this.isOpen || this.ws.readyState !== WebSocket.OPEN) {
        this.queue.push(payload)
        return
      }
  
      this.ws.send(payload)
    }
  
    disconnect() {
      if (!this.ws) return
      this.ws.close()
      this.ws = null
      this.isOpen = false
      this.queue = []
    }
  }