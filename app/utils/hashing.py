from passlib.context import CryptContext

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return PWD_CONTEXT.hash(password)