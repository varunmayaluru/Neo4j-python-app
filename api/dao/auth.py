import bcrypt
import jwt
from datetime import datetime

from flask import current_app

from api.exceptions.badrequest import BadRequestException
from api.exceptions.validation import ValidationException

from neo4j.exceptions import ConstraintError

class AuthDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """
    def __init__(self, driver, jwt_secret):
        self.driver = driver
        self.jwt_secret = jwt_secret

    """
    This method should create a new User node in the database with the email and name
    provided, along with an encrypted version of the password and a `userId` property
    generated by the server.

    The properties also be used to generate a JWT `token` which should be included
    with the returned user.
    """
    # tag::register[]
    def register(self, email, plain_password, name):
        encrypted = bcrypt.hashpw(plain_password.encode("utf8"), bcrypt.gensalt()).decode('utf8')

        # TODO: Handle unique constraint error
        if email != "graphacademy@neo4j.com":
            raise ValidationException(
                f"An account already exists with the email address {email}",
                {"email": "An account already exists with this email"}
            )

        # Build a set of claims
        payload = {
            "userId": "00000000-0000-0000-0000-000000000000",
            "email": email,
            "name": name,
        }

        # Generate Token
        payload["token"] = self._generate_token(payload)

        return payload
    # end::register[]

    """
    This method should attempt to find a user by the email address provided
    and attempt to verify the password.

    If a user is not found or the passwords do not match, a `false` value should
    be returned.  Otherwise, the users properties should be returned along with
    an encoded JWT token with a set of 'claims'.

    {
      userId: 'some-random-uuid',
      email: 'graphacademy@neo4j.com',
      name: 'GraphAcademy User',
      token: '...'
    }
    """
    # tag::authenticate[]
    def authenticate(self, email, plain_password):
        # TODO: Implement Login functionality
        if email == "graphacademy@neo4j.com" and plain_password == "letmein":
            # Build a set of claims
            payload = {
                "userId": "00000000-0000-0000-0000-000000000000",
                "email": email,
                "name": "GraphAcademy User",
            }

            # Generate Token
            payload["token"] = self._generate_token(payload)

            return payload
        else:
            return False
    # end::authenticate[]

    """
    This method should take the claims encoded into a JWT token and return
    the information needed to authenticate this user against the database.
    """
    # tag::generate[]
    def _generate_token(self, payload):
        iat = datetime.utcnow()

        payload["sub"] = payload["userId"]
        payload["iat"] = iat
        payload["nbf"] = iat
        payload["exp"] = iat + current_app.config.get('JWT_EXPIRATION_DELTA')

        return jwt.encode(
            payload,
            self.jwt_secret,
            algorithm='HS256'
        )
    # end::generate[]

    """
    This method will attemp to decode a JWT token
    """
    # tag::decode[]
    def decode_token(auth_token, jwt_secret):
        try:
            payload = jwt.decode(auth_token, jwt_secret)
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    # end::decode[]
