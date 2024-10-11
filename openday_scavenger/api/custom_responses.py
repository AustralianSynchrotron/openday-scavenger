import json
import typing

from fastapi import Response


class PrettyJSONResponse(Response):
    """Equivilant to the FastAPI JSONResponse class but 'pretty prints' the JSON"""

    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # Avoid using this for endpoints that are used often as it is a blocking operation
        # There are ways of making this non blocking but it is only used for a utility endpoint
        # so not a big issue for now
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            separators=(", ", ": "),
        ).encode("utf-8")
