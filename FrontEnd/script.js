let username;
let ws;
let localStream;
const connections = {}; // username -> RTCPeerConnection
const remoteAudios = {}; // username -> <audio>

const config = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
};

async function startCall() {
  username = document.getElementById("username").value;
  if (!username) {
    alert("Digite seu nome!");
    return;
  }

  ws = new WebSocket(`wss://projeto-aie1.onrender.com/ws/${username}`);

  ws.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    const from = data.from;
    if (data.type === "online-users") {
      document.getElementById("userList").innerHTML = "";
      data.users.forEach(user => {
        addUserToList(user);
      });
    }


    if (data.type === "user-joined") {
      addUserToList(data.username);
      await createConnection(data.username, true);
    }

    function addUserToList(username) {
      if (document.getElementById(`user-${username}`)) return;

      const li = document.createElement("li");
      li.id = `user-${username}`;
      li.textContent = `🟢 ${username} está online`;
      document.getElementById("userList").appendChild(li);
    }


    if (data.type === "offer") {
      await createConnection(from, false);
      await connections[from].setRemoteDescription(new RTCSessionDescription(data.offer));
      const answer = await connections[from].createAnswer();
      await connections[from].setLocalDescription(answer);
      ws.send(JSON.stringify({ type: "answer", answer, target: from }));
    }

    if (data.type === "answer") {
      await connections[from].setRemoteDescription(new RTCSessionDescription(data.answer));
    }

    if (data.type === "candidate") {
      if (data.candidate) {
        try {
          await connections[from].addIceCandidate(new RTCIceCandidate(data.candidate));
        } catch (err) {
          console.error("Erro ICE", err);
        }
      }
    }

    if (data.type === "user-left") {
      if (connections[data.username]) {
        connections[data.username].close();
        delete connections[data.username];
        document.getElementById(`user-${data.username}`)?.remove();
        document.getElementById(`audio-${data.username}`)?.remove();
      }
    }
  };

  ws.onopen = async () => {
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  };
}

async function createConnection(peerUsername, isInitiator) {
  if (connections[peerUsername]) return;

  const pc = new RTCPeerConnection(config);
  connections[peerUsername] = pc;

  localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

  pc.onicecandidate = ({ candidate }) => {
    if (candidate) {
      ws.send(JSON.stringify({ type: "candidate", candidate, target: peerUsername }));
    }
  };

  pc.ontrack = (event) => {
    if (!remoteAudios[peerUsername]) {
      const audio = document.createElement("audio");
      audio.id = `audio-${peerUsername}`;
      audio.autoplay = true;
      document.body.appendChild(audio);
      remoteAudios[peerUsername] = audio;
    }
    remoteAudios[peerUsername].srcObject = event.streams[0];
  };

  if (isInitiator) {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    ws.send(JSON.stringify({ type: "offer", offer, target: peerUsername }));
  }
}

function leaveCall() {
  for (const peer in connections) {
    connections[peer].close();
    document.getElementById(`audio-${peer}`)?.remove();
  }
  if (ws) {
    ws.close();
  }
  if (localStream) {
    localStream.getTracks().forEach(track => track.stop());
  }
  alert("Você saiu da chamada.");
}
