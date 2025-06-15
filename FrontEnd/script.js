let localConnection;
let ws = new WebSocket("ws://localhost:8000/ws");

let config = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
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
      console.error("Erro ao adicionar ICE", e);
    }
  }
};

async function startCall() {
  localConnection = new RTCPeerConnection(config);

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  stream.getTracks().forEach(track => localConnection.addTrack(track, stream));

  localConnection.onicecandidate = ({ candidate }) => {
    if (candidate) {
      ws.send(JSON.stringify({ type: "candidate", candidate }));
    }
  };

  localConnection.ontrack = (event) => {
    const remoteAudio = document.getElementById("remoteAudio");
    remoteAudio.srcObject = event.streams[0];
  };

  const offer = await localConnection.createOffer();
  await localConnection.setLocalDescription(offer);
  ws.send(JSON.stringify(offer));
}
