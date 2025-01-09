import hashlib
import secrets
import base64

class IdGenerator:
    ALPHANUMERIC_CHARACTERS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    ID_LENGTH = 56

    @staticmethod
    def generate_deterministic_id(seed: str) -> str:
        if not seed:
            raise ValueError('Input string cannot be null or empty')

        first_hash = hashlib.sha256(seed.encode()).digest()
        second_hash = hashlib.sha256(first_hash).digest()
        combined_hash = first_hash + second_hash

        base64_encoded = base64.b64encode(combined_hash).decode()
        clean_id = ''.join(c for c in base64_encoded if c.isalnum())

        return clean_id[:IdGenerator.ID_LENGTH]

    @staticmethod
    def generate_random_id() -> str:
        chars = []
        for _ in range(IdGenerator.ID_LENGTH):
            random_byte = secrets.randbelow(len(IdGenerator.ALPHANUMERIC_CHARACTERS))
            chars.append(IdGenerator.ALPHANUMERIC_CHARACTERS[random_byte])

        return ''.join(chars)