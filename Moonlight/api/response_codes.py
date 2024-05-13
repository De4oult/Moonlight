from enum import Enum


class ResponseCodes(Enum):
    # Success
    OK:      int = 200 
    CREATED: int = 201

    # Client error
    BAD_REQUEST:  int = 400
    UNAUTHORIZED: int = 401
    FORBIDDEN:    int = 403
    NOT_FOUND:    int = 404
    CONFLICT:     int = 409