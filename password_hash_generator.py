import hashlib
import re

SALT = "saltvaluebytheta"

def password_is_valid(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

def generate_hash(password: str) -> str:
    # Combine password with salt and hash using SHA256
    salted_password = password + SALT
    hash_object = hashlib.sha256(salted_password.encode('utf-8'))
    return hash_object.hexdigest()

def verify_password(provided_pass: str, stored_hash: str) -> bool:
    # Verify the password by comparing the hash    
    new_password = generate_hash(provided_pass)
    #generate_hash_all()
    return stored_hash == new_password 

    
   
