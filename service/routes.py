######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# cspell: ignore jsonify, Rofrano

"""
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete wishlist and wishlist items from the account in a e-commerce website.
"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, WishListItem
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    data = {
        "name": "Wishlist REST API service",
        "version": "1.0.0",
        "description": "A RESTful API for managing user wishlists and wishlist items.",
    }

    json_response = jsonify(data)
    return (json_response, status.HTTP_200_OK)


######################################################################
#  R E S T   A P I   E N D P O I N T S   F O R   W I S H L I S T
######################################################################


######################################################################
# LIST ALL Wishlists
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
    app.logger.info("Request for Wishlists list")
    accounts = []

    accounts = Wishlist.all()

    # Return as an array of dictionaries
    results = [account.serialize() for account in accounts]

    return jsonify(results), status.HTTP_200_OK


@app.route("/wishlists", methods=["POST"])
def create_wishlist():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to Create a wishlist")
    check_content_type("application/json")
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()
    message = wishlist.serialize()
    # set the location URL
    location_url = url_for("list_wishlists", wishlist_id=wishlist.id, _external=True)
    # location_url = "/wishlists/" + str(wishlist.id)
    return (jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlist(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a Wishlist based on the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # Update from the json in the body of the request
    # original_data = wishlist.serialize()
    data = request.get_json()
    # data["created_at"] = original_data["created_at"]
    wishlist.deserialize(data)
    wishlist.id = wishlist_id
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:id>", methods=["DELETE"])
# pylint: disable=redefined-builtin
def delete_wishlist(id):
    """
    Delete a wishlist
    This endpoint will delete a Wishlist based on the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", id)

    # Retrieve the wishlist from DB and delete it
    wishlist_to_delete = Wishlist.find(id)
    if wishlist_to_delete:
        wishlist_to_delete.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )


# ---------------------------------------------------------------------
#                I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# ADD AN ITEM TO A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_wishlist_item(wishlist_id):
    """
    Create an Item on a Wishlist

    This endpoint will add an item to a Wishlist
    """
    app.logger.info(
        "Request to create a WishlistItem for Wishlist with id: %s", wishlist_id
    )
    check_content_type("application/json")

    # See if the account exists and abort if it doesn't
    # account = Account.find(account_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Create an address from the json data
    item = WishListItem()
    item_data = request.get_json()
    item_data["wishlist_id"] = wishlist_id
    item.deserialize(item_data)
    item.wishlist_id = wishlist_id
    # Append the address to the account
    wishlist.wishlist_items.append(item)
    wishlist.update()

    # Prepare a message to return
    message = item.serialize()
    location_url = url_for(
        "list_wishlist_items", wishlist_id=wishlist.id, item_id=item.id, _external=True
    )

    return (jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# LIST WISHLIST ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_wishlist_items(wishlist_id):
    """Returns all of the Items for a a Wishlist"""
    app.logger.info("Request for all Items for Wishlist with id: %s", wishlist_id)

    # Abort if the wishlist doesn't exist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get the items for the wishlist
    results = [items.serialize() for items in wishlist.wishlist_items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN ITEM FROM WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/items/<int:id>", methods=["GET"])
# pylint: disable=redefined-builtin
def get_wishlist_item(wishlist_id, id):
    """
    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve item %s for Wishlist id: %s", (id, wishlist_id)
    )

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id='{wishlist_id}' could not be found.",
        )

    # See if the item exists and abort if it doesn't
    item = WishListItem.find(id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{id}' could not be found.",
        )

    # An extra check to verify that item belongs to wishlist id provided
    if wishlist_id != item.wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{id}' could not be found inside wishlist with id='{wishlist_id}",
        )

    return jsonify(item.serialize()), status.HTTP_200_OK


@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist

    This endpoint will return a wishlist based on it's id
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


#####################################################################
# DELETE AN ITEM FROM WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/items/<int:id>", methods=["DELETE"])
# pylint: disable=redefined-builtin
def delete_wishlist_item(wishlist_id, id):
    """
    Delete a wishlist item

    This endpoint will delete a wishlist item based the id specified in the path
    """
    app.logger.info(
        "Request to delete wishlist item  %s for wishlist  id: %s", (id, wishlist_id)
    )

    # See if the wishlist item  exists and delete it if it does
    wishlist_item = WishListItem.find(id)
    if wishlist_item:
        wishlist_item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE WISHLIST ITEMS
######################################################################


@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["PUT"])
def update_wishlist_items(wishlist_id, item_id):
    """
    Update a Wishlist Item
    This endpoint will update a wishlist item based the body that is posted
    """
    app.logger.info(
        "Request to update a wishlist item %s for Wishlist id: %s",
        (item_id, wishlist_id),
    )
    check_content_type("application/json")
    wishlist = Wishlist.find(wishlist_id)
    # see if the wishlist exists and abort if it doesn't
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    # See if the item exists and abort if it doesn't
    item = WishListItem.find(item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found in the Wishlist with id '{wishlist_id}'.",
        )
    if wishlist_id != item.wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{id}' could not be found inside wishlist with id='{wishlist_id}",
        )
    # Update from the json in the body of the request
    data = request.get_json()
    # original_data = item.serialize()
    # data["created_at"] = original_data["created_at"]
    item.deserialize(data)
    item.id = item_id
    item.update()
    return jsonify(item.serialize()), status.HTTP_200_OK
