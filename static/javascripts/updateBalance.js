let balanceInterval;

document.getElementById('account-choice').addEventListener('change', function() {
    // Clear the existing interval
    if (balanceInterval) {
        clearInterval(balanceInterval);
    }

    // If an account is selected, start the interval
    if (this.value) {
        balanceInterval = setInterval(updateBalance, 1000);
    }
});

function updateBalance() {
    fetch('/get_balance')
        .then(response => response.json())
        .then(data => {
            // Update the balance display
            document.getElementById('balance-display').textContent = 'Your Balance: $' + data.balance;
        })
        .catch(error => {
            // Handle the error
            console.error('Error:', error);
        });
}