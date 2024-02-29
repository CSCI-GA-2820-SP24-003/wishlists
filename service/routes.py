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

# cspell: ignore jsonify

"""
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Pets from the inventory of pets in the PetShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Wishlist
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S   F O R   W I S H L I S T  
######################################################################


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
    # TODO: set the location URL
    # location_url = url_for("get_wishlist", wishlist_id=wishlist.id, _external=True)
    location_url = "/wishlists/" + str(wishlist.id)
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
    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK

######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:id>", methods=["DELETE"])
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
