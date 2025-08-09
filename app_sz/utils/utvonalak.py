from fastapi import APIRouter, HTTPException
from typing import List
from .modellek import Kurzus, Valasz
from .FileHandler import FileHandler


api = APIRouter()
file_handler = FileHandler()

@api.get("/kurzusok", response_model=List[Kurzus])
async def get_osszes_kurzus():

    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")

    kurzuslist = [Kurzus(**k) for k in kurzusok]    
    return kurzuslist

@api.post("/kurzusok", response_model=Valasz)
async def uj_kurzus(kurzus: Kurzus):

    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    
    #Kurzus formazasa dictbe
    kurzus = kurzus.model_dump()
    for k in kurzusok:
        if k["id"] == kurzus["id"]:
            return Valasz(uzenet = "Ez a kurzus id foglalt")

    kurzusok.append(kurzus)
    file_handler.UpdateKurzusok(kurzusok)
    return Valasz(uzenet = "Sikeres felvétel")
    
@api.get("/kurzusok/filter", response_model=List[Kurzus])
async def get_kurzusok_filter(nap_idopont: str = None, oktato_email: str = None, tipus: str = None, evfolyam: str = None, helyszin: str = None, max_letszam: int = None):

    filters = {"nap_idopont": nap_idopont, "oktato_email": oktato_email, "tipus": tipus, "evfolyam": evfolyam, "helyszin": helyszin, "max_letszam": max_letszam}
    filtercount = 0
    
    for k,v in filters.items():
        if v is not None:
            filtercount+=1
        if filtercount > 1:
            raise HTTPException(status_code=400, detail="Csak egy filtert lehet megadni")
        if k == "evfolyam" and evfolyam and evfolyam.isdigit():
            filters[k] = int(v)
        
    if filtercount == 0:
        raise HTTPException(status_code=400, detail="Adjon meg egy filtert")
    
    filter = {key:value for key,value in filters.items() if value}
    filter_key, filter_value = next(iter(filter.items()))

    kurzusok_filtered = []
    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    
    for k in kurzusok:
        if filter_key == "oktato_email":  #külön statementekben continue-val, hiszen keyerror lenne az elif ágon
            if k["oktato"]["email"] == filter_value:
                kurzusok_filtered.append(k)
            else:
                continue
        elif k[filter_key] == filter_value:
            kurzusok_filtered.append(k)

    return kurzusok_filtered #mive elvárt response List, ezét nem létező esetén is [] a return

@api.get("/kurzusok/filters", response_model=List[Kurzus])
async def get_kurzusok_filters(nap_idopont: str = None, oktato_email: str = None, tipus: str = None, evfolyam: str = None, helyszin: str = None, max_letszam: int = None):

    filters = {"nap_idopont": nap_idopont, "oktato_email": oktato_email, "tipus": tipus, "evfolyam": evfolyam, "helyszin": helyszin, "max_letszam": max_letszam}
    filtercount = 0

    for f in filters:
        if filters[f] is not None:
            filtercount+=1
            if f == "evfolyam":
                try:        #mivel a paraméterekben str tipusu, de a jsonben intként szerepel
                    filters[f] = int(filters[f])
                except:
                    raise TypeError("Evfolyam nem egy szám")        

    if filtercount == 0:
        raise HTTPException(status_code=400, detail="Adjon meg legalább egy filtert")
    
    list = []
    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    for k in kurzusok:
        match_count = 0
        for f in filters:
            if f == "oktato_email":
                if k["oktato"]["email"] == filters[f]:
                    match_count+=1
                continue
            elif k[f] == filters[f]:
                match_count+=1
        if match_count == filtercount: #minden f kulcsu filter erteke egyezik a kurzus f kulcsu ertekevel
            list.append(k)
    return list

@api.put("/kurzusok/{kurzus_id}", response_model=Kurzus)   
async def update_kurzus(kurzus_id: int, kurzus: Kurzus):
    kurzus = kurzus.model_dump() #dict parse

    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    
    for i,k in enumerate(kurzusok):
        if k["id"] == kurzus_id:
            kurzusok[i] = kurzus #kell az indexelés mivel k=.. esetén nem frissíti helyben a lista értékét
            file_handler.UpdateKurzusok(kurzusok)
            return kurzus
        
    raise HTTPException(status_code=404, detail="Nincs ilyen kurzus")

@api.delete("/kurzusok/{kurzus_id}")
async def delete_kurzus(kurzus_id: int):

    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    
    for k in kurzusok:
        if k["id"] == kurzus_id:
            kurzusok.remove(k)
            file_handler.UpdateKurzusok(kurzusok)
            return Valasz(uzenet=f"A {kurzus_id} számú kurzus sikeresen törlve lett")

    raise HTTPException(status_code=404, detail=f"Nem létezik {kurzus_id} id-val kurzus")

@api.get("/kurzusok/hallgatok/{hallgato_id}", response_model=List[Kurzus])
async def get_hallgato_kurzusai(hallgato_id: int):
    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")
    
    hallgato_kurzusai = []
    [[hallgato_kurzusai.append(k) for h in k['hallgatok'] if h['id'] == hallgato_id] for k in kurzusok]

    if not hallgato_kurzusai:
        raise HTTPException(status_code=404, detail="Nem szerepel egyik kurzuson se ez a hallgató")
    return hallgato_kurzusai


@api.get("/kurzusok/{kurzus_id}/hallgatok/{hallgato_id}", response_model=Valasz)
async def get_hallgato_kurzuson(kurzus_id: int, hallgato_id: int):
    
    kurzusok = file_handler.ReadKurzusok()
    if not kurzusok:
        raise HTTPException(status_code=404, detail="Nincs kurzusok.json file")

    if not [1 for k in kurzusok if k['id'] == kurzus_id]:
        raise HTTPException(status_code=404, detail= "Nincs ilyen kurzus")

    if [[1 for h in k['hallgatok'] if h['id'] == hallgato_id] for k in kurzusok if kurzus_id == k['id']][0]: #pythonosabb megoldas
        return Valasz(uzenet="Igen")
    
    return Valasz(uzenet="Nem")

    
    