import hashlib
import random
import string

def get_random_salt(length=16):
    # Random string of fixed length
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def tokenize_number(number): 
    number_str = str(number)
    # Generate a random salt
    salt = get_random_salt()
    # Tokenize number to a fixed length using a hash function with salt
    hashed = hashlib.sha256((number_str + salt).encode()).hexdigest()[:len(number_str)]
    return ''.join(str((int(char, 16) % 10)) for char in hashed)

def tokenize_string(value):
    # Generate a random salt
    salt = get_random_salt()
    # Tokenize string to a deterministic random string of the same length using salt
    hashed = hashlib.sha256((value + salt).encode()).hexdigest()
    return hashed[:len(value)]

def tokenize_email(email):
    user, domain = email.split('@')
    tokenized_user = tokenize_string(user)
    tokenized_domain = tokenize_string(domain.split('.')[0])
    return f"{tokenized_user}@{tokenized_domain}.domain"


