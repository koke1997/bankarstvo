// Path: /app/assets/javascripts/transfer.js
$(document).ready(function() {
    // Handle "Transfer" button click
    $("#transfer-button").click(function(e) {
        e.preventDefault();

        $.ajax({
            url: '/transfer',
            type: 'POST',
            data: {
                recipient_account_id: $("#search-results-dropdown").val(),
                amount: $("#transfer_amount").val()
            },
            success: function(response) {
                console.log("Transfer successful.");
                // Handle successful transfer, e.g. show a success message
            },
            error: function(response) {
                console.log("Transfer failed.");
                // Handle failed transfer, e.g. show an error message
            }
        });
    });
});