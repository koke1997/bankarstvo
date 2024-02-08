$('#accountDropdown').on('change', function() {
    // Remove the 'selected' class from all options
    $(this).find('option').removeClass('selected');

    // Add the 'selected' class to the selected option
    $(this).find('option:selected').addClass('selected');
});