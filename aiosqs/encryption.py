import hmac
import hashlib


def hmac_sha256(key: bytes, msg: str):
    return hmac.new(
        key=key,
        msg=msg.encode("utf-8"),
        digestmod=hashlib.sha256,
    )


def hmac_sha256_digest(key: bytes, msg: str):
    return hmac_sha256(key=key, msg=msg).digest()


def hmac_sha256_hexdigest(key: bytes, msg: str):
    return hmac_sha256(key=key, msg=msg).hexdigest()


def sha256_hexdigest(msg: str):
    return hashlib.sha256(msg.encode("utf-8")).hexdigest()


def get_signature_key(aws_secret_access_key: str, date_stamp: str, region_name: str, service_name: str):
    kDate = hmac_sha256_digest(("AWS4" + aws_secret_access_key).encode("utf-8"), date_stamp)
    kRegion = hmac_sha256_digest(kDate, region_name)
    kService = hmac_sha256_digest(kRegion, service_name)
    kSigning = hmac_sha256_digest(kService, "aws4_request")
    return kSigning
