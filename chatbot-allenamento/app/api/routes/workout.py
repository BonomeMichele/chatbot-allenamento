"""
Route API per gestione schede allenamento
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.workout import (
    WorkoutGenerationRequest, WorkoutGenerationResponse, 
    WorkoutPlanResponse, WorkoutListResponse, WorkoutDeleteResponse
)
from app.dependencies import get_workout_service
from app.services.workout_service import WorkoutService
from app.core.error_handler import ChatbotException

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/workout/generate", response_model=WorkoutGenerationResponse)
async def generate_workout(
    request: WorkoutGenerationRequest,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Genera una nuova scheda di allenamento personalizzata
    """
    try:
        workout_plan = await workout_service.generate_workout_plan(
            user_input=request.user_input,
            chat_id=request.chat_id
        )
        
        # Converti in response schema
        workout_response = WorkoutPlanResponse(
            id=workout_plan.id,
            title=workout_plan.title,
            workout_days=[
                {
                    "day": day.day,
                    "focus": day.focus,
                    "warm_up": day.warm_up,
                    "exercises": [
                        {
                            "name": ex.name,
                            "sets": ex.sets,
                            "reps": ex.reps,
                            "rest": ex.rest,
                            "weight": ex.weight,
                            "notes": ex.notes,
                            "muscle_groups": ex.muscle_groups
                        }
                        for ex in day.exercises
                    ],
                    "cool_down": day.cool_down,
                    "duration_minutes": day.duration_minutes
                }
                for day in workout_plan.workout_days
            ],
            nutrition={
                "calories_estimate": workout_plan.nutrition.calories_estimate if workout_plan.nutrition else None,
                "protein_grams": workout_plan.nutrition.protein_grams if workout_plan.nutrition else None,
                "meal_timing": workout_plan.nutrition.meal_timing if workout_plan.nutrition else [],
                "hydration": workout_plan.nutrition.hydration if workout_plan.nutrition else None,
                "supplements": workout_plan.nutrition.supplements if workout_plan.nutrition else []
            } if workout_plan.nutrition else None,
            progression={
                "week_1_2": workout_plan.progression.week_1_2 if workout_plan.progression else "",
                "week_3_4": workout_plan.progression.week_3_4 if workout_plan.progression else "",
                "week_5_6": workout_plan.progression.week_5_6 if workout_plan.progression else None,
                "deload_week": workout_plan.progression.deload_week if workout_plan.progression else None,
                "progression_notes": workout_plan.progression.progression_notes if workout_plan.progression else []
            } if workout_plan.progression else None,
            general_notes=workout_plan.general_notes,
            sources=workout_plan.sources,
            created_at=workout_plan.created_at
        )
        
    except HTTPException:
        raise
    except ChatbotException as e:
        logger.error(f"Chatbot error in get_workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_workout: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.delete("/workout/{workout_id}", response_model=WorkoutDeleteResponse)
async def delete_workout(
    workout_id: str,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Elimina una scheda di allenamento specifica
    """
    try:
        success = await workout_service.delete_workout_plan(workout_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Scheda di allenamento non trovata")
        
        return WorkoutDeleteResponse(
            success=True,
            message="Scheda di allenamento eliminata con successo",
            deleted_workout_id=workout_id
        )
        
    except HTTPException:
        raise
    except ChatbotException as e:
        logger.error(f"Chatbot error in delete_workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_workout: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.post("/workout/{workout_id}/variations", response_model=WorkoutGenerationResponse)
async def create_workout_variation(
    workout_id: str,
    variation_type: str = Query(..., description="Tipo di variazione: easier, harder, different_focus"),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Crea una variazione di una scheda esistente
    """
    try:
        variation_workout = await workout_service.generate_workout_variations(
            base_workout_id=workout_id,
            variation_type=variation_type
        )
        
        # Converti in response schema
        workout_response = WorkoutPlanResponse(
            id=variation_workout.id,
            title=variation_workout.title,
            workout_days=[
                {
                    "day": day.day,
                    "focus": day.focus,
                    "warm_up": day.warm_up,
                    "exercises": [
                        {
                            "name": ex.name,
                            "sets": ex.sets,
                            "reps": ex.reps,
                            "rest": ex.rest,
                            "weight": ex.weight,
                            "notes": ex.notes,
                            "muscle_groups": ex.muscle_groups
                        }
                        for ex in day.exercises
                    ],
                    "cool_down": day.cool_down,
                    "duration_minutes": day.duration_minutes
                }
                for day in variation_workout.workout_days
            ],
            nutrition={
                "calories_estimate": variation_workout.nutrition.calories_estimate if variation_workout.nutrition else None,
                "protein_grams": variation_workout.nutrition.protein_grams if variation_workout.nutrition else None,
                "meal_timing": variation_workout.nutrition.meal_timing if variation_workout.nutrition else [],
                "hydration": variation_workout.nutrition.hydration if variation_workout.nutrition else None,
                "supplements": variation_workout.nutrition.supplements if variation_workout.nutrition else []
            } if variation_workout.nutrition else None,
            progression={
                "week_1_2": variation_workout.progression.week_1_2 if variation_workout.progression else "",
                "week_3_4": variation_workout.progression.week_3_4 if variation_workout.progression else "",
                "week_5_6": variation_workout.progression.week_5_6 if variation_workout.progression else None,
                "deload_week": variation_workout.progression.deload_week if variation_workout.progression else None,
                "progression_notes": variation_workout.progression.progression_notes if variation_workout.progression else []
            } if variation_workout.progression else None,
            general_notes=variation_workout.general_notes,
            sources=variation_workout.sources,
            created_at=variation_workout.created_at
        )
        
        return WorkoutGenerationResponse(
            success=True,
            workout_plan=workout_response,
            message=f"Variazione '{variation_type}' creata con successo!",
            chat_id=None
        )
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in create_workout_variation: {e}")
        return WorkoutGenerationResponse(
            success=False,
            workout_plan=None,
            message=f"Errore nella creazione della variazione: {str(e)}",
            chat_id=None
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_workout_variation: {e}")
        return WorkoutGenerationResponse(
            success=False,
            workout_plan=None,
            message="Errore interno nella creazione della variazione",
            chat_id=None
        )

@router.get("/workout/recommendations", response_model=dict)
async def get_workout_recommendations(
    goals: List[str] = Query(..., description="Lista degli obiettivi"),
    experience_level: str = Query(..., description="Livello di esperienza"),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Ottiene raccomandazioni per schede basate su obiettivi e livello
    """
    try:
        recommendations = await workout_service.get_workout_recommendations(
            user_goals=goals,
            experience_level=experience_level
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "message": "Raccomandazioni generate con successo"
        }
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in get_workout_recommendations: {e}")
        return {
            "success": False,
            "recommendations": [],
            "message": f"Errore nel recupero delle raccomandazioni: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_workout_recommendations: {e}")
        return {
            "success": False,
            "recommendations": [],
            "message": "Errore interno nel recupero delle raccomandazioni"
        }plan.progression else "",
                "week_5_6": workout_plan.progression.week_5_6 if workout_plan.progression else None,
                "deload_week": workout_plan.progression.deload_week if workout_plan.progression else None,
                "progression_notes": workout_plan.progression.progression_notes if workout_plan.progression else []
            } if workout_plan.progression else None,
            general_notes=workout_plan.general_notes,
            sources=workout_plan.sources,
            created_at=workout_plan.created_at
        )
        
        return WorkoutGenerationResponse(
            success=True,
            workout_plan=workout_response,
            message="Scheda di allenamento generata con successo!",
            chat_id=request.chat_id
        )
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in generate_workout: {e}")
        return WorkoutGenerationResponse(
            success=False,
            workout_plan=None,
            message=f"Errore nella generazione della scheda: {str(e)}",
            chat_id=request.chat_id
        )
    except Exception as e:
        logger.error(f"Unexpected error in generate_workout: {e}")
        return WorkoutGenerationResponse(
            success=False,
            workout_plan=None,
            message="Errore interno nella generazione della scheda",
            chat_id=request.chat_id
        )

@router.get("/workout/list", response_model=WorkoutListResponse)
async def list_workouts(
    limit: int = Query(50, ge=1, le=100),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Lista tutte le schede di allenamento disponibili
    """
    try:
        workouts = await workout_service.list_workout_plans(limit=limit)
        
        return WorkoutListResponse(
            workouts=[
                {
                    "id": workout["id"],
                    "title": workout["title"],
                    "created_at": workout["created_at"],
                    "total_days": workout["total_days"],
                    "total_exercises": workout["total_exercises"]
                }
                for workout in workouts
            ],
            total=len(workouts)
        )
        
    except ChatbotException as e:
        logger.error(f"Chatbot error in list_workouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in list_workouts: {e}")
        raise HTTPException(status_code=500, detail="Errore interno del server")

@router.get("/workout/{workout_id}", response_model=WorkoutPlanResponse)
async def get_workout(
    workout_id: str,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Ottiene i dettagli di una scheda di allenamento specifica
    """
    try:
        workout_plan = await workout_service.get_workout_plan(workout_id)
        
        if not workout_plan:
            raise HTTPException(status_code=404, detail="Scheda di allenamento non trovata")
        
        # Converti in response schema (stesso codice del generate_workout)
        return WorkoutPlanResponse(
            id=workout_plan.id,
            title=workout_plan.title,
            workout_days=[
                {
                    "day": day.day,
                    "focus": day.focus,
                    "warm_up": day.warm_up,
                    "exercises": [
                        {
                            "name": ex.name,
                            "sets": ex.sets,
                            "reps": ex.reps,
                            "rest": ex.rest,
                            "weight": ex.weight,
                            "notes": ex.notes,
                            "muscle_groups": ex.muscle_groups
                        }
                        for ex in day.exercises
                    ],
                    "cool_down": day.cool_down,
                    "duration_minutes": day.duration_minutes
                }
                for day in workout_plan.workout_days
            ],
            nutrition={
                "calories_estimate": workout_plan.nutrition.calories_estimate if workout_plan.nutrition else None,
                "protein_grams": workout_plan.nutrition.protein_grams if workout_plan.nutrition else None,
                "meal_timing": workout_plan.nutrition.meal_timing if workout_plan.nutrition else [],
                "hydration": workout_plan.nutrition.hydration if workout_plan.nutrition else None,
                "supplements": workout_plan.nutrition.supplements if workout_plan.nutrition else []
            } if workout_plan.nutrition else None,
            progression={
                "week_1_2": workout_plan.progression.week_1_2 if workout_plan.progression else "",
                "week_3_4": workout_plan.progression.week_3_4 if workout_
