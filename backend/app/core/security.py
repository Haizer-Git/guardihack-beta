from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from werkzeug.exceptions import InternalServerError, BadRequest, NotFound, Unauthorized
from extensions import redis_client, db
from models import (
    User
)
import secrets, string, hashlib, os, re


_key = os.getenv("CYPHER_KEY")
_cipher = Fernet(_key) if _key else None

_banned_file = Path(__file__).resolve().parent / "banned_username.txt"
try:
    with _banned_file.open(encoding="utf-8") as f:
        banned_usernames = {line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")}
except FileNotFoundError:
    banned_usernames = set()
except OSError:
    banned_usernames = set()

def reg_verify_username(username):
    if username in banned_usernames:
        raise Unauthorized("USERNAME_BANNED|Ce nom d'utilisateur n'est pas autorisé.")
    if len(username) < 3 or len(username) > 32:
        raise BadRequest("USERNAME_LENGTH|Le nom d'utilisateur ne respecte pas les critères de longueur (3-32 caractères).")

def reg_verify_passphrase(passphrase):
    if len(passphrase) < 14:
        raise BadRequest("WEAK_PASSPHRASE|La phrase doit contenir au moins 14 caractères.")
    if re.search(r'(.)\1{3,}', passphrase):
        raise BadRequest("WEAK_PASSPHRASE|La phrase contient trop de caractères répétés.")
    if " " not in passphrase:
        raise BadRequest("WEAK_PASSPHRASE|La phrase doit contenir plusieurs mots séparés par des espaces.")

def reg_setup_passphrase(passphrase):
    hashed = PasswordHasher()
    try:
        return hashed.hash(passphrase)
    except Exception:
        raise InternalServerError("HASHING_FAILED|Erreur lors du hachage de la passphrase.")

def log_verify_passphrase(stored_hash, provided_passphrase):
    ph = PasswordHasher()
    try:
        return ph.verify(stored_hash, provided_passphrase)
    except VerifyMismatchError:
        return False
    except Exception:
        raise InternalServerError("HASHING_FAILED|Erreur lors de la vérification de la passphrase.")

def generate_token():
    return secrets.token_urlsafe(32)

def generate_update_code(user_id):
    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    redis_client.setex(f"update_code:{user_id}", 300, code)
    return code

def verify_update_code(user_id, code):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    redis_key = f"update_code:{user_id}"
    attempt_key = f"update_attempts:{user_id}"
    stored_code = redis_client.get(redis_key)
    if not stored_code:
        raise BadRequest("UPDATE_CODE_INVALID|Le code de vérification est invalide ou a expiré.")
    if isinstance(stored_code, bytes):
        stored_code = stored_code.decode('utf-8')
    code = str(code)
    if stored_code != code:
        current_attempts = redis_client.incr(attempt_key)
        if current_attempts == 1:
            redis_client.expire(attempt_key, 300)
        if current_attempts >= 3:
            redis_client.delete(redis_key)
            redis_client.delete(attempt_key)
            lock_user(user_id)
            raise BadRequest("ACCOUNT_LOCKED|Votre compte a été verrouillé après trop de tentatives infructueuses. Merci de contacter un administrateur.")
        raise BadRequest("UPDATE_CODE_INVALID|Le code de vérification est invalide ou a expiré.")
    return "Code de vérification valide."

def lock_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise BadRequest("USER_NOT_FOUND|Utilisateur non trouvé.")
    user.status = "locked"
    db.session.commit()

def delete_update_code(user_id):
    redis_client.delete(f"update_code:{user_id}")
    redis_client.delete(f"update_attempts:{user_id}")

def generate_reset_url(user_id):
    token = generate_token()
    redis_client.setex(f"reset_token:{token}", 3600, user_id)
    return f"http://127.0.0.1:5173/reset/passphrase/{token}"

def verify_reset_token(token):
    redis_key = f"reset_token:{token}"
    user_id = redis_client.get(redis_key)
    if not user_id:
        raise NotFound("LINK_INVALID|Le lien de réinitialisation est invalide ou a expiré.")
    if isinstance(user_id, bytes):
        user_id = user_id.decode('utf-8')
    return "Lien de réinitialisation valide.",user_id

def hash_flag(flag):
    ph = PasswordHasher()
    try:
        return ph.hash(flag)
    except Exception:
        raise InternalServerError("HASHING_FAILED|Erreur lors du hachage du flag")

def generate_user_flag(user_secret_key, challenge_secret_key):
    combinaison = f"{user_secret_key}:{challenge_secret_key}"
    hash_object = hashlib.sha512(combinaison.encode())
    empreinte = hash_object.hexdigest()
    identifiant_flag = empreinte[:32]
    user_flag = f"GH{{{identifiant_flag}}}"
    return user_flag

def verify_flag(stored_hash, provided_flag, dynamic=None):
    ph = PasswordHasher()
    try:
        if ph.verify(stored_hash, provided_flag):
            return True, "MASTER"
    except VerifyMismatchError:
        pass
    except Exception:
        return False, None
    if dynamic and isinstance(dynamic, dict):
        user_secret = dynamic.get("user")
        challenge_secret = dynamic.get("challenge")
        if user_secret and challenge_secret:
            combinaison = f"{user_secret}:{challenge_secret}"
            empreinte = hashlib.sha512(combinaison.encode()).hexdigest()[:32]
            flag_structure = f"GH{{{empreinte}}}"
            if provided_flag.strip() == flag_structure:
                return True, "DYNAMIC"
    return False, None

def file_sha256(file):
    sha256_hash = hashlib.sha256()
    file.stream.seek(0)
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.stream.seek(0)
    return sha256_hash.hexdigest()

def encrypt_flag(flag):
    if not _cipher:
        raise BadRequest("La clé de chiffrement n'est pas définie.")
    encrypted_flag = _cipher.encrypt(flag.encode())
    return encrypted_flag.decode()

def decrypt_flag(encrypted_flag):
    if not _cipher:
        raise BadRequest("La clé de chiffrement n'est pas définie.")
    decrypted_flag = _cipher.decrypt(encrypted_flag.encode())
    return decrypted_flag.decode()
