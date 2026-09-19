from services.preset_service import (
    create_preset
)
from services.auth_service import (
    create_token, register_user
)

passphrase = "MOT DE PASSE DE TEST"

def test_db():
    paris_preset = {
        "name": "Preset Paris GCS3",
        "type": "USER",
        "affiliation": "PARIS",
    }
    create_preset(1, paris_preset)

    lyon_preset = {
        "name": "Preset Lyon GCS3",
        "type": "USER",
        "affiliation": "LYON",
    }
    create_preset(1, lyon_preset)

    bordeaux_preset = {
        "name": "Preset Bordeaux GCS3",
        "type": "USER",
        "affiliation": "BORDEAUX",
    }
    create_preset(1, bordeaux_preset)

    paris_students = [
        {"username": "Antoine", "mail": "antoine.dupont@guardiaschool.fr", "first_name": "Antoine", "last_name": "Dupont", "niveau": "GCS3", "classe": "3"},
        {"username": "Sophie", "mail": "sophie.martin@guardiaschool.fr", "first_name": "Sophie", "last_name": "Martin", "niveau": "GCS3", "classe": "3"},
        {"username": "Lucas", "mail": "lucas.bernard@guardiaschool.fr", "first_name": "Lucas", "last_name": "Bernard", "niveau": "GCS3", "classe": "3"},
        {"username": "Emma", "mail": "emma.thomas@guardiaschool.fr", "first_name": "Emma", "last_name": "Thomas", "niveau": "GCS3", "classe": "3"},
        {"username": "Maxime", "mail": "maxime.robert@guardiaschool.fr", "first_name": "Maxime", "last_name": "Robert", "niveau": "GCS3", "classe": "3"},
        {"username": "Claire", "mail": "claire.richard@guardiaschool.fr", "first_name": "Claire", "last_name": "Richard", "niveau": "GCS3", "classe": "3"},
        {"username": "Thomas", "mail": "thomas.dubois@guardiaschool.fr", "first_name": "Thomas", "last_name": "Dubois", "niveau": "GCS3", "classe": "3"},
        {"username": "Marine", "mail": "marine.petit@guardiaschool.fr", "first_name": "Marine", "last_name": "Petit", "niveau": "GCS3", "classe": "3"},
        {"username": "Nicolas", "mail": "nicolas.lefevre@guardiaschool.fr", "first_name": "Nicolas", "last_name": "Lefevre", "niveau": "GCS3", "classe": "3"},
        {"username": "Amelie", "mail": "amelie.michel@guardiaschool.fr", "first_name": "Amelie", "last_name": "Michel", "niveau": "GCS3", "classe": "3"},
    ]

    lyon_students = [
        {"username": "Pierre", "mail": "pierre.moreau@guardiaschool.fr", "first_name": "Pierre", "last_name": "Moreau", "niveau": "GCS3", "classe": "3"},
        {"username": "Isabelle", "mail": "isabelle.simon@guardiaschool.fr", "first_name": "Isabelle", "last_name": "Simon", "niveau": "GCS3", "classe": "3"},
        {"username": "Julien", "mail": "julien.laurent@guardiaschool.fr", "first_name": "Julien", "last_name": "Laurent", "niveau": "GCS3", "classe": "3"},
        {"username": "Margot", "mail": "margot.lefebvre@guardiaschool.fr", "first_name": "Margot", "last_name": "Lefebvre", "niveau": "GCS3", "classe": "3"},
        {"username": "Samuel", "mail": "samuel.michel@guardiaschool.fr", "first_name": "Samuel", "last_name": "Michel", "niveau": "GCS3", "classe": "3"},
        {"username": "Charlotte", "mail": "charlotte.garcia@guardiaschool.fr", "first_name": "Charlotte", "last_name": "Garcia", "niveau": "GCS3", "classe": "3"},
        {"username": "Victor", "mail": "victor.martinez@guardiaschool.fr", "first_name": "Victor", "last_name": "Martinez", "niveau": "GCS3", "classe": "3"},
        {"username": "Nathalie", "mail": "nathalie.robinson@guardiaschool.fr", "first_name": "Nathalie", "last_name": "Robinson", "niveau": "GCS3", "classe": "3"},
        {"username": "Alexandre", "mail": "alexandre.clark@guardiaschool.fr", "first_name": "Alexandre", "last_name": "Clark", "niveau": "GCS3", "classe": "3"},
        {"username": "Veronique", "mail": "veronique.rodriguez@guardiaschool.fr", "first_name": "Veronique", "last_name": "Rodriguez", "niveau": "GCS3", "classe": "3"},
    ]

    bordeaux_students = [
        {"username": "Francois", "mail": "francois.lewis@guardiaschool.fr", "first_name": "Francois", "last_name": "Lewis", "niveau": "GCS3", "classe": "3"},
        {"username": "Sylvie", "mail": "sylvie.walker@guardiaschool.fr", "first_name": "Sylvie", "last_name": "Walker", "niveau": "GCS3", "classe": "3"},
        {"username": "Olivier", "mail": "olivier.hall@guardiaschool.fr", "first_name": "Olivier", "last_name": "Hall", "niveau": "GCS3", "classe": "3"},
        {"username": "Chantal", "mail": "chantal.allen@guardiaschool.fr", "first_name": "Chantal", "last_name": "Allen", "niveau": "GCS3", "classe": "3"},
        {"username": "Benoit", "mail": "benoit.young@guardiaschool.fr", "first_name": "Benoit", "last_name": "Young", "niveau": "GCS3", "classe": "3"},
        {"username": "Monique", "mail": "monique.king@guardiaschool.fr", "first_name": "Monique", "last_name": "King", "niveau": "GCS3", "classe": "3"},
        {"username": "Raphael", "mail": "raphael.scott@guardiaschool.fr", "first_name": "Raphael", "last_name": "Scott", "niveau": "GCS3", "classe": "3"},
        {"username": "Patricia", "mail": "patricia.green@guardiaschool.fr", "first_name": "Patricia", "last_name": "Green", "niveau": "GCS3", "classe": "3"},
        {"username": "Sebastien", "mail": "sebastien.adams@guardiaschool.fr", "first_name": "Sebastien", "last_name": "Adams", "niveau": "GCS3", "classe": "3"},
        {"username": "Josee", "mail": "josee.nelson@guardiaschool.fr", "first_name": "Josee", "last_name": "Nelson", "niveau": "GCS3", "classe": "3"},
    ]

    all_users_to_register = []
    for student in paris_students:
        token_data = {
            "max_uses": 1,
            "preset_id": 2,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        }
        token_str = create_token(1, data=token_data, auto=True)[1]
        all_users_to_register.append({
            "token": token_str,
            "username": student["username"],
            "passphrase": passphrase,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        })
    for student in lyon_students:
        token_data = {
            "max_uses": 1,
            "preset_id": 3,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        }
        token_str = create_token(1, data=token_data, auto=True)[1]
        all_users_to_register.append({
            "token": token_str,
            "username": student["username"],
            "passphrase": passphrase,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        })
    for student in bordeaux_students:
        token_data = {
            "max_uses": 1,
            "preset_id": 4,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        }
        token_str = create_token(1, data=token_data, auto=True)[1]
        all_users_to_register.append({
            "token": token_str,
            "username": student["username"],
            "passphrase": passphrase,
            "mail": student["mail"],
            "first_name": student["first_name"],
            "last_name": student["last_name"],
            "niveau": student["niveau"],
            "classe": student["classe"]
        })

    for user_data in all_users_to_register:
        register_user(user_data)