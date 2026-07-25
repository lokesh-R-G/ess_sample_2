import os
from pathlib import Path

BASE_DIR = Path("backend/app/organization")

folders = [
    "models", "schemas", "repositories", "services", 
    "controllers", "routes", "validators", "constants", "engine"
]

entities = [
    "organization", "company", "branch", "department", 
    "designation", "role", "shift", "holiday"
]

def create_structure():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "__init__.py").touch()
    
    for folder in folders:
        folder_path = BASE_DIR / folder
        folder_path.mkdir(exist_ok=True)
        (folder_path / "__init__.py").touch()
        
    # Constants
    with open(BASE_DIR / "constants" / "enums.py", "w") as f:
        f.write('from enum import Enum\n\nclass Status(str, Enum):\n    ACTIVE = "Active"\n    INACTIVE = "Inactive"\n')
        
    # Engine
    with open(BASE_DIR / "engine" / "organization_engine.py", "w") as f:
        f.write('class OrganizationEngine:\n    pass\n')
        
    # Base Repository
    with open(BASE_DIR / "repositories" / "base_repository.py", "w") as f:
        f.write('''from typing import TypeVar, Generic, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = self.db[collection_name]
''')

    for entity in entities:
        # models
        with open(BASE_DIR / "models" / f"{entity}.py", "w") as f:
            f.write(f'''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class {entity.capitalize()}Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
''')
        # schemas
        with open(BASE_DIR / "schemas" / f"{entity}.py", "w") as f:
            f.write(f'''from pydantic import BaseModel
from typing import Optional

class {entity.capitalize()}Create(BaseModel):
    name: str

class {entity.capitalize()}Update(BaseModel):
    name: Optional[str] = None

class {entity.capitalize()}Response({entity.capitalize()}Create):
    id: str
''')
        # repository
        with open(BASE_DIR / "repositories" / f"{entity}_repository.py", "w") as f:
            f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.{entity} import {entity.capitalize()}Model

class {entity.capitalize()}Repository(BaseRepository[{entity.capitalize()}Model]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "{entity if entity.endswith('s') else entity + 's'}")
''')
        # validator
        with open(BASE_DIR / "validators" / f"{entity}_validator.py", "w") as f:
            f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException

class {entity.capitalize()}Validator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def validate_create(self, data: dict):
        pass
''')
        # service
        with open(BASE_DIR / "services" / f"{entity}_service.py", "w") as f:
            f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.{entity}_repository import {entity.capitalize()}Repository
from ..validators.{entity}_validator import {entity.capitalize()}Validator

class {entity.capitalize()}Service:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = {entity.capitalize()}Repository(db)
        self.validator = {entity.capitalize()}Validator(db)
''')
        # controller
        with open(BASE_DIR / "controllers" / f"{entity}_controller.py", "w") as f:
            f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from ..services.{entity}_service import {entity.capitalize()}Service

class {entity.capitalize()}Controller:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = {entity.capitalize()}Service(db)
''')
        # routes
        with open(BASE_DIR / "routes" / f"{entity}_routes.py", "w") as f:
            f.write(f'''from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ..controllers.{entity}_controller import {entity.capitalize()}Controller

router = APIRouter(prefix="/{entity if entity.endswith('s') else entity + 's'}", tags=["{entity.capitalize()}"])
''')
            
    # Master Router
    with open(BASE_DIR / "routes" / "router.py", "w") as f:
        f.write('from fastapi import APIRouter\n')
        for entity in entities:
            f.write(f'from .{entity}_routes import router as {entity}_router\n')
        f.write('\norganization_router = APIRouter()\n')
        for entity in entities:
            f.write(f'organization_router.include_router({entity}_router)\n')

if __name__ == "__main__":
    create_structure()
    print("Scaffolding complete.")
