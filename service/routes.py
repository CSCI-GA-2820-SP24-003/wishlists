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

# cspell: ignore jsonify, Rofrano, wishlistitem

"""
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete wishlist and wishlist items from the account in a e-commerce website.
"""

from flask import jsonify, request, abort, url_for
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, WishlistItem
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
    wishlists = []

    name = request.args.get("name")
    username = request.args.get("username")
    if name:
        wishlists = Wishlist.find_by_name(name)
    elif username:
        wishlists = Wishlist.find_for_user(username)
    else:
        wishlists = Wishlist.all()

    # Return as an array of dictionaries
    results = [wishlist.serialize() for wishlist in wishlists]

    return jsonify(results), status.HTTP_200_OK


@app.route("/wishlists", methods=["POST"])
def create_wishlist():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based on the data in the body that is posted.
    """
    app.logger.info("Request to Create a wishlist")
    check_content_type("application/json")

    wishlist_data = request.get_json()

    # Extract username and name from the request data
    username = wishlist_data.get('username')
    name = wishlist_data.get('name')

    # Check if a wishlist with the same username and name already exists
    existing_wishlist = Wishlist.query.filter_by(username=username, name=name).first()

    if existing_wishlist:
        # If a wishlist with the same username and name already exists, return an error response
        message = {"error": "A wishlist with the same name already exists for this user."}
        return jsonify(message), status.HTTP_409_CONFLICT

    # If no existing wishlist is found, proceed to create a new one
    wishlist = Wishlist()
    wishlist.deserialize(wishlist_data)
    wishlist.create()
    message = wishlist.serialize()

    # Set the location URL
    location_url = url_for("list_wishlists", wishlist_id=wishlist.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


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
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
# pylint: disable=redefined-builtin
def delete_wishlist(wishlist_id):
    """
    Delete a wishlist
    This endpoint will delete a Wishlist based on the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", wishlist_id)

    # Retrieve the wishlist from DB and delete it
    wishlist_to_delete = Wishlist.find(wishlist_id)
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
    item = WishlistItem()
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

    product_name = request.args.get("product_name")
    items = []
    if product_name:
        items = WishlistItem.find_by_product_name(product_name, wishlist_id)
    else:
        items = wishlist.wishlist_items

    # Get the items for the wishlist
    results = [item.serialize() for item in items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE AN ITEM FROM WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/items/<int:wishlistitem_id>", methods=["GET"])
# pylint: disable=redefined-builtin
def get_wishlist_item(wishlist_id, wishlistitem_id):
    """
    This endpoint returns just an item
    """
    app.logger.info(
        "Request to retrieve item %s for Wishlist id: %s",
        (wishlistitem_id, wishlist_id),
    )

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id='{wishlist_id}' could not be found.",
        )

    # See if the item exists and abort if it doesn't
    item = WishlistItem.find(wishlistitem_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{wishlistitem_id}' could not be found.",
        )

    # An extra check to verify that item belongs to wishlist id provided
    if wishlist_id != item.wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id='{wishlistitem_id}' could not be found inside wishlist with id='{wishlist_id}",
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


@app.route(
    "/wishlists/<int:wishlist_id>/items/<int:wishlistitem_id>", methods=["DELETE"]
)
# pylint: disable=redefined-builtin
def delete_wishlist_item(wishlist_id, wishlistitem_id):
    """
    Delete a wishlist item

    This endpoint will delete a wishlist item based the id specified in the path
    """
    app.logger.info(
        "Request to delete wishlist item  %s for wishlist  id: %s",
        (wishlistitem_id, wishlist_id),
    )

    # See if the wishlist item  exists and delete it if it does
    wishlist_item = WishlistItem.find(wishlistitem_id)
    if wishlist_item:
        wishlist_item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE WISHLIST ITEMS
######################################################################


@app.route("/wishlists/<int:wishlist_id>/items/<int:wishlistitem_id>", methods=["PUT"])
def update_wishlist_items(wishlist_id, wishlistitem_id):
    """
    Update a Wishlist Item
    This endpoint will update a wishlist item based the body that is posted
    """
    app.logger.info(
        "Request to update a wishlist item %s for Wishlist id: %s",
        (wishlistitem_id, wishlist_id),
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
    item = WishlistItem.find(wishlistitem_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{wishlistitem_id}' could not be found in the Wishlist with id '{wishlist_id}'.",
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
    item.id = wishlistitem_id
    item.update()
    return jsonify(item.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                A C T I O N    R O U T E S
# ---------------------------------------------------------------------

######################################################################
# PUBLISH A WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/publish", methods=["PUT"])
def publish_wishlist(wishlist_id):
    """
    Publishes a Wishlist

    This endpoint will make a Wishlist publicly visible for all users
    """
    app.logger.info("Request to publish wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # publishing the wishlist
    wishlist.is_public = True
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# UNPUBLISH A WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/unpublish", methods=["PUT"])
def unpublish_wishlist(wishlist_id):
    """
    Unpublishes a Wishlist
    This endpoint will make a wishlist not visible to the public anymore
    """
    app.logger.info("Request to unpublish wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # publishing the wishlist
    wishlist.is_public = False
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK
