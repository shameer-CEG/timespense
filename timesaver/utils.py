import uuid
import base64

def encode_uuid_to_base64(uuid_value):
    """
    Convert a UUID to a URL-safe Base64-encoded string.
    """
    return base64.urlsafe_b64encode(uuid_value.bytes).rstrip(b'=').decode('utf-8')

def decode_base64_to_uuid(base64_str):
    """
    Convert a Base64-encoded string back to a UUID.
    """
    base64_str += '=' * (-len(base64_str) % 4)  # Add padding back if needed
    return uuid.UUID(bytes=base64.urlsafe_b64decode(base64_str))

