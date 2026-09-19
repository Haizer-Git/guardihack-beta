import hashlib
import secrets

def simuler_flag_dynamique(user_secret_key, challenge_secret_key):
    """
    Calcule et retourne le flag dynamique attendu en fonction des deux clés secrètes.
    """
    combinaison = f"{user_secret_key}:{challenge_secret_key}"
    hash_object = hashlib.sha512(combinaison.encode())
    empreinte = hash_object.hexdigest()
    identifiant_flag = empreinte[:32]
    flag_attendu = f"GH{{{identifiant_flag}}}"
    return flag_attendu

# ==========================================
# EXEMPLE CONCRET DE TEST
# ==========================================
if __name__ == "__main__":
    print("--- 🧪 SIMULATION GENERATION DE FLAG DYNAMIQUE ---")
    user_key = "VeJNxaNa7b-_AT9lDwnBa4IHWTSOqWNMXWPVCrIEoIs"
    challenge_key = "c1TbOcW7g_ptL5wfC3P0XesvsoeJPvVIud6HbDmcL2E"
    
    print(f"\n[BDD User] Clé secrète du joueur      : {user_key}")
    print(f"[BDD Chall] Clé secrète du challenge : {challenge_key}")
    flag_genere = simuler_flag_dynamique(user_key, challenge_key)
    print("\n-------------------------------------------")
    print(f"👉 SORTIE ATTENDUE DANS LA VM DU JOUEUR :")
    print(f"   {flag_genere}")
    print("-------------------------------------------")
    print("\n[Vérification] Si le joueur soumet exactement ce texte :")
    test_match = (flag_genere.strip() == flag_genere)
    print(f"-> Résultat du match : {test_match} (DYNAMIC VALIDATED ✅)")