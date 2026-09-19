from extensions import db
import random
from datetime import datetime
from models.core import (
    User, Boutique, BoutiquePromotion, 
    Cosmetic, BoutiqueRotation, UserCosmetic
)
from werkzeug.exceptions import BadRequest, Conflict, NotFound, InternalServerError

RARETE_POIDS = {
    "COMMUN": 1,
    "RARE": 0.5,
    "EPIC": 0.25,
    "LEGENDARY": 0.05
}
HISTORIC_POIDS = {
    1: 0.1,
    2: 0.2125,
    3: 0.325,
    4: 0.4375,
    5: 0.55,
    6: 0.6625,
    7: 0.775,
    8: 0.8875,
    9: 1
}


def create_boutique_rotation(data):
    required_fields = ['name', 'start', 'end', 'type']
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    for field in required_fields:
        if not data.get(field):
            raise BadRequest(f"MISSING_FIELD|Le champ '{field}' est requis.")
    rotation_name = data['name']
    rotation_start = data['start']
    rotation_end = data['end']
    rotation_type = data['type']
    rotations = Boutique.query.filter_by(name=rotation_name).with_entities(Boutique.name).first()
    if rotations:
        raise Conflict(f"CONFLICT|La rotation '{rotation_name}' existe déjà.")
    try:
        rotation_start = datetime.fromisoformat(rotation_start.replace("Z", "+00:00"))
        rotation_end = datetime.fromisoformat(rotation_end.replace("Z", "+00:00"))
    except (BadRequest):
        raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide.")
    if rotation_start >= rotation_end:
        raise BadRequest("INVALID_DATE_RANGE|La date de début doit être antérieure à la date de fin.")
    NewRotation = Boutique()
    NewRotation.name = rotation_name
    NewRotation.start_time = rotation_start
    NewRotation.end_time = rotation_end
    NewRotation.type = rotation_type
    db.session.add(NewRotation)
    db.session.commit()
    return "Rotation créée avec succès."

def modify_boutique_rotation(rotation_id, data):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    if not isinstance(data, dict):
        raise BadRequest("INVALID_DATA|Les données doivent être un dictionnaire.")
    rotation = BoutiqueRotation.query.filter_by(id=rotation_id).first()
    if not rotation:
        raise NotFound(f"NOT_FOUND|La rotation avec l'ID '{rotation_id}' n'existe pas.")
    if 'name' in data:
        new_name = data['name']
        if new_name != rotation.name:
            existing_rotation = BoutiqueRotation.query.filter_by(name=new_name).with_entities(BoutiqueRotation.name).first()
            if existing_rotation:
                raise Conflict(f"CONFLICT|La rotation '{new_name}' existe déjà.")
            rotation.name = new_name
    if 'start' in data:
        try:
            new_start = datetime.fromisoformat(data['start'].replace("Z", "+00:00"))
            rotation.start = new_start
        except (BadRequest):
            raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide pour le champ 'start'.")
    if 'end' in data:
        try:
            new_end = datetime.fromisoformat(data['end'].replace("Z", "+00:00"))
            rotation.end = new_end
        except (BadRequest):
            raise BadRequest("INVALID_DATE_FORMAT|Format de date invalide pour le champ 'end'.")
    if rotation.start >= rotation.end:
        raise BadRequest("INVALID_DATE_RANGE|La date de début doit être antérieure à la date de fin.")
    db.session.commit()
    return "Rotation modifiée avec succès."

def delete_boutique_rotation(rotation_id):
    if not isinstance(rotation_id, int):
        raise BadRequest("INVALID_ROTATION_ID|L'ID de la rotation doit être un entier.")
    rotation = BoutiqueRotation.query.filter_by(id=rotation_id).first()
    if not rotation:
        raise NotFound(f"NOT_FOUND|La rotation avec l'ID '{rotation_id}' n'existe pas.")
    db.session.delete(rotation)
    db.session.commit()
    return "Rotation supprimée avec succès."

def calculer_poids_cosmetique(cosmetic_id):
    if not isinstance(cosmetic_id, int):
        raise BadRequest("INVALID_COSMETIC_ID|L'ID du cosmétique doit être un entier.")
    cosmetic = Cosmetic.query.filter_by(id=cosmetic_id).first()
    if not cosmetic:
        raise NotFound(f"NOT_FOUND|Le cosmétique avec l'ID '{cosmetic_id}' n'existe pas.")
    poids_rarete = RARETE_POIDS.get(cosmetic.rarete.upper(), 1.0)
    active_boutique = Boutique.query.filter_by(type='STANDARD').filter(Boutique.state == 'ACTIVE').first()
    if not active_boutique:
        active_boutique = Boutique.query.filter_by(type='STANDARD').order_by(Boutique.id.desc()).first()
    current_id = active_boutique.id if active_boutique else 1
    derniere_liaison = (BoutiqueRotation.query.filter_by(cosmetic_id=cosmetic_id).join(Boutique).order_by(Boutique.id.desc()).first())
    if not derniere_liaison:
        delay = current_id
    else:
        delay = current_id - derniere_liaison.boutique_id
    Y = poids_rarete * 1.0
    if delay <= 9:
        poids_historique = HISTORIC_POIDS.get(delay, 1.0)
        Y = poids_rarete * poids_historique
    else:
        Y = poids_rarete * 1.0
        for _ in range(10, delay + 1):
            if Y > poids_rarete:
                Y = Y + (Y / 4)
            else:
                Y = poids_rarete * 1.1
    return Y

def random_cosmetic_selection(size, slot):
    if not isinstance(size, int) or size <= 0:
        raise BadRequest("INVALID_SIZE|La taille doit être un entier positif.")
    if not isinstance(slot, int) or slot <= 0:
        raise BadRequest("INVALID_SLOT|Le slot doit être un entier positif.")
    if slot > size:
        raise BadRequest("INVALID_SLOT|Le slot ne peut pas dépasser la taille.")
    available_cosmetics = Cosmetic.query.filter_by(exclu=False).all()
    if len(available_cosmetics) < size:
        raise BadRequest("NOT_ENOUGH_COSMETICS|Pas assez de cosmétiques disponibles pour cette taille de sélection.")
    high_tier_pool = []
    other_pool = []
    for c in available_cosmetics:
        poids = calculer_poids_cosmetique(c.id)
        item = {"cosmetic": c, "weight": poids}
        
        if c.rarete.upper() in ["EPIC", "LEGENDARY"]:
            high_tier_pool.append(item)
        else:
            other_pool.append(item)
    if len(high_tier_pool) < slot:
        raise BadRequest("NOT_ENOUGH_HIGH_TIER|Pas assez de cosmétiques Épiques ou Légendaires pour satisfaire le nombre de slots demandés.")
    selected_cosmetics = []
    for _ in range(slot):
        choices_list = [item["cosmetic"] for item in high_tier_pool]
        weights_list = [item["weight"] for item in high_tier_pool]
        
        chosen = random.choices(choices_list, weights=weights_list, k=1)[0]
        selected_cosmetics.append(chosen)
        
        high_tier_pool = [item for item in high_tier_pool if item["cosmetic"].id != chosen.id]
    remaining_size = size - slot
    remaining_pool = high_tier_pool + other_pool
    for _ in range(remaining_size):
        choices_list = [item["cosmetic"] for item in remaining_pool]
        weights_list = [item["weight"] for item in remaining_pool]
        chosen = random.choices(choices_list, weights=weights_list, k=1)[0]
        selected_cosmetics.append(chosen)
        remaining_pool = [item for item in remaining_pool if item["cosmetic"].id != chosen.id]
    serialized_results = []
    for c in selected_cosmetics:
        serialized_results.append({
            "id": c.id,
            "name": c.name,
            "type": c.type,
            "description": c.description,
            "icon_url": c.icon_url,
            "rarete": c.rarete,
            "exclu": c.exclu,
            "global_cosmetic": c.global_cosmetic,
            "requirement_type": c.requirement_type,
            "requirement_value": c.requirement_value,
            "requirement_text": c.requirement_text
        })
    return serialized_results

def get_active_boutique(user_id):
    if not isinstance(user_id, int):
        raise InternalServerError("INVALID_USER_ID|L'ID de l'utilisateur doit être un entier.")
    # Récupérer l'utilisateur avec son inventaire
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise NotFound("USER_NOT_FOUND|Utilisateur non trouvé.")
    # Extraire la liste des IDs de cosmétiques déjà possédés par l'utilisateur
    earned_cosmetic_ids = {inv.cosmetic_id for inv in user.inventory}
    # Récupérer la boutique active (via le hybrid_property 'state')
    active_boutiques = Boutique.query.filter(Boutique.state == "ACTIVE").all()
    if not active_boutiques:
        return []
    boutique_data = []
    # Parcourir les boutiques actives, leurs lignes de rotations, puis les cosmétiques associés
    for boutique in active_boutiques:
        for rotation in boutique.rotations:
            cosmetic = rotation.cosmetic
            if cosmetic:
                boutique_data.append({
                    "id": cosmetic.id,
                    "name": cosmetic.name,
                    "type": cosmetic.type,
                    "description": cosmetic.description,
                    "icon_url": cosmetic.icon_url,
                    "rarete": cosmetic.rarete,
                    "exclu": cosmetic.exclu,
                    "global_cosmetic": cosmetic.global_cosmetic,
                    "requirement_type": cosmetic.requirement_type,
                    "requirement_value": cosmetic.requirement_value,
                    "requirement_text": cosmetic.requirement_text,
                    "is_earned": cosmetic.id in earned_cosmetic_ids
                })
    return boutique_data

def add_cosmetic_in_boutique(boutique_id, data):
    if not isinstance(boutique_id, int):
        raise BadRequest("INVALID_BOUTIQUE_ID|L'ID de la boutique doit être un entier.")
    if not isinstance(data, list):
        raise BadRequest("INVALID_DATA|Les données doivent être une liste de dictionnaires.")

    cosmetic_ids = []
    for item in data:
        if not isinstance(item, dict):
            raise BadRequest("INVALID_DATA|Chaque élément de la liste doit être un dictionnaire.")
        cosmetic_id = item.get("id")
        if not cosmetic_id:
            raise BadRequest("INVALID_DATA|Chaque dictionnaire doit contenir un ID de cosmétique.")
        cosmetic_ids.append(cosmetic_id)

    # Vérifier que la boutique existe
    boutique = Boutique.query.filter_by(id=boutique_id).first()
    if not boutique:
        raise NotFound("BOUTIQUE_NOT_FOUND|La boutique spécifiée est introuvable.")

    for cosmetic_id in cosmetic_ids:
        cosmetic = Cosmetic.query.filter_by(id=cosmetic_id).first()
        if not cosmetic:
            raise NotFound(f"COSMETIC_NOT_FOUND|Le cosmétique avec l'ID {cosmetic_id} est introuvable.")
        
        # 🟢 CORRECTION : Créer l'entrée dans la table de liaison BoutiqueRotation
        # Tu peux y associer un promotion_id par défaut si besoin (ex: ID 1 ou gérer selon ta logique)
        # Et tu peux y stocker le poids calculé via ta fonction précédente si tu le souhaites !
        from services.boutique_service import calculer_poids_cosmetique # selon ton import
        poids_calcule = calculer_poids_cosmetique(cosmetic.id)

        nouvelle_liaison = BoutiqueRotation(
            boutique_id=boutique.id,
            cosmetic_id=cosmetic.id,
            promotion_id=1,  # Assure-toi d'avoir une promotion valide par défaut ou récupère la bonne
            poids=poids_calcule
        )
        db.session.add(nouvelle_liaison)

    db.session.commit()
    return "Cosmétiques ajoutés à la boutique avec succès."
