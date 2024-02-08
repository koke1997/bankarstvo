        // Path: /app/assets/javascripts/search_accounts.js
        $(document).ready(function() {
            // Hide the account selection field initially
            $("#account_selection").hide();
    
            $("#search-button").click(function(e) {
                e.preventDefault();
    
                $.ajax({
                    url: '/search_accounts',
                    type: 'POST',
                    data: {
                        recipient: $("#recipient-input").val()
                    },
                    success: function(response) {
                        console.log("Success function executed.");
    
                        var dropdown = $("#search-results-dropdown");
                        dropdown.empty();
    
                        // Show the account selection field only if accounts are found
                        if (response.accounts.length > 0) {
                            $.each(response.accounts, function(i, account) {
                                dropdown.append(
                                    $('<option></option>').val(account.account_id).html(account.account_name)
                                );
                            });
    
                            $("#account_selection").show();
                        } else {
                            $("#account_selection").hide();
                        }
                    },
                    error: function(error) {
                        console.log(error);
                        $("#account_selection").hide();
                    }
                });
            });
        });
        // End of javascript