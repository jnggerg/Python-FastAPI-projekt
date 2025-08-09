from typing import List, Optional
from pydantic import BaseModel

class Oktato(BaseModel):
    nev: str
    email: str

class Hallgato(BaseModel):
    id: Optional[int]
    nev: str
    email: str

class Kurzus(BaseModel):
    id: Optional[int]
    nev: str
    tipus: str
    evfolyam: int
    nap_idopont: str
    helyszin: str
    oktato: Oktato
    hallgatok: Optional[List[Hallgato]]
    max_letszam: int

class Valasz(BaseModel):
    uzenet: str

