from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, Unauthorized
from extensions import db
import csv, io
from models.core import (
    User, PresetToken, UserProfile, UserPreset
)
from services.auth_service import (
    create_token, send_token
)

def auto_create_token(user_id, preset_id, file, send=False):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    if not isinstance(preset_id, int):
        raise BadRequest("INVALID_PRESET_ID|L'ID du preset doit être un entier.")
    if not file:
        raise BadRequest("MISSING_FILE|Aucun fichier CSV fourni.")
    stream = io.TextIOWrapper(file.stream, encoding="utf-8")
    csv_reader = csv.DictReader(stream)
    created_tokens = []
    errors = []
    for row in csv_reader:
        row_data = {
            'preset_id': preset_id,
            'mail': row.get('mail', '').strip(),
            'first_name': row.get('first_name', '').strip(),
            'last_name': row.get('last_name', '').strip(),
            'classe': row.get('classe', '').strip(),
            'niveau': row.get('niveau', '').strip(),
            'max_uses': 1,
        }
        try:
            token_id = create_token(user_id, row_data, auto=True)[0]
            if send and token_id:
                send_token(token_id)
            created_tokens.append(row_data['mail'])
        except Exception as e:
            errors.append({"mail": row_data.get('mail'), "error": str(e)})
    return {
        "success": f"{len(created_tokens)} tokens créés avec succès.",
        "errors": errors
    }