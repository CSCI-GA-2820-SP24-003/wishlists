$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#id").val(res.id);
        $("#username").val(res.username);
        $("#name").val(res.name);
        $("#description").val(res.description);
        if (res.is_public == true) {
            $("#is_public").val("true");
        } else {
            $("#is_public").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#id").val("");
        $("#username").val("");
        $("#name").val("");
        $("#description").val("");
        $("#is_public").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function clear_search_result() {
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">'
        table += '<thead><tr>'
        table += '<th class="col-md-1">Wishlist ID</th>'
        table += '<th class="col-md-1">Username</th>'
        table += '<th class="col-md-4">Wishlist Name</th>'
        table += '<th class="col-md-4">Public Wishlist</th>'
        table += '<th class="col-md-4">Wishlist Description</th>'
        table += '</tr></thead><tbody>'
        table += '</tbody></table>';
        $("#search_results").append(table);
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {
        clear_search_result();
        let name = $("#name").val();
        let username = $("#username").val();
        let description = $("#description").val();
        let is_public = $("#is_public").val() == "true";

        let data = {
            "name": name,
            "username": username,
            "is_public": is_public,
            "description": description
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {
        clear_search_result();
        let wishlist_id = $("#id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

})