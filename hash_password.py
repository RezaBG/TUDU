from passlib.context import CryptContext

# Initialize bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password to hash
plain_password = "password123"
hashed_password = pwd_context.hash(plain_password)

print(f"Hashed password: {hashed_password}")
