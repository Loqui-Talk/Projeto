let localConnection;
let ws;
let username;
let stream;

const config = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
};

function startCall() {
  username = document.getElementById("username").value;
  if (!username) {
    alert("Digite seu nome!");
    return;
  }

  // ✅ Conectando com o backend no Render (produção)
  ws = new WebSocket(`wss://projeto-aie1.onrender.com/ws/${username}`);

  ws.onopen = async () => {
    console.log("✅ WebSocket conectado com sucesso");

    // Criação da conexão WebRTC
    localConnection = new RTCPeerConnection(config);

    // Captura do áudio local
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => localConnection.addTrack(track, stream));

    // Envio de candidatos ICE (para NAT traversal)
    localConnection.onicecandidate = ({ candidate }) => {
      if (candidate) {
        ws.send(JSON.stringify({ type: "candidate", candidate }));
      }
    };

    // Quando o áudio remoto for recebido
    localConnection.ontrack = (event) => {
      document.getElementById("remoteAudio").srcObject = event.streams[0];
    };

    // Criação da oferta
    const offer = await localConnection.createOffer();
    await localConnection.setLocalDescription(offer);
    ws.send(JSON.stringify(offer));
  };

  ws.onmessage = async (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "offer") {
      await localConnection.setRemoteDescription(new RTCSessionDescription(message));
      const answer = await localConnection.createAnswer();
      await localConnection.setLocalDescription(answer);
      ws.send(JSON.stringify(answer));

    } else if (message.type === "answer") {
      await localConnection.setRemoteDescription(new RTCSessionDescription(message));

    } else if (message.type === "candidate") {
      try {
        await localConnection.addIceCandidate(message.candidate);
      } catch (e) {
        console.error("⚠️ Erro ao adicionar ICE candidate", e);
      }
    }
  };

  ws.onclose = () => {
    console.log("🔌 WebSocket desconectado.");
  };

  ws.onerror = (error) => {
    console.error("❌ Erro na conexão WebSocket:", error);
  };
}

function leaveCall() {
  if (localConnection) {
    localConnection.close();
    localConnection = null;
  }
  if (ws) {
    ws.close();
    ws = null;
  }
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
  alert("Você saiu da chamada.");
}
