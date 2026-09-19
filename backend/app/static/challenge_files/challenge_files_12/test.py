from services.preset_service import (
    create_preset
)
from services.auth_service import (
    create_token, register_user
)

passphrase ="MOT DE PASSE DE TEST"

dataparis = {
    "max_uses": 10,
    "preset_id": 2,
}
datalyon = {
    "max_uses": 10,
    "preset_id": 3,
}
databordeaux = {
    "max_uses": 10,
    "preset_id": 4,
}

def test_db():
    paris_preset = {
        "type": "USER",
        "affiliation": "PARIS",
        "niveau": "GCS3",
        "classe": "3"
    }
    create_preset(1, paris_preset)
    paris_token = create_token(0, data=dataparis)
    lyon_preset = {
        "type": "USER",
        "affiliation": "LYON",
        "niveau": "GCS3",
        "classe": "3"
    }
    create_preset(1, lyon_preset)
    lyon_token= create_token(0, data=datalyon)
    bordeaux_preset = {
        "type": "USER",
        "affiliation": "BORDEAUX",
        "niveau": "GCS3",
        "classe": "3"
    }
    create_preset(1, bordeaux_preset)
    bordeaux_token = create_token(0, data=databordeaux)

    paris_users = [
        {
            "token": paris_token,
            "username": "Antoine",
            "passphrase": passphrase,
            "mail": "antoine.dupont@guardiaschool.fr",
            "first_name": "Antoine",
            "last_name": "Dupont",
        },
        {
            "token": paris_token,
            "username": "Sophie",
            "passphrase": passphrase,
            "mail": "sophie.martin@guardiaschool.fr",
            "first_name": "Sophie",
            "last_name": "Martin",
        },
        {
            "token": paris_token,
            "username": "Lucas",
            "passphrase": passphrase,
            "mail": "lucas.bernard@guardiaschool.fr",
            "first_name": "Lucas",
            "last_name": "Bernard",
        },
        {
            "token": paris_token,
            "username": "Emma",
            "passphrase": passphrase,
            "mail": "emma.thomas@guardiaschool.fr",
            "first_name": "Emma",
            "last_name": "Thomas",
        },
        {
            "token": paris_token,
            "username": "Maxime",
            "passphrase": passphrase,
            "mail": "maxime.robert@guardiaschool.fr",
            "first_name": "Maxime",
            "last_name": "Robert",
        },
        {
            "token": paris_token,
            "username": "Claire",
            "passphrase": passphrase,
            "mail": "claire.richard@guardiaschool.fr",
            "first_name": "Claire",
            "last_name": "Richard",
        },
        {
            "token": paris_token,
            "username": "Thomas",
            "passphrase": passphrase,
            "mail": "thomas.dubois@guardiaschool.fr",
            "first_name": "Thomas",
            "last_name": "Dubois",
        },
        {
            "token": paris_token,
            "username": "Marine",
            "passphrase": passphrase,
            "mail": "marine.petit@guardiaschool.fr",
            "first_name": "Marine",
            "last_name": "Petit",
        },
        {
            "token": paris_token,
            "username": "Nicolas",
            "passphrase": passphrase,
            "mail": "nicolas.lefevre@guardiaschool.fr",
            "first_name": "Nicolas",
            "last_name": "Lefevre",
        },
        {
            "token": paris_token,
            "username": "Amelie",
            "passphrase": passphrase,
            "mail": "amelie.michel@guardiaschool.fr",
            "first_name": "Amelie",
            "last_name": "Michel",
        },
    ]

    lyon_users = [
        {
            "token": lyon_token,
            "username": "Pierre",
            "passphrase": passphrase,
            "mail": "pierre.moreau@guardiaschool.fr",
            "first_name": "Pierre",
            "last_name": "Moreau",
        },
        {
            "token": lyon_token,
            "username": "Isabelle",
            "passphrase": passphrase,
            "mail": "isabelle.simon@guardiaschool.fr",
            "first_name": "Isabelle",
            "last_name": "Simon",
        },
        {
            "token": lyon_token,
            "username": "Julien",
            "passphrase": passphrase,
            "mail": "julien.laurent@guardiaschool.fr",
            "first_name": "Julien",
            "last_name": "Laurent",
        },
        {
            "token": lyon_token,
            "username": "Margot",
            "passphrase": passphrase,
            "mail": "margot.lefebvre@guardiaschool.fr",
            "first_name": "Margot",
            "last_name": "Lefebvre",
        },
        {
            "token": lyon_token,
            "username": "Samuel",
            "passphrase": passphrase,
            "mail": "samuel.michel@guardiaschool.fr",
            "first_name": "Samuel",
            "last_name": "Michel",
        },
        {
            "token": lyon_token,
            "username": "Charlotte",
            "passphrase": passphrase,
            "mail": "charlotte.garcia@guardiaschool.fr",
            "first_name": "Charlotte",
            "last_name": "Garcia",
        },
        {
            "token": lyon_token,
            "username": "Victor",
            "passphrase": passphrase,
            "mail": "victor.martinez@guardiaschool.fr",
            "first_name": "Victor",
            "last_name": "Martinez",
        },
        {
            "token": lyon_token,
            "username": "Nathalie",
            "passphrase": passphrase,
            "mail": "nathalie.robinson@guardiaschool.fr",
            "first_name": "Nathalie",
            "last_name": "Robinson",
        },
        {
            "token": lyon_token,
            "username": "Alexandre",
            "passphrase": passphrase,
            "mail": "alexandre.clark@guardiaschool.fr",
            "first_name": "Alexandre",
            "last_name": "Clark",
        },
        {
            "token": lyon_token,
            "username": "Veronique",
            "passphrase": passphrase,
            "mail": "veronique.rodriguez@guardiaschool.fr",
            "first_name": "Veronique",
            "last_name": "Rodriguez",
        },
    ]

    bordeaux_users = [
        {
            "token": bordeaux_token,
            "username": "Francois",
            "passphrase": passphrase,
            "mail": "francois.lewis@guardiaschool.fr",
            "first_name": "Francois",
            "last_name": "Lewis",
        },
        {
            "token": bordeaux_token,
            "username": "Sylvie",
            "passphrase": passphrase,
            "mail": "sylvie.walker@guardiaschool.fr",
            "first_name": "Sylvie",
            "last_name": "Walker",
        },
        {
            "token": bordeaux_token,
            "username": "Olivier",
            "passphrase": passphrase,
            "mail": "olivier.hall@guardiaschool.fr",
            "first_name": "Olivier",
            "last_name": "Hall",
        },
        {
            "token": bordeaux_token,
            "username": "Chantal",
            "passphrase": passphrase,
            "mail": "chantal.allen@guardiaschool.fr",
            "first_name": "Chantal",
            "last_name": "Allen",
        },
        {
            "token": bordeaux_token,
            "username": "Benoit",
            "passphrase": passphrase,
            "mail": "benoit.young@guardiaschool.fr",
            "first_name": "Benoit",
            "last_name": "Young",
        },
        {
            "token": bordeaux_token,
            "username": "Monique",
            "passphrase": passphrase,
            "mail": "monique.king@guardiaschool.fr",
            "first_name": "Monique",
            "last_name": "King",
        },
        {
            "token": bordeaux_token,
            "username": "Raphael",
            "passphrase": passphrase,
            "mail": "raphael.scott@guardiaschool.fr",
            "first_name": "Raphael",
            "last_name": "Scott",
        },
        {
            "token": bordeaux_token,
            "username": "Patricia",
            "passphrase": passphrase,
            "mail": "patricia.green@guardiaschool.fr",
            "first_name": "Patricia",
            "last_name": "Green",
        },
        {
            "token": bordeaux_token,
            "username": "Sebastien",
            "passphrase": passphrase,
            "mail": "sebastien.adams@guardiaschool.fr",
            "first_name": "Sebastien",
            "last_name": "Adams",
        },
        {
            "token": bordeaux_token,
            "username": "Josee",
            "passphrase": passphrase,
            "mail": "josee.nelson@guardiaschool.fr",
            "first_name": "Josee",
            "last_name": "Nelson",
        },
    ]
    for user in paris_users + lyon_users + bordeaux_users:
        register_user(user)