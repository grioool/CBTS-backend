from fastapi import APIRouter

router = APIRouter()


@router.post("/auth/login")
def login():
    return {
        "access_token": "eyJhbGciOiJIUzI1..."
    }


@router.post("/auth/registration")
def register():
    return {
        "access_token": "eyJhbGciOiJIUzI1..."
    }


@router.post("/auth/refresh")
def refresh_token():
    return {
        "access_token": "new_access_token"
    }
