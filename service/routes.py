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

# from flask import jsonify, request, abort, url_for
from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.models import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for Wishlists service"""
    return app.send_static_file("index.html")


############################################################
# HEALTH ENDPOINT
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S   F O R   W I S H L I S T
######################################################################


# Define the Wishlist Item model so that the docs can reflect what can be sent
create_item_model = api.model(
    "Item",
    {
        "id": fields.Integer(required=True, description="Id of the wishlist item"),
        "wishlist_id": fields.Integer(required=True, description="Id of the wishlist"),
        "product_id": fields.Integer(required=True, description="Id of the product"),
        "product_name": fields.String(required=True, description="Name of the product"),
        "product_description": fields.String(
            required=True, description="Description of the product"
        ),
        "product_price": fields.Float(
            required=True, description="Price of the product"
        ),
        "created_at": fields.DateTime(
            required=True, description="Time when item was created"
        ),
        "last_updated_at": fields.DateTime(
            required=True, description="Time when item was last updated"
        ),
    },
)

item_model = api.inherit(
    "ItemModel",
    create_item_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The Id of the item assigned internally by the service",
        ),
        "wishlist_id": fields.Integer(
            readOnly=True,
            description="The Id of the wishlist to which the item belongs",
        ),
    },
)

# Item Query String Arguments
item_args = reqparse.RequestParser()
item_args.add_argument(
    "product_name",
    type=str,
    location="args",
    required=False,
    help="Filter Wishlists by product name",
)

# Define the Wishlist model so that the docs can reflect what can be sent
create_wishlist_model = api.model(
    "Wishlist",
    {
        "username": fields.String(
            required=True, description="Username of the wishlist owner"
        ),
        "name": fields.String(required=True, description="Name of the wishlist"),
        "is_public": fields.Boolean(
            required=True, description="Is the wishlist published?"
        ),
        "description": fields.String(
            required=False, description="Description of the wishlist"
        ),
        "wishlist_items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="Items in the wishlist",
        ),
        "created_at": fields.DateTime(
            required=True, description="Time when wishlist was created"
        ),
        "last_updated_at": fields.DateTime(
            required=True, description="Time when wishlist was last updated"
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The Id of the wishlist assigned internally by the service",
        ),
        "wishlist_items": fields.List(
            fields.Nested(item_model),
            required=False,
            description="Items in the wishlist",
        ),
    },
)

# Wishlist Query String Arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="Filter Wishlists by name"
)
wishlist_args.add_argument(
    "username",
    type=str,
    location="args",
    required=False,
    help="Filter Wishlists by username",
)


######################################################################
# PATH: /wishlists/<wishlist_id>
######################################################################
@api.route("/wishlists/<int:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """Handles all interactions with a Wishlist"""

    # ---------------------------------------------------------------------
    #                READ A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("get_wishlists")
    @api.response(404, "Wishlist could not be found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Get a Wishlist
        This endpoint will return a Wishlist based on the id specified in the path
        """
        app.logger.info("Request for Wishlist with id: %s", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    # ---------------------------------------------------------------------
    #                DELETE A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("delete_wishlists", security="apikey")
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """
        Delete a PWishlist

        This endpoint will delete a wishlist based the id specified in the path
        """
        app.logger.info(f"Request to delete wishlist with id: {wishlist_id}")

        wishlist_to_delete = Wishlist.find(wishlist_id)
        if wishlist_to_delete:
            wishlist_to_delete.delete()

        app.logger.info(f"Wishlist with ID: {wishlist_id} deleted")
        return "", status.HTTP_204_NO_CONTENT

    # ---------------------------------------------------------------------
    #                UPDATE A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.response(409, "Wishlist name already exists")
    @api.response(415, "Invalid header content-type")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist
        This endpoint will update a Wishlist based on the data in the body
        """
        app.logger.info("Request to update wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        # Retrieve the wishlist if it exists
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                "Wishlist with id '{wishlist_id}' was not found.",
            )

        # Update the wishlist with the data posted
        body = api.payload

        # Checking for conflicts when renaming
        existing_wishlist = Wishlist.query.filter_by(
            username=body["username"], name=body["name"]
        ).first()

        if existing_wishlist is not None:
            abort(
                status.HTTP_409_CONFLICT,
                "Duplicate Wishlist",
            )

        wishlist.deserialize(body)
        wishlist.update()

        return wishlist.serialize(), status.HTTP_200_OK


######################################################################
# PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    # ---------------------------------------------------------------------
    #                LIST ALL WISHLISTS
    # ---------------------------------------------------------------------
    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """
        Return all wishlists
        This endpoint will return all Wishlists in the database
        """
        app.logger.info("Request for a list of Wishlists")

        # Filtering by wishlist name, if needed
        args = wishlist_args.parse_args()
        if args["name"]:
            wishlists = Wishlist.find_by_name(args["name"])
            if len(wishlists) == 0:
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"wishlist with {args['name']} doesn't exist.",
                )
            wishlists = [wishlists[0].serialize()]
        elif args["username"]:
            wishlists = Wishlist.find_for_user(args["username"])
            if len(wishlists) == 0:
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"User = {args['username']} doesn't have any wishlist.",
                )
            wishlists = [wishlists[0].serialize()]
        else:
            # Return as an array of JSON
            wishlists = [wishlist.serialize() for wishlist in Wishlist.all()]

        return wishlists, status.HTTP_200_OK

    # ---------------------------------------------------------------------
    #                CREATE A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("create_wishlists")
    @api.response(400, "Invalid wishlist request body")
    @api.response(409, "Wishlist name taken")
    @api.response(415, "Invalid header content-type")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Create a wishlist
        This endpoint will create a Wishlist based on the data in the body that is posted
        """
        app.logger.info("Request to create a Wishlist")
        check_content_type("application/json")

        # Create the wishlist
        wishlist = Wishlist()
        data = api.payload
        wishlist.deserialize(data)
        existing_wishlist = Wishlist.query.filter_by(
            username=data["username"], name=data["name"]
        ).first()

        if existing_wishlist:
            abort(status.HTTP_409_CONFLICT, "Duplicate Wishlist")
        else:
            wishlist.create()

        res = wishlist.serialize()
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )
        return res, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# PATH: /wishlists/<wishlist_id>/publish
######################################################################


@api.route("/wishlists/<int:wishlist_id>/publish")
@api.param("wishlist_id", "The Wishlist identifier")
class PublishResource(Resource):
    """Publish action on a Wishlist"""

    # ---------------------------------------------------------------------
    #                PUBLISH A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("publish_wishlist")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Publish a wishlist
        This action route will publish the given Wishlist
        """
        app.logger.info("Request to publish wishlist with id: %s", wishlist_id)
        # Retrieve the wishlist to be pubblished, and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist not found.")
        # Publish the fetched wishlist
        wishlist.is_public = True
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK


######################################################################
# PATH: /wishlists/<wishlist_id>/unpublish
######################################################################


@api.route("/wishlists/<int:wishlist_id>/unpublish")
@api.param("wishlist_id", "The Wishlist identifier")
class UnpublishResource(Resource):
    """Unpublish action on a Wishlist"""

    # ---------------------------------------------------------------------
    #                UNPUBLISH A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("unpublish_wishlist")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Unpublish a wishlist
        This action route will unpublish the given Wishlist
        """
        app.logger.info("Request to unpublish wishlist with id: %s", wishlist_id)
        # Retrieve the wishlist to be unpublished, and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist not found.")
        # Unpublish the fetched wishlist
        wishlist.is_public = False
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK


######################################################################
# PATH: /wishlists/<wishlist_id>/items/<item_id>
######################################################################


@api.route("/wishlists/<int:wishlist_id>/items/<int:item_id>")
@api.param("wishlist_id", "Wishlist identifier")
@api.param("item_id", "Item identifier")
class ItemResource(Resource):
    """Handles all interactions with an Item"""

    # ---------------------------------------------------------------------
    #                READ AN ITEM
    # ---------------------------------------------------------------------
    @api.doc("get_wishlist_item")
    @api.response(404, "Item not found for wishlist")
    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Get an Item
        This endpoint returns the requested item from the specified wishlist
        """
        app.logger.info(
            "Request to retrieve a item with id %s from Wishlist %s",
            item_id,
            wishlist_id,
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id= '{wishlist_id}' could not be found.",
            )

        # See if the product exists, and abort if it does not
        item = WishlistItem.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND, f"Product with id '{item_id}' was not found."
            )

        # An extra check to verify that item belongs to wishlist id provided
        if wishlist_id != item.wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id='{item_id}' could not be found inside wishlist with id='{wishlist_id}",
            )

        return item.serialize(), status.HTTP_200_OK

    # ---------------------------------------------------------------------
    #                UPDATE AN ITEM
    # ---------------------------------------------------------------------
    @api.doc("update_items")
    @api.response(404, "Item not found for wishlist")
    @api.response(400, "Posted Item data not valid")
    @api.response(415, "Invalid header content-type")
    @api.expect(create_item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """
        Update a item
        This endpoint updates the specified product from the given wishlist
        """
        app.logger.info(
            "Request to update product %s in Wishlist %s", item_id, wishlist_id
        )
        check_content_type("application/json")

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # See if the product exists, and abort if it does not
        product = WishlistItem.find(item_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found")

        # An extra check to verify that item belongs to wishlist id provided
        if wishlist_id != product.wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id='{item_id}' could not be found inside wishlist with id='{wishlist_id}",
            )

        original_wishlist_id = product.wishlist_id
        product.deserialize(api.payload)
        product.id = item_id
        product.wishlist_id = original_wishlist_id
        product.update()

        return product.serialize(), status.HTTP_200_OK

    # ---------------------------------------------------------------------
    #                DELETE AN ITEM
    # ---------------------------------------------------------------------
    @api.doc("delete_items")
    @api.response(204, "Item deleted")
    def delete(self, wishlist_id, item_id):
        """
        Remove an item from a wishlist
        This endpoint will remove the given item from the wishlist
        """
        app.logger.info(
            "Request to delete item %s for Wishlist id: %s", item_id, wishlist_id
        )

        # See if the product exists, and delete it if it does
        product = WishlistItem.find(item_id)
        if product:
            product.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# PATH: /wishlists/<wishlist_id>/items
######################################################################


@api.route("/wishlists/<int:wishlist_id>/items", strict_slashes=False)
@api.param("wishlist_id", "Wishlist identifier")
class ItemCollection(Resource):
    """Handles all interactions with collections of Items"""

    # ---------------------------------------------------------------------
    #                LIST ALL ITEMS OF A WISHLIST
    # ---------------------------------------------------------------------
    @api.doc("list_wishlist_items")
    @api.response(404, "Wishlist not found")
    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """
        Return all items in a wishlist
        This endpoint will return all products in the given wishlist
        """
        app.logger.info("Request for all Products in Wishlist with id: %s", wishlist_id)

        # See if the wishlist exists, and abort if it does not
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist not found.")

        res = [item.serialize() for item in wishlist.wishlist_items]

        # Filtering, if needed
        args = item_args.parse_args()
        if args["product_name"]:
            res = [
                product
                for product in res
                if product["product_name"] == str(args["product_name"])
            ]
            if len(res) == 0:
                abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Product with name '{args['product_name']}' cannot be found.",
                )

        return res, status.HTTP_200_OK

    # ---------------------------------------------------------------------
    #                CREATE AN ITEM
    # ---------------------------------------------------------------------
    @api.doc("create_items")
    @api.response(400, "Invalid item request body")
    @api.response(404, "Wishlist id not found")
    @api.response(415, "Invalid header content-type")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Create an Item
        This endpoint will add a product to a wishlist.
        """
        app.logger.info("Request to add a Product to Wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        # See if the wishlist exists, and abort if it does not
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        # Create a product from the JSON data
        item = WishlistItem()
        item.deserialize(api.payload)

        # Adding the item to the wishlist
        wishlist.wishlist_items.append(item)
        wishlist.update()

        message = item.serialize()
        location_url = api.url_for(
            ItemResource, wishlist_id=wishlist.id, item_id=item.id, _external=True
        )
        return message, status.HTTP_201_CREATED, {"Location": location_url}


# ######################################################################
# #  U T I L I T Y   F U N C T I O N S
# ######################################################################


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


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
