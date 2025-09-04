from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from core.db import get_db_connection
import jwt
import os
from datetime import datetime, timedelta
from starlette.responses import RedirectResponse
from core.config import set_google_oauth

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth = set_google_oauth()

# ----- Schemas -----
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

# ----- Helpers -----
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ----- Normal Signup -----
@router.post("/signup")
def signup(request: SignupRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (request.email, request.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_password = pwd_context.hash(request.password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, google_id) VALUES (%s, %s, %s, %s)",
        (request.username, request.email, hashed_password, None)
    )
    conn.commit()
    conn.close()

    token = create_access_token({"sub": request.email})
    return {"access_token": token, "token_type": "bearer"}

# ----- Normal Login -----
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/google/login")
async def google_login(request: Request):
    
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if user exists by google_id or email
    cursor.execute("SELECT * FROM users WHERE google_id = %s OR email = %s", (user_info["sub"], user_info["email"]))
    user = cursor.fetchone()

    if not user:
        # Register Google user
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, google_id) VALUES (%s, %s, %s, %s)",
            (user_info.get("name", user_info["email"]), user_info["email"], None, user_info["sub"])
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email = %s", (user_info["email"],))
        user = cursor.fetchone()

    conn.close()

    # Issue JWT
    access_token = create_access_token({"sub": user["email"]})
    response = RedirectResponse(url=f"http://localhost:3000/dashboard?token={access_token}")
    return response

# ----- Dashboard -----
@router.get("/dashboard")
def get_dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }
