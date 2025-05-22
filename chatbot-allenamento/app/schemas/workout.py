"""
Schemi Pydantic per le API workout
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkoutGenerationRequest(BaseModel):
    """Schema per la richiesta di generazione scheda"""
    user_input: str = Field(..., min_length=10, max_length=2000, description="Descrizione delle esigenze utente")
    chat_id: Optional[str] = Field(default=None, description="ID della chat associata")
    
    # Parametri opzionali per override
    age: Optional[int] = Field(default=None, ge=12, le=100, description="Età")
    experience_level: Optional[str] = Field(default=None, description="Livello esperienza")
    available_days: Optional[int] = Field(default=None, ge=1, le=7, description="Giorni disponibili")
    goals: Optional[List[str]] = Field(default=None, description="Obiettivi specifici")

class ExerciseResponse(BaseModel):
    """Schema per un esercizio nella risposta"""
    name: str = Field(..., description="Nome dell'esercizio")
    sets: int = Field(..., description="Numero di serie")
    reps: str = Field(..., description="Numero di ripetizioni")
    rest: str = Field(..., description="Tempo di recupero")
    weight: Optional[str] = Field(default=None, description="Peso consigliato")
    notes: Optional[str] = Field(default=None, description="Note tecniche")
    muscle_groups: List[str] = Field(default_factory=list, description="Gruppi muscolari")

class WorkoutDayResponse(BaseModel):
    """Schema per un giorno di allenamento nella risposta"""
    day: str = Field(..., description="Giorno della settimana")
    focus: str = Field(..., description="Focus del giorno")
    warm_up: List[str] = Field(default_factory=list, description="Riscaldamento")
    exercises: List[ExerciseResponse] = Field(..., description="Esercizi principali")
    cool_down: List[str] = Field(default_factory=list, description="Defaticamento")
    duration_minutes: Optional[int] = Field(default=None, description="Durata stimata")

class NutritionResponse(BaseModel):
    """Schema per le linee guida nutrizionali"""
    calories_estimate: Optional[str] = Field(default=None, description="Stima calorie")
    protein_grams: Optional[str] = Field(default=None, description="Proteine consigliate")
    meal_timing: List[str] = Field(default_factory=list, description="Timing pasti")
    hydration: Optional[str] = Field(default=None, description="Idratazione")
    supplements: List[str] = Field(default_factory=list, description="Integratori")

class ProgressionResponse(BaseModel):
    """Schema per il piano di progressione"""
    week_1_2: str = Field(..., description="Settimane 1-2")
    week_3_4: str = Field(..., description="Settimane 3-4")
    week_5_6: Optional[str] = Field(default=None, description="Settimane 5-6")
    deload_week: Optional[str] = Field(default=None, description="Settimana scarico")
    progression_notes: List[str] = Field(default_factory=list, description="Note progressione")

class WorkoutPlanResponse(BaseModel):
    """Schema per la risposta completa della scheda"""
    id: str = Field(..., description="ID della scheda")
    title: str = Field(..., description="Titolo della scheda")
    workout_days: List[WorkoutDayResponse] = Field(..., description="Giorni allenamento")
    nutrition: Optional[NutritionResponse] = Field(default=None, description="Nutrizione")
    progression: Optional[ProgressionResponse] = Field(default=None, description="Progressione")
    general_notes: List[str] = Field(default_factory=list, description="Note generali")
    sources: List[str] = Field(default_factory=list, description="Fonti utilizzate")
    created_at: datetime = Field(..., description="Data creazione")
    
class WorkoutGenerationResponse(BaseModel):
    """Schema per la risposta di generazione scheda"""
    success: bool = Field(..., description="Successo operazione")
    workout_plan: Optional[WorkoutPlanResponse] = Field(default=None, description="Scheda generata")
    message: str = Field(..., description="Messaggio di risposta")
    chat_id: Optional[str] = Field(default=None, description="ID chat associata")

class WorkoutListItem(BaseModel):
    """Schema per un elemento nella lista schede"""
    id: str = Field(..., description="ID della scheda")
    title: str = Field(..., description="Titolo")
    created_at: datetime = Field(..., description="Data creazione")
    total_days: int = Field(..., description="Giorni totali")
    total_exercises: int = Field(..., description="Esercizi totali")

class WorkoutListResponse(BaseModel):
    """Schema per la lista delle schede"""
    workouts: List[WorkoutListItem] = Field(..., description="Lista schede")
    total: int = Field(..., description="Numero totale")

class WorkoutDeleteResponse(BaseModel):
    """Schema per la risposta di eliminazione scheda"""
    success: bool = Field(..., description="Successo operazione")
    message: str = Field(..., description="Messaggio conferma")
    deleted_workout_id: str = Field(..., description="ID scheda eliminata")
