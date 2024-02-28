from datetime import datetime, timezone
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
from service.models import Wishlist


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
