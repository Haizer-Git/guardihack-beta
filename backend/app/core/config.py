import os

from services.preset_service import (
    create_preset
)
from services.auth_service import (
    create_token, send_token
)
data_admin = [
    {
        "preset_id": 1,
        "mail": os.getenv('ADMIN_EMAIL_HAIZER'),
        "first_name": "Haizer",
        "last_name": "Tiouti",
        "niveau": "GCS3",
        "max_uses": 1,
    },
    {
        "preset_id": 1,
        "mail": os.getenv('ADMIN_EMAIL_AJAX'),
        "first_name": "Abonga",
        "last_name": "Ajax",
        "niveau": "GCS3",
        "max_uses": 1,
    }
]

def init_db():
    admin_preset = {
        "name": "ADMIN",
        "type": "ADMIN",
        "affiliation": "PARIS",
        "niveau": "GCS3"
    }
    create_preset(1, admin_preset)
    for data in data_admin:
        token_id = create_token(1, data, auto=True)[0]
        send_token(token_id)


