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

  ws = new WebSocket(`ws://localhost:8000/ws/${username}`);

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

  ws.onopen = async () => {
    localConnection = new RTCPeerConnection(config);

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => localConnection.addTrack(track, stream));

    localConnection.onicecandidate = ({ candidate }) => {
      if (candidate) {
        ws.send(JSON.stringify({ type: "candidate", candidate }));
      }
    };

    localConnection.ontrack = (event) => {
      document.getElementById("remoteAudio").srcObject = event.streams[0];
    };

    const offer = await localConnection.createOffer();
    await localConnection.setLocalDescription(offer);
    ws.send(JSON.stringify(offer));
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
