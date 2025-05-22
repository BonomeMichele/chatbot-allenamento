"""
Formattazione schede per visualizzazione
"""

import logging
from typing import Dict, Any, List
from app.models.workout import WorkoutPlan, WorkoutDay, Exercise

logger = logging.getLogger(__name__)

class WorkoutFormatter:
    """Formattatore per schede di allenamento"""
    
    @staticmethod
    def format_for_chat(workout_plan: WorkoutPlan) -> str:
        """
        Formatta una scheda per la visualizzazione nella chat
        
        Args:
            workout_plan: Scheda da formattare
            
        Returns:
            Scheda formattata come HTML/Markdown
        """
        output = []
        
        # Titolo principale
        output.append(f'<div class="workout-card">')
        output.append(f'<h2 class="workout-title">🏋️ {workout_plan.title}</h2>')
        
        # Profilo utente
        profile = workout_plan.user_profile
        output.append('<div class="profile-section">')
        output.append('<h3>👤 Il Tuo Profilo</h3>')
        output.append('<ul>')
        
        if profile.age:
            output.append(f'<li><strong>Età:</strong> {profile.age} anni</li>')
        if profile.gender:
            output.append(f'<li><strong>Genere:</strong> {profile.gender.value.title()}</li>')
        
        output.append(f'<li><strong>Livello:</strong> {profile.experience_level.value.title()}</li>')
        
        goals_str = ', '.join([goal.value.replace('_', ' ').title() for goal in profile.goals])
        output.append(f'<li><strong>Obiettivi:</strong> {goals_str}</li>')
        output.append(f'<li><strong>Giorni/settimana:</strong> {profile.available_days}</li>')
        
        if profile.session_duration:
            output.append(f'<li><strong>Durata sessione:</strong> {profile.session_duration} minuti</li>')
        
        if profile.injuries:
            injuries_str = ', '.join(profile.injuries)
            output.append(f'<li><strong>Limitazioni:</strong> {injuries_str}</li>')
        
        output.append('</ul>')
        output.append('</div>')
        
        # Giorni di allenamento
        for i, day in enumerate(workout_plan.workout_days):
            output.append(f'<div class="workout-day">')
            output.append(f'<h3>📅 {day.day} - {day.focus}</h3>')
            
            # Riscaldamento
            if day.warm_up:
                output.append('<h4>🔥 Riscaldamento</h4>')
                output.append('<ul>')
                for warmup in day.warm_up:
                    output.append(f'<li>{warmup}</li>')
                output.append('</ul>')
            
            # Esercizi principali
            if day.exercises:
                output.append('<h4>💪 Esercizi Principali</h4>')
                output.append(WorkoutFormatter._format_exercises_table(day.exercises))
            
            # Defaticamento
            if day.cool_down:
                output.append('<h4>🧘 Defaticamento</h4>')
                output.append('<ul>')
                for cooldown in day.cool_down:
                    output.append(f'<li>{cooldown}</li>')
                output.append('</ul>')
            
            # Durata stimata
            if day.duration_minutes:
                output.append(f'<p><strong>⏱️ Durata stimata:</strong> {day.duration_minutes} minuti</p>')
            
            output.append('</div>')
        
        # Nutrizione
        if workout_plan.nutrition:
            nutrition = workout_plan.nutrition
            output.append('<div class="nutrition-section">')
            output.append('<h3>🥗 Linee Guida Nutrizionali</h3>')
            output.append('<ul>')
            
            if nutrition.calories_estimate:
                output.append(f'<li><strong>Calorie stimate:</strong> {nutrition.calories_estimate}</li>')
            if nutrition.protein_grams:
                output.append(f'<li><strong>Proteine:</strong> {nutrition.protein_grams}</li>')
            if nutrition.hydration:
                output.append(f'<li><strong>Idratazione:</strong> {nutrition.hydration}</li>')
            
            if nutrition.meal_timing:
                output.append('<li><strong>Timing pasti:</strong></li>')
                output.append('<ul>')
                for timing in nutrition.meal_timing:
                    output.append(f'<li>{timing}</li>')
                output.append('</ul>')
            
            if nutrition.supplements:
                supplements_str = ', '.join(nutrition.supplements)
                output.append(f'<li><strong>Integratori:</strong> {supplements_str}</li>')
            
            output.append('</ul>')
            output.append('</div>')
        
        # Progressione
        if workout_plan.progression:
            prog = workout_plan.progression
            output.append('<div class="progression-section">')
            output.append('<h3>📈 Piano di Progressione</h3>')
            output.append('<ul>')
            output.append(f'<li><strong>Settimane 1-2:</strong> {prog.week_1_2}</li>')
            output.append(f'<li><strong>Settimane 3-4:</strong> {prog.week_3_4}</li>')
            
            if prog.week_5_6:
                output.append(f'<li><strong>Settimane 5-6:</strong> {prog.week_5_6}</li>')
            if prog.deload_week:
                output.append(f'<li><strong>Settimana scarico:</strong> {prog.deload_week}</li>')
            
            if prog.progression_notes:
                output.append('<li><strong>Note:</strong></li>')
                output.append('<ul>')
                for note in prog.progression_notes:
                    output.append(f'<li>{note}</li>')
                output.append('</ul>')
            
            output.append('</ul>')
            output.append('</div>')
        
        # Note generali
        if workout_plan.general_notes:
            output.append('<div class="notes-section">')
            output.append('<h3>📝 Note Importanti</h3>')
            output.append('<ul>')
            for note in workout_plan.general_notes:
                output.append(f'<li>{note}</li>')
            output.append('</ul>')
            output.append('</div>')
        
        output.append('</div>')
        
        return ''.join(output)
    
    @staticmethod
    def _format_exercises_table(exercises: List[Exercise]) -> str:
        """
        Formatta una lista di esercizi come tabella HTML
        
        Args:
            exercises: Lista di esercizi
            
        Returns:
            Tabella HTML formattata
        """
        if not exercises:
            return '<p>Nessun esercizio specificato</p>'
        
        table = ['<table class="exercise-table">']
        
        # Header
        table.append('<thead>')
        table.append('<tr>')
        table.append('<th>Esercizio</th>')
        table.append('<th>Serie</th>')
        table.append('<th>Ripetizioni</th>')
        table.append('<th>Recupero</th>')
        if any(ex.weight for ex in exercises):
            table.append('<th>Peso</th>')
        table.append('</tr>')
        table.append('</thead>')
        
        # Body
        table.append('<tbody>')
        for exercise in exercises:
            table.append('<tr>')
            table.append(f'<td><strong>{exercise.name}</strong>')
            
            # Aggiungi note se presenti
            if exercise.notes:
                table.append(f'<br><small><em>{exercise.notes}</em></small>')
            
            # Aggiungi gruppi muscolari se presenti
            if exercise.muscle_groups:
                muscles = ', '.join(exercise.muscle_groups)
                table.append(f'<br><small>🎯 {muscles}</small>')
            
            table.append('</td>')
            table.append(f'<td>{exercise.sets}</td>')
            table.append(f'<td>{exercise.reps}</td>')
            table.append(f'<td>{exercise.rest}</td>')
            
            if any(ex.weight for ex in exercises):
                weight = exercise.weight or '-'
                table.append(f'<td>{weight}</td>')
            
            table.append('</tr>')
        
        table.append('</tbody>')
        table.append('</table>')
        
        return ''.join(table)
    
    @staticmethod
    def format_for_print(workout_plan: WorkoutPlan) -> str:
        """
        Formatta una scheda per la stampa (testo semplice)
        
        Args:
            workout_plan: Scheda da formattare
            
        Returns:
            Scheda formattata come testo
        """
        output = []
        
        # Titolo
        output.append("=" * 60)
        output.append(f"  {workout_plan.title.upper()}")
        output.append("=" * 60)
        output.append("")
        
        # Profilo
        profile = workout_plan.user_profile
        output.append("PROFILO UTENTE:")
        output.append("-" * 20)
        
        if profile.age:
            output.append(f"Età: {profile.age} anni")
        if profile.gender:
            output.append(f"Genere: {profile.gender.value.title()}")
        
        output.append(f"Livello: {profile.experience_level.value.title()}")
        
        goals_str = ', '.join([goal.value.replace('_', ' ').title() for goal in profile.goals])
        output.append(f"Obiettivi: {goals_str}")
        output.append(f"Giorni/settimana: {profile.available_days}")
        
        if profile.session_duration:
            output.append(f"Durata sessione: {profile.session_duration} minuti")
        
        output.append("")
        
        # Giorni
        for day in workout_plan.workout_days:
            output.append(f"{day.day.upper()} - {day.focus.upper()}")
            output.append("-" * 40)
            
            if day.warm_up:
                output.append("RISCALDAMENTO:")
                for warmup in day.warm_up:
                    output.append(f"  • {warmup}")
                output.append("")
            
            if day.exercises:
                output.append("ESERCIZI:")
                for i, ex in enumerate(day.exercises, 1):
                    output.append(f"  {i}. {ex.name}")
                    output.append(f"     Serie: {ex.sets} | Ripetizioni: {ex.reps} | Recupero: {ex.rest}")
                    
                    if ex.weight:
                        output.append(f"     Peso: {ex.weight}")
                    if ex.notes:
                        output.append(f"     Note: {ex.notes}")
                    if ex.muscle_groups:
                        muscles = ', '.join(ex.muscle_groups)
                        output.append(f"     Muscoli: {muscles}")
                    output.append("")
            
            if day.cool_down:
                output.append("DEFATICAMENTO:")
                for cooldown in day.cool_down:
                    output.append(f"  • {cooldown}")
            
            output.append("")
        
        # Note generali
        if workout_plan.general_notes:
            output.append("NOTE IMPORTANTI:")
            output.append("-" * 20)
            for note in workout_plan.general_notes:
                output.append(f"• {note}")
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def format_summary(workout_plan: WorkoutPlan) -> Dict[str, Any]:
        """
        Crea un riassunto della scheda
        
        Args:
            workout_plan: Scheda da riassumere
            
        Returns:
            Dizionario con il riassunto
        """
        total_exercises = sum(len(day.exercises) for day in workout_plan.workout_days)
        total_sets = sum(
            sum(ex.sets for ex in day.exercises) 
            for day in workout_plan.workout_days
        )
        
        # Trova gruppi muscolari coinvolti
        muscle_groups = set()
        for day in workout_plan.workout_days:
            for ex in day.exercises:
                muscle_groups.update(ex.muscle_groups)
        
        # Calcola durata stimata totale
        total_duration = sum(
            day.duration_minutes or 60 
            for day in workout_plan.workout_days
        )
        
        return {
            'total_days': len(workout_plan.workout_days),
            'total_exercises': total_exercises,
            'total_sets': total_sets,
            'muscle_groups_covered': list(muscle_groups),
            'estimated_weekly_duration': total_duration,
            'experience_level': workout_plan.user_profile.experience_level.value,
            'primary_goals': [goal.value for goal in workout_plan.user_profile.goals],
            'has_nutrition_guide': workout_plan.nutrition is not None,
            'has_progression_plan': workout_plan.progression is not None
        }
