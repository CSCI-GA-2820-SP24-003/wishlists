from datetime import datetime, timezone
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
from decimal import Decimal
from service.models import Wishlist, WishListItem


class WishlistFactory(factory.Factory):
    """Creates fake wishlists that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    username = factory.Faker("word")
    created_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    last_updated_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    is_public = FuzzyChoice(choices=[True, False])

    @factory.post_generation
    def wishlist_items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the wishlist items list"""
        if not create:
            return

        if extracted:
            self.wishlist_items = extracted

class WishListItemFactory(factory.Factory):
    """Creates fake wishlist items that you don't have to feed"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Maps factory to wishlist item data model"""

        model = WishListItem

    id = factory.Sequence(lambda n: n)
    wishlist_id = None
    product_id = factory.Faker('random_int', min=1, max=9999)
    product_name = factory.Faker("word")
    product_description = factory.Faker("sentence")
    product_price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True, min_value=Decimal('10.00'), max_value=Decimal('1000.00'))
    created_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    last_updated_at = FuzzyDateTime(datetime(2000, 1, 1, tzinfo=timezone.utc))
    wishlist = factory.SubFactory(WishlistFactory)
