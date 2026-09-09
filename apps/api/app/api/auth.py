from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """
    Authentication endpoint.

    Replace the demo authentication below with your real user store/JWT
    implementation when authentication is wired into the application.
    """

    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # TODO:
    # 1. Look up the user.
    # 2. Verify the password hash.
    # 3. Generate a JWT.
    #
    # This placeholder keeps the API contract stable while the inference
    # pipeline is being implemented.

    return LoginResponse(
        access_token="development-token",
    )