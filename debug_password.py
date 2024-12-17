from passlib.context import CryptContext

# Initialize bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Replace this with the hashed password stored in your database
hashed_password = "$2b$12$0s9R1DfElF636ukFe27I3OTj7q1XrlO6OenBt9gPK1H8QFFPgCDOm"

# Replace this with the plain password you are testing (from Insomnia)
plain_password = "devpassword123"

# Verify if the plain password matches the hashed password
is_valid = pwd_context.verify(plain_password, hashed_password)

# Output result
print(f"Password is valid: {is_valid}")
