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

"""
Test cases for Address Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, WishListItem, db
from tests.factories import WishlistFactory, WishListItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        W I S H L I S T  I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestWishListItem(TestCase):
    """WishlistItem Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishListItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize_an_wishlist_item(self):
        """It should serialize an wishlist item"""
        wishlist_item = WishListItemFactory()
        serial_wishlist_item = wishlist_item.serialize()
        self.assertEqual(serial_wishlist_item["id"], wishlist_item.id)
        self.assertEqual(serial_wishlist_item["wishlist_id"], wishlist_item.wishlist_id)
        self.assertEqual(serial_wishlist_item["product_id"], wishlist_item.product_id)
        self.assertEqual(serial_wishlist_item["product_name"], wishlist_item.product_name)
        self.assertEqual(serial_wishlist_item["product_description"], wishlist_item.product_description)
        self.assertEqual(serial_wishlist_item["product_price"], wishlist_item.product_price)
        self.assertEqual(serial_wishlist_item["created_at"], wishlist_item.created_at.isoformat())
        self.assertEqual(serial_wishlist_item["last_updated_at"], wishlist_item.last_updated_at.isoformat())


    def test_deserialize_an_wishlist_item(self):
        """It should deserialize an wishlist item"""
        wishlist_item = WishListItemFactory()
        wishlist_item.create()
        new_wishlist_item = WishListItem()
        new_wishlist_item.deserialize(wishlist_item.serialize())
        self.assertEqual(new_wishlist_item.id, wishlist_item.id)
        self.assertEqual(new_wishlist_item.wishlist_id, wishlist_item.wishlist_id)
        self.assertEqual(new_wishlist_item.product_id, wishlist_item.product_id)
        self.assertEqual(new_wishlist_item.product_name, wishlist_item.product_name)
        self.assertEqual(new_wishlist_item.product_description, wishlist_item.product_description)
        self.assertEqual(new_wishlist_item.product_price, wishlist_item.product_price)
        self.assertEqual(new_wishlist_item.created_at, wishlist_item.created_at)
        self.assertEqual(new_wishlist_item.last_updated_at, wishlist_item.last_updated_at)