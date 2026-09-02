from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status


def parse_object_id(id_str: str) -> ObjectId:
    """Validate and convert a path-param string into a Mongo ObjectId.

    Raises 400 (not 500) when the client sends a malformed id, since that is
    a client error, not a server fault.
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid id format.",
        )


def serialize_doc(doc: dict) -> dict:
    """Turn a Mongo document's _id into a plain string `id` field."""
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    return doc
