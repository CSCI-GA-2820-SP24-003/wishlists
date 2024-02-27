from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Wishlist


class WishlistFactory(factory.Factory):
    """Creates fake wishlists that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    username = factory.Faker("word")
    created_at = FuzzyDate(date(2008, 1, 1))
    last_updated_at = FuzzyDate(date(2008, 1, 1))
    is_public = FuzzyChoice(choices=[True, False])