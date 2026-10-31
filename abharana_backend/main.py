# import os, re, uuid, secrets
# from pathlib import Path
# from datetime import datetime, timedelta, timezone
# from typing import Optional
# from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import jwt, JWTError
# from passlib.context import CryptContext
# from pydantic import BaseModel, Field
# from sqlalchemy import create_engine, String, Text, Float, Boolean, DateTime, select
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
# from dotenv import load_dotenv

# load_dotenv()
# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
# DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'abharana.db'}")
# SECRET_KEY = os.getenv("SECRET_KEY", "")
# if len(SECRET_KEY) < 32:
#     SECRET_KEY = secrets.token_urlsafe(48)
#     print("WARNING: Set a persistent SECRET_KEY in .env before deployment.")
# ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
# if len(ADMIN_PASSWORD) < 12:
#     print("WARNING: Set a strong ADMIN_PASSWORD (at least 12 characters) in .env.")
# ALGORITHM = "HS256"
# TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "720"))
# MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))
# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# class Base(DeclarativeBase): pass
# class Admin(Base):
#     __tablename__ = "admins"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
#     password_hash: Mapped[str] = mapped_column(String(255))
# class Product(Base):
#     __tablename__ = "products"
#     id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     name: Mapped[str] = mapped_column(String(160), index=True)
#     category: Mapped[str] = mapped_column(String(80), default="Jewellery")
#     price: Mapped[float] = mapped_column(Float, default=0)
#     description: Mapped[str] = mapped_column(Text, default="")
#     image_url: Mapped[str] = mapped_column(String(500), default="")
#     featured: Mapped[bool] = mapped_column(Boolean, default=False)
#     active: Mapped[bool] = mapped_column(Boolean, default=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# bearer = HTTPBearer(auto_error=False)
# class LoginIn(BaseModel):
#     username: str = Field(min_length=1, max_length=80)
#     password: str = Field(min_length=1, max_length=200)
# class ProductIn(BaseModel):
#     name: str = Field(min_length=1, max_length=160)
#     category: str = Field(default="Jewellery", max_length=80)
#     price: float = Field(ge=0, le=100000000)
#     description: str = Field(default="", max_length=5000)
#     image_url: str = Field(default="", max_length=500)
#     featured: bool = False
#     active: bool = True

# def get_db():
#     db = SessionLocal()
#     try: yield db
#     finally: db.close()
# def create_access_token(username: str) -> str:
#     now = datetime.now(timezone.utc)
#     return jwt.encode({"sub": username, "iat": now, "exp": now + timedelta(minutes=TOKEN_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
# def require_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer), db: Session = Depends(get_db)):
#     if not credentials: raise HTTPException(status_code=401, detail="Admin login required")
#     try:
#         payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if not username: raise HTTPException(status_code=401, detail="Invalid token")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in again.")
#     admin = db.scalar(select(Admin).where(Admin.username == username))
#     if not admin: raise HTTPException(status_code=401, detail="Admin account not found")
#     return admin
# def serialize_product(p: Product):
#     return {"id":p.id,"name":p.name,"category":p.category,"price":p.price,"description":p.description,"image_url":p.image_url,"featured":p.featured,"active":p.active,"created_at":p.created_at.isoformat()}

# app = FastAPI(title="Abharana Jewellery API", version="1.0.0")
# origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000").split(",") if x.strip()]
# app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Authorization","Content-Type"])

# @app.on_event("startup")
# def startup():
#     Base.metadata.create_all(bind=engine)
#     if ADMIN_PASSWORD and len(ADMIN_PASSWORD) >= 12:
#         with SessionLocal() as db:
#             if not db.scalar(select(Admin).where(Admin.username == ADMIN_USERNAME)):
#                 db.add(Admin(username=ADMIN_USERNAME, password_hash=pwd_context.hash(ADMIN_PASSWORD)))
#                 db.commit()

# @app.get("/")
# def root(): return {"service":"Abharana Jewellery API","docs":"/docs","health":"/api/health"}
# @app.get("/api/health")
# def health(): return {"status":"ok"}
# @app.post("/api/admin/login")
# def login(data: LoginIn, db: Session = Depends(get_db)):
#     admin = db.scalar(select(Admin).where(Admin.username == data.username))
#     if not admin or not pwd_context.verify(data.password, admin.password_hash):
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     return {"access_token":create_access_token(admin.username),"token_type":"bearer","expires_in":TOKEN_MINUTES*60}
# @app.get("/api/admin/me")
# def admin_me(admin: Admin = Depends(require_admin)): return {"username":admin.username,"authenticated":True}
# @app.get("/api/products")
# def list_products(db: Session = Depends(get_db)):
#     return [serialize_product(p) for p in db.scalars(select(Product).where(Product.active == True).order_by(Product.created_at.desc())).all()]
# @app.get("/api/admin/products")
# def admin_products(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
#     return [serialize_product(p) for p in db.scalars(select(Product).order_by(Product.created_at.desc())).all()]
# @app.post("/api/admin/products", status_code=201)
# def create_product(data: ProductIn, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
#     p = Product(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return serialize_product(p)
# @app.put("/api/admin/products/{product_id}")
# def update_product(product_id: str, data: ProductIn, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
#     p = db.get(Product, product_id)
#     if not p: raise HTTPException(status_code=404, detail="Product not found")
#     for key, value in data.model_dump().items(): setattr(p, key, value)
#     db.commit(); db.refresh(p); return serialize_product(p)
# @app.delete("/api/admin/products/{product_id}", status_code=204)
# def delete_product(product_id: str, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
#     p = db.get(Product, product_id)
#     if not p: raise HTTPException(status_code=404, detail="Product not found")
#     if p.image_url.startswith("/uploads/"):
#         candidate = (UPLOAD_DIR / Path(p.image_url).name).resolve()
#         if candidate.parent == UPLOAD_DIR.resolve() and candidate.exists(): candidate.unlink()
#     db.delete(p); db.commit(); return None
# @app.post("/api/admin/upload", status_code=201)
# async def upload_image(file: UploadFile = File(...), admin: Admin = Depends(require_admin)):
#     ext = Path(file.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, WEBP and GIF images are allowed")
#     if not (file.content_type or "").lower().startswith("image/"): raise HTTPException(status_code=400, detail="Uploaded file must be an image")
#     filename = f"{uuid.uuid4().hex}{ext}"; destination = UPLOAD_DIR / filename; total = 0
#     try:
#         with destination.open("wb") as out:
#             while True:
#                 chunk = await file.read(1024*1024)
#                 if not chunk: break
#                 total += len(chunk)
#                 if total > MAX_UPLOAD_MB*1024*1024:
#                     out.close(); destination.unlink(missing_ok=True)
#                     raise HTTPException(status_code=413, detail=f"Image exceeds {MAX_UPLOAD_MB} MB limit")
#                 out.write(chunk)
#     finally: await file.close()
#     return {"filename":filename,"url":f"/uploads/{filename}","size_bytes":total}
# @app.get("/uploads/{filename}")
# def get_upload(filename: str):
#     if Path(filename).name != filename or not re.fullmatch(r"[a-f0-9]{32}\.(jpg|jpeg|png|webp|gif)", filename): raise HTTPException(status_code=404, detail="Image not found")
#     path = UPLOAD_DIR / filename
#     if not path.is_file(): raise HTTPException(status_code=404, detail="Image not found")
#     return FileResponse(path)
# @app.get("/api/admin/stats")
# def admin_stats(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
#     products = db.scalars(select(Product)).all()
#     return {"total_products":len(products),"active_products":sum(p.active for p in products),"featured_products":sum(p.featured for p in products)}




import os, re, uuid, secrets
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Text, Float, Boolean, DateTime, select, inspect, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'abharana.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    SECRET_KEY = secrets.token_urlsafe(48)
    print("WARNING: Set a persistent SECRET_KEY in .env before deployment.")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
if len(ADMIN_PASSWORD) < 12:
    print("WARNING: Set a strong ADMIN_PASSWORD (at least 12 characters) in .env.")
ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "720"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase): pass
class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100), default="")
    email: Mapped[str] = mapped_column(String(254), default="")
class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(80), default="Jewellery")
    price: Mapped[float] = mapped_column(Float, default=0)
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)
class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)
class RegisterAdminIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=12, max_length=200)
    registration_key: str = Field(min_length=1, max_length=200)

class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(default="Jewellery", max_length=80)
    price: float = Field(ge=0, le=100000000)
    description: str = Field(default="", max_length=5000)
    image_url: str = Field(default="", max_length=500)
    featured: bool = False
    active: bool = True

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": username, "iat": now, "exp": now + timedelta(minutes=TOKEN_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
def require_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401, detail="Admin login required")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in again.")
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if not admin: raise HTTPException(status_code=401, detail="Admin account not found")
    return admin
def serialize_product(p: Product):
    return {"id":p.id,"name":p.name,"category":p.category,"price":p.price,"description":p.description,"image_url":p.image_url,"featured":p.featured,"active":p.active,"created_at":p.created_at.isoformat()}

app = FastAPI(title="Abharana Jewellery API", version="1.0.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Authorization","Content-Type"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # Add profile columns to an existing SQLite database without deleting existing accounts.
    if DATABASE_URL.startswith("sqlite"):
        columns = {col["name"] for col in inspect(engine).get_columns("admins")}
        with engine.begin() as conn:
            if "full_name" not in columns:
                conn.execute(text("ALTER TABLE admins ADD COLUMN full_name VARCHAR(100) NOT NULL DEFAULT ''"))
            if "email" not in columns:
                conn.execute(text("ALTER TABLE admins ADD COLUMN email VARCHAR(254) NOT NULL DEFAULT ''"))
    if ADMIN_PASSWORD and len(ADMIN_PASSWORD) >= 12:
        with SessionLocal() as db:
            if not db.scalar(select(Admin).where(Admin.username == ADMIN_USERNAME)):
                db.add(Admin(username=ADMIN_USERNAME, password_hash=pwd_context.hash(ADMIN_PASSWORD)))
                db.commit()

@app.get("/")
def root(): return {"service":"Abharana Jewellery API","docs":"/docs","health":"/api/health"}
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.post("/api/admin/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    admin = db.scalar(select(Admin).where(Admin.username == data.username))
    if not admin or not pwd_context.verify(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token":create_access_token(admin.username),"token_type":"bearer","expires_in":TOKEN_MINUTES*60}
@app.post("/api/admin/register", status_code=201)
def register_admin(data: RegisterAdminIn, db: Session = Depends(get_db)):
    # Registration is protected by a secret set by the site owner in the backend .env file.
    registration_key = os.getenv("ADMIN_REGISTRATION_KEY", "")
    if len(registration_key) < 16:
        raise HTTPException(status_code=503, detail="Admin registration is not configured. Ask the site owner to set ADMIN_REGISTRATION_KEY in the backend .env file.")
    if not secrets.compare_digest(data.registration_key, registration_key):
        raise HTTPException(status_code=403, detail="Incorrect private registration key")
    if db.scalar(select(Admin).where(Admin.username == data.username)):
        raise HTTPException(status_code=409, detail="That username is already taken")
    if db.scalar(select(Admin).where(Admin.email == data.email)):
        raise HTTPException(status_code=409, detail="That email address is already registered")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", data.email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    account = Admin(username=data.username, password_hash=pwd_context.hash(data.password), full_name=data.full_name.strip(), email=data.email.strip().lower())
    db.add(account)
    db.commit()
    return {"message":"Admin account created","username":account.username}

@app.get("/api/admin/me")
def admin_me(admin: Admin = Depends(require_admin)): return {"username":admin.username,"authenticated":True}
@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return [serialize_product(p) for p in db.scalars(select(Product).where(Product.active == True).order_by(Product.created_at.desc())).all()]
@app.get("/api/admin/products")
def admin_products(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    return [serialize_product(p) for p in db.scalars(select(Product).order_by(Product.created_at.desc())).all()]
@app.post("/api/admin/products", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    p = Product(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return serialize_product(p)
@app.put("/api/admin/products/{product_id}")
def update_product(product_id: str, data: ProductIn, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.model_dump().items(): setattr(p, key, value)
    db.commit(); db.refresh(p); return serialize_product(p)
@app.delete("/api/admin/products/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    if p.image_url.startswith("/uploads/"):
        candidate = (UPLOAD_DIR / Path(p.image_url).name).resolve()
        if candidate.parent == UPLOAD_DIR.resolve() and candidate.exists(): candidate.unlink()
    db.delete(p); db.commit(); return None
@app.post("/api/admin/upload", status_code=201)
async def upload_image(file: UploadFile = File(...), admin: Admin = Depends(require_admin)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, WEBP and GIF images are allowed")
    if not (file.content_type or "").lower().startswith("image/"): raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    filename = f"{uuid.uuid4().hex}{ext}"; destination = UPLOAD_DIR / filename; total = 0
    try:
        with destination.open("wb") as out:
            while True:
                chunk = await file.read(1024*1024)
                if not chunk: break
                total += len(chunk)
                if total > MAX_UPLOAD_MB*1024*1024:
                    out.close(); destination.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail=f"Image exceeds {MAX_UPLOAD_MB} MB limit")
                out.write(chunk)
    finally: await file.close()
    return {"filename":filename,"url":f"/uploads/{filename}","size_bytes":total}
@app.get("/uploads/{filename}")
def get_upload(filename: str):
    if Path(filename).name != filename or not re.fullmatch(r"[a-f0-9]{32}\.(jpg|jpeg|png|webp|gif)", filename): raise HTTPException(status_code=404, detail="Image not found")
    path = UPLOAD_DIR / filename
    if not path.is_file(): raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)
@app.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db), admin: Admin = Depends(require_admin)):
    products = db.scalars(select(Product)).all()
    return {"total_products":len(products),"active_products":sum(p.active for p in products),"featured_products":sum(p.featured for p in products)}
