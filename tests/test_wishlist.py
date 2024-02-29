"""
Test cases for Wishlist Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Wishlist, DataValidationError, db
from tests.factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  W I S H L I S T   M O D E L   T E S T   C A S E S
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

    def test_create_a_wishlist(self):
        """It should Create a WISHLIST and assert that it exists"""
        wishlist_obj = Wishlist(name="Sports", username="user123", is_public=True)
        self.assertTrue(wishlist_obj is not None)
        self.assertEqual(wishlist_obj.id, None)
        self.assertEqual(wishlist_obj.name, "Sports")
        self.assertEqual(wishlist_obj.is_public, True)

    def test_add_a_wishlist(self):
        """It should create a wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist_obj = Wishlist(name="Sports", username="user123", is_public=True)
        self.assertTrue(wishlist_obj is not None)
        self.assertEqual(wishlist_obj.id, None)
        wishlist_obj.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist_obj.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    def test_read_a_wishlist(self):
        """It should read a wishlist"""
        wishlist_fake = WishlistFactory()
        wishlist_fake.id = None
        wishlist_fake.create()
        self.assertIsNotNone(wishlist_fake.id)
        self.assertIsNotNone(wishlist_fake.name)
        self.assertIsNotNone(wishlist_fake.username)

        # Fetch it back - this time from the DB
        found_wishlist = Wishlist.find(wishlist_fake.id)
        self.assertEqual(found_wishlist.id, wishlist_fake.id)
        self.assertEqual(found_wishlist.name, wishlist_fake.name)

    def test_list_all_wishlists(self):
        """It should list all wishlists in the database"""
        all_wishlists = Wishlist.all()
        self.assertEqual(all_wishlists, [])  # empty DB check

        # Create 10 dummy records
        for _ in range(10):
            wishlist = WishlistFactory()
            wishlist.create()

        # See if we get back 10 wishlists
        wishlists_from_db = Wishlist.all()
        self.assertEqual(len(wishlists_from_db), 10)

    def test_update_a_wishlist(self):
        """It should update a wishlist"""
        wishlist_obj = Wishlist(
            name="Sports wishlist", username="user123", is_public=False
        )
        logging.debug(wishlist_obj)
        wishlist_obj.id = None
        wishlist_obj.create()
        logging.debug(wishlist_obj)
        self.assertIsNotNone(wishlist_obj.id)

        # Change is_public field and save it to DB
        wishlist_obj.is_public = True
        original_id = wishlist_obj.id
        wishlist_obj.update()
        self.assertEqual(wishlist_obj.id, original_id)
        self.assertEqual(wishlist_obj.is_public, True)

        # Fetch it back from the DB and read item
        # the id should not change
        # but the is_public data should change
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].id, original_id)
        self.assertEqual(wishlists[0].is_public, True)

    @patch("service.models.db.session.commit")
    def test_update_wishlist_failed(self, exception_mock):
        """It should not update a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    def test_delete_a_wishlist(self):
        """It should delete a wishlist"""
        fake_wishlist = WishlistFactory()
        fake_wishlist.create()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        fake_wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)
