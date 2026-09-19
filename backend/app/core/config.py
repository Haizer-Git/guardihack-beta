from services.preset_service import (
    create_preset
)
from services.auth_service import (
    create_token
)

data = {
    "max_uses": 10,
    "preset_id": 1
}

def init_db():
    
    admin_preset = {
        "name": "ADMIN",
        "type": "ADMIN",
        "affiliation": "PARIS",
        "niveau": "GCS3",
        "classe": "1"
    }
    create_preset(1, admin_preset)
    create_token(0, data=data, auto=True)


