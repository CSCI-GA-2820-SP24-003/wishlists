"""
Models for wishlist and wishlist items

All of the models are stored in this package
"""

from .persistent_base import db, DataValidationError
from .wishlist import Wishlist
from .wishlist_item import WishListItem
