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

# cspell:ignore jsonify, wishlist, app, id
# pylint: disable=W0622
"""
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlists
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
        jsonify(
            name="Wishlists Service",
            version="0.1.0",
            # url=url_for("list_wishlists", _external=True),
            url="/",
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# Read a single Wishlist
######################################################################
@app.route("/wishlists/<int:id>", methods=["GET"])
def read_wishlist(id: int):
    """Read a single Wishlist API endpoint"""
    app.logger.info("Request to Read a wishlist with id: %s", id)
    wishlist = Wishlist.find(id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{id}' was not found.")
    return jsonify(wishlist.serialize()), status.HTTP_200_OK
