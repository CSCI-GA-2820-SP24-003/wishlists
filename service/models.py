"""
Models for wishlist and wishlist items
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

# Initializing sql alchemy application
def init_db(app):
    Wishlist.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Wishlist(db.Model):
    """
    Class that represents a wishlist

    Schema Description:
    id = primary key for Wishlist table
    name = user-assigned wishlist name
    description = a short note user can add for the wishlist
    username = username of the customer who owns the wishlist
    created_at = timestamp field to store when wishlist was created
    last_updated_at = timestamp field to store when wishlist was last updated
    is_public = boolean flag to check visibility of the wishlist
    """

    app = None

    ##################################################
    # Wishlist Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)                
    name = db.Column(db.String(255), nullable=False)            
    description = db.Column(db.String(255))      
    username = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    last_updated_at = db.Column(db.DateTime, server_default=db.func.now())
    is_public = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a wishlist and add it to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a wishlist to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """ Removes a wishlist from the data store """
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """ Serializes a wishlist into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "username": self.username,
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
            "is_public": self.is_public
        }

    def deserialize(self, data):
        """
        Deserializes a wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid wishlist: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app):
        """Initializing the database session"""
        logger.info("Initializing the database")
        cls.app = app
        """Initializing SQL Alchemy"""
        db.init_app(app)
        app.app_context().push()
        """Create tables on SQL Alchemy"""
        db.create_all()

    @classmethod
    def all(cls):
        """ Returns all of the wishlists in the database """
        logger.info("Processing all wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a wishlist by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Return all wishlists with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
    
    @classmethod
    def find_for_user(cls, username):
        """Return all wishlists for a specific user"""
        logger.info("Processing lookup for user %s ...", username)
        return cls.query.filter(cls.username == username)
