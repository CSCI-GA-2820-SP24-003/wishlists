"""
Test cases for Wishlist Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Wishlist, WishListItem, DataValidationError, db
from tests.factories import WishlistFactory, WishListItemFactory

# cspell: ignore psycopg testdb, psycopg

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
        db.session.query(WishListItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should create a wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name,
            is_public=fake_wishlist.is_public,
            username=fake_wishlist.username,
            description=fake_wishlist.description,
            created_at=fake_wishlist.created_at,
            last_updated_at=fake_wishlist.last_updated_at,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.username, fake_wishlist.username)
        self.assertEqual(wishlist.description, fake_wishlist.description)
        self.assertEqual(wishlist.created_at, fake_wishlist.created_at)
        self.assertEqual(wishlist.last_updated_at, fake_wishlist.last_updated_at)
        self.assertEqual(wishlist.wishlist_items, fake_wishlist.wishlist_items)

    def test_add_a_wishlist(self):
        """It should Create a wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    @patch("service.models.db.session.commit")
    def test_add_wishlist_failed(self, exception_mock):
        """It should not create a wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.create)

    def test_read_wishlist(self):
        """It should Read a wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.name, wishlist.name)
        self.assertEqual(found_wishlist.username, wishlist.username)
        self.assertEqual(found_wishlist.description, wishlist.description)
        self.assertEqual(found_wishlist.created_at, wishlist.created_at)
        self.assertEqual(found_wishlist.last_updated_at, wishlist.last_updated_at)
        self.assertEqual(found_wishlist.is_public, wishlist.is_public)
        self.assertEqual(found_wishlist.wishlist_items, [])

    def test_update_wishlist(self):
        """It should Update a wishlist"""
        wishlist = WishlistFactory(name="Sports")
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(wishlist.name, "Sports")

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        wishlist.name = "Clothes"
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.name, "Clothes")

    @patch("service.models.db.session.commit")
    def test_update_wishlist_failed(self, exception_mock):
        """It should not update a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    def test_delete_a_wishlist(self):
        """It should Delete a wishlist from the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        wishlist = wishlists[0]
        wishlist.delete()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 0)

    @patch("service.models.db.session.commit")
    def test_delete_wishlist_failed(self, exception_mock):
        """It should not delete a wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.delete)

    def test_list_all_wishlists(self):
        """It should List all Wishlists in the database"""
        wishlist = Wishlist.all()
        self.assertEqual(wishlist, [])
        for dummy_wishlist in WishlistFactory.create_batch(5):
            dummy_wishlist.create()
        # Assert that there are not 5 accounts in the database
        all_wishlists = Wishlist.all()
        self.assertEqual(len(all_wishlists), 5)

    def test_find_by_name(self):
        """It should Find a wishlist by name"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name)

    def test_find_by_user(self):
        """It should Find a wishlist by username"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_for_user(wishlist.username)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.username, wishlist.username)

    def test_serialize_a_wishlist(self):
        """It should Serialize a Wishlist with WishlistItem"""
        wishlist = WishlistFactory()
        item = WishListItemFactory()
        wishlist.wishlist_items.append(item)
        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist["id"], wishlist.id)
        self.assertEqual(serial_wishlist["name"], wishlist.name)
        self.assertEqual(serial_wishlist["username"], wishlist.username)
        self.assertEqual(serial_wishlist["description"], wishlist.description)
        self.assertEqual(serial_wishlist["created_at"], wishlist.created_at.isoformat())
        self.assertEqual(serial_wishlist["last_updated_at"], wishlist.last_updated_at.isoformat())
        self.assertEqual(serial_wishlist["is_public"], wishlist.is_public)
        self.assertEqual(len(serial_wishlist["wishlist_items"]), 1)

        items = serial_wishlist["wishlist_items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["wishlist_id"], item.wishlist_id)
        self.assertEqual(items[0]["product_id"], item.product_id)
        self.assertEqual(items[0]["product_name"], item.product_name)
        self.assertEqual(items[0]["product_description"], item.product_description)
        self.assertEqual(items[0]["product_price"], item.product_price)
        self.assertEqual(items[0]["created_at"], item.created_at.isoformat())
        self.assertEqual(items[0]["last_updated_at"], item.last_updated_at.isoformat())

    def test_deserialize_a_wishlist(self):
        """It should Deserialize a wishlist"""
        wishlist = WishlistFactory()
        wishlist.wishlist_items.append(WishListItemFactory())
        wishlist.create()
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.name, wishlist.name)
        self.assertEqual(new_wishlist.username, wishlist.username)
        self.assertEqual(new_wishlist.is_public, wishlist.is_public)
        self.assertEqual(new_wishlist.description, wishlist.description)
        self.assertEqual(new_wishlist.created_at, wishlist.created_at.isoformat())
        self.assertEqual(new_wishlist.last_updated_at, wishlist.last_updated_at.isoformat())

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = WishListItem()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = WishListItem()
        self.assertRaises(DataValidationError, item.deserialize, [])
