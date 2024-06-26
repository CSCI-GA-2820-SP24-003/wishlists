######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""
Wishlist steps

Steps file for wishlists.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following wishlists")
def step_impl(context):
    """Delete all the Wishlists and load the new ones"""

    # List all the wishlists and delete them one by one
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK

    for wishlist in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{wishlist['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    for row in context.table:
        payload = {
            "username": row["username"],
            "name": row["name"],
            "is_public": row["is_public"] in ["True", "true", "1"],
            "description": row["description"],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED
