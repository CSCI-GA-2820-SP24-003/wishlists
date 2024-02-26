"""
Test cases for Pet Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Test Cases for Wishlist Model"""

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
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_find_wishlist_by_id(self):
        """It should return a wishlist by id"""
        wishlist = Wishlist(
            name="test wishlist", user_id=1, description="test description"
        )
        wishlist.create()
        result = Wishlist.find(wishlist.id)
        self.assertIsNot(result, None)
        self.assertEqual(result.id, wishlist.id)
        self.assertEqual(result.name, wishlist.name)
        self.assertEqual(result.user_id, wishlist.user_id)
        self.assertEqual(result.description, wishlist.description)
