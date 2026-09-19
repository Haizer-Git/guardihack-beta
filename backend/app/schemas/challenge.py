from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional
from backend.app.models.core.challenge import ChallengeType

# Schéma de base
class ChallengeBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    connection_info: Optional[str] = None
    value: int
    type: ChallengeType = ChallengeType.standard
    state: str = "visible"
    max_attempts: int = 0

# Utilisé par l'Admin pour créer/modifier (inclut le Flag)
class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    category: str = Field(..., description="Ex: Web, Crypto, Forensic, etc.")
    value: int = Field(..., gt=0, description="Points du challenge (ex: 10, 100, 250...)")
    flag: str = Field(..., description="GHP{flag format}")
    state: str = Field("hidden", description="hidden ou visible")
    
class ChallengeUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    category: str | None = None
    value: int | None = Field(None, gt=0)
    flag: str | None = None
    state: str | None = None

# Ce que le Joueur voit (SÉCURISÉ : pas de flag ici)
class ChallengeRead(ChallengeBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

# Ce que l'Admin voit (Full info)
class ChallengeAdminRead(ChallengeRead):
    flag: str
    
class ChallengeSubmit(BaseModel):
    flag: str