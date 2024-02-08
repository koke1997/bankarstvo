// websocket_client.js
const socket = new WebSocket('ws://localhost:8765');

socket.addEventListener('message', function (event) {
    const data = JSON.parse(event.data);
    console.log('Balance: ', data.balance);
    console.log('Transactions: ', data.transactions);
});

socket.send('Hello Server!');