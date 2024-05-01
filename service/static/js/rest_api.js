$(function () {

    let BASE_URL = "/api/wishlists";

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
        table += '<th class="col-md-4">Created At</th>'
        table += '<th class="col-md-4">Last Updated At</th>'
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
            url: `${BASE_URL}`,
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

        if (!wishlist_id) {
            flash_message("Missing ID");
            return; // Exit function if ID is missing
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/${wishlist_id}`,
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

    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {
        clear_search_result();
        let name = $("#name").val();
        let username = $("#username").val();
        let description = $("#description").val();
        let is_public = $("#is_public").val() == "true";
        let id = $("#id").val();
        let data = {
            "name": name,
            "username": username,
            "is_public": is_public,
            "description": description
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: BASE_URL + "/" + id,
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
    // Search for a wishlist
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#name").val();
        let username = $("#username").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (username) {
            if (queryString.length > 0) {
                queryString += '&username=' + username
            } else {
                queryString += 'username=' + username
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Wishlist ID</th>'
            table += '<th class="col-md-2">Username</th>'
            table += '<th class="col-md-2">Wishlist Name</th>'
            table += '<th class="col-md-2">Public Wishlist</th>'
            table += '<th class="col-md-2">Wishlist Description</th>'
            table += '<th class="col-md-4">Created At</th>'
            table += '<th class="col-md-4">Last Updated At</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            for(let i = 0; i < res.length; i++) {
                let wishlist = res[i];
                table +=  `<tr id="row_${i}"><td>${wishlist.id}</td><td>${wishlist.username}</td><td>${wishlist.name}</td><td>${wishlist.is_public}</td><td>${wishlist.description}</td><td>${wishlist.created_at}</td><td>${wishlist.last_updated_at}</td></tr>`;
                if (i == 0) {
                    firstWishlist = wishlist;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_form_data(firstWishlist)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        let wishlist_id = $("#id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Publish a Wishlist
    // ****************************************

    $("#publish-btn").click(function () {
        $("#flash_message").empty();
        let wishlist_id = $("#id").val();
        //alert if the wishlist id is empty
        if (wishlist_id == "") {
            flash_message("Please enter a Wishlist ID")
            return
        }

        let ajax = $.ajax({
            type: "PUT",
            url: `${BASE_URL}/${wishlist_id}/publish`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Published!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });


    // ****************************************
    // Unpublish a Wishlist
    // ****************************************

    $("#unpublish-btn").click(function () {
        $("#flash_message").empty();
        let wishlist_id = $("#id").val();
        //alert if the wishlist id is empty
        if (wishlist_id == "") {
            flash_message("Please enter a Wishlist ID")
            return
        }

        let ajax = $.ajax({
            type: "PUT",
            url: `${BASE_URL}/${wishlist_id}/unpublish`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been unpublished!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
})