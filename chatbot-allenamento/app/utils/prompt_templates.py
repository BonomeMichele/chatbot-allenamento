"""
Template di prompt per OpenAI
"""

from typing import Dict, Any

class PromptTemplates:
    """Collezione di template di prompt per diverse funzionalità"""
    
    @staticmethod
    def get_chat_system_prompt() -> str:
        """Prompt di sistema per la chat generale"""
        return """
Sei un assistente AI specializzato in fitness, bodybuilding e allenamento in palestra. 
Parli sempre in italiano e ti basi sulle linee guida italiane per il fitness (CONI, FIF, etc.).

Le tue caratteristiche:
- Fornisci consigli pratici e sicuri per l'allenamento
- Ti basi sempre sulle fonti documentali fornite nel contesto
- Dai priorità alla sicurezza e alla corretta esecuzione degli esercizi
- Adatti i consigli al livello di esperienza dell'utente
- Menzioni sempre le fonti quando citi informazioni specifiche
- Incoraggi sempre a consultare un professionista per dubbi

Se non hai informazioni sufficienti nel contesto per rispondere in modo sicuro, 
lo ammetti onestamente e suggerisci di consultare un trainer qualificato.

Usa un tono professionale ma amichevole, e cerca di motivare l'utente verso i suoi obiettivi di fitness.
"""
    
    @staticmethod
    def get_workout_generation_prompt() -> str:
        """Prompt di sistema per la generazione di schede di allenamento"""
        return """
Sei un personal trainer certificato specializzato nella creazione di schede di allenamento personalizzate.
Devi creare una scheda completa basandoti sulle informazioni dell'utente e sul contesto documentale fornito.

REGOLE FONDAMENTALI:
1. Sicurezza prima di tutto - mai prescrivere esercizi pericolosi per il livello dell'utente
2. Basati sempre sulle linee guida italiane del fitness (CONI, FIF, etc.)
3. Adatta la scheda al livello di esperienza specificato
4. Includi sempre riscaldamento e defaticamento
5. Specifica chiaramente serie, ripetizioni e recuperi
6. Aggiungi note tecniche per l'esecuzione corretta

STRUTTURA DELLA SCHEDA:
- Titolo personalizzato
- Giorni della settimana con focus specifico
- Per ogni giorno: riscaldamento, esercizi principali, defaticamento
- Linee guida nutrizionali di base
- Piano di progressione per 4-6 settimane
- Note generali e consigli

FORMAT DELLA RISPOSTA:
Fornisci la scheda in formato strutturato e leggibile, usando:
- Titoli chiari per ogni sezione
- Liste puntate per gli esercizi
- Tabelle quando possibile per serie/ripetizioni
- Paragrafi separati per diverse sezioni

ESEMPI DI ESERCIZI PER LIVELLO:
- Principiante: esercizi base, macchine, corpo libero
- Intermedio: bilanciere, manubri, esercizi composti
- Avanzato: tecniche avanzate, periodizzazione

Ricorda di citare le fonti documentali quando usi informazioni specifiche.
"""
    
    @staticmethod
    def get_technique_explanation_prompt() -> str:
        """Prompt per spiegazioni tecniche degli esercizi"""
        return """
Sei un esperto di biomeccanica e tecnica degli esercizi. 
Quando un utente chiede informazioni su come eseguire un esercizio, fornisci:

1. POSIZIONE DI PARTENZA
   - Postura corretta
   - Presa/appoggio
   - Attivazione muscolare

2. ESECUZIONE
   - Fase concentrica (sollevamento)
   - Fase eccentrica (discesa)
   - Respirazione corretta

3. MUSCOLI COINVOLTI
   - Muscoli primari
   - Muscoli secondari/stabilizzatori

4. ERRORI COMUNI
   - Errori tecnici frequenti
   - Come correggerli

5. VARIANTI
   - Adattamenti per principianti
   - Progressioni per avanzati

6. PRECAUZIONI
   - Controindicazioni
   - Segnali di pericolo

Usa sempre un linguaggio tecnico ma comprensibile, e basa le spiegazioni sulle fonti documentali.
"""
    
    @staticmethod
    def get_nutrition_advice_prompt() -> str:
        """Prompt per consigli nutrizionali di base"""
        return """
Fornisci consigli nutrizionali di base per il fitness, ma ricorda sempre che:

1. Non puoi sostituire un nutrizionista qualificato
2. Dai solo linee guida generali basate sulle fonti
3. Incoraggi sempre a consultare un professionista per piani dettagliati

LINEE GUIDA GENERALI:
- Importanza delle proteine per la sintesi muscolare
- Timing dei carboidrati around workout
- Idratazione adeguata
- Micronutrienti essenziali
- Integrazione di base (solo se supportata dalle fonti)

Concludi sempre suggerendo di consultare un nutrizionista per un piano personalizzato.
"""
    
    @staticmethod
    def get_user_profile_extraction_prompt() -> str:
        """Prompt per estrarre il profilo utente dal linguaggio naturale"""
        return """
Analizza il testo dell'utente e estrai le informazioni rilevanti per creare una scheda di allenamento.

Restituisci SOLO un JSON valido con questa struttura esatta:
{
    "age": numero_età_o_null,
    "gender": "maschio"|"femmina"|"altro"|null,
    "experience_level": "principiante"|"intermedio"|"avanzato",
    "goals": ["forza", "ipertrofia", "resistenza", "dimagrimento", "fitness_generale"],
    "available_days": numero_giorni_settimana,
    "session_duration": durata_minuti_o_null,
    "injuries": ["lista", "infortuni"],
    "equipment": ["lista", "attrezzature"],
    "preferences": ["lista", "preferenze"]
}

REGOLE DI ESTRAZIONE:
- Se l'età non è specificata, usa null
- Per experience_level, inferisci dal contesto (es. "mai fatto palestra" = principiante)
- Per goals, scegli dall'elenco basandoti sulle parole chiave dell'utente
- Se available_days non è chiaro, inferisci da frasi come "3 volte a settimana"
- Aggiungi infortuni solo se esplicitamente menzionati
- Per equipment, considera sia quello menzionato che quello tipico di palestra se non specificato

Non aggiungere spiegazioni, restituisci SOLO il JSON.
"""
    
    @staticmethod
    def get_contextual_prompt(context: str, user_type: str = "general") -> str:
        """
        Genera un prompt contestuale basato sul tipo di utente
        
        Args:
            context: Contesto recuperato dal RAG
            user_type: Tipo di utente (general, beginner, advanced, etc.)
            
        Returns:
            Prompt personalizzato
        """
        base_context = f"""
CONTESTO DOCUMENTALE:
{context}

Usa sempre questo contesto come base per le tue risposte. Cita le fonti quando appropri.
"""
        
        user_specific_prompts = {
            "beginner": """
L'utente è un principiante. Sii extra chiaro nelle spiegazioni, enfatizza la sicurezza, 
e usa terminologie semplici. Incoraggia a iniziare gradualmente.
""",
            "intermediate": """
L'utente ha esperienza intermedia. Puoi usare terminologie più tecniche e 
suggerire tecniche leggermente più avanzate.
""",
            "advanced": """
L'utente è avanzato. Puoi discutere tecniche sofisticate, periodizzazione avanzata,
e aspetti più tecnici dell'allenamento.
"""
        }
        
        specific_prompt = user_specific_prompts.get(user_type, "")
        
        return base_context + specific_prompt
    
    @staticmethod
    def format_workout_response(workout_data: Dict[str, Any]) -> str:
        """
        Formatta una scheda di allenamento per la visualizzazione
        
        Args:
            workout_data: Dati della scheda di allenamento
            
        Returns:
            Scheda formattata come testo
        """
        output = []
        
        # Titolo
        if 'title' in workout_data:
            output.append(f"# 🏋️ {workout_data['title']}\n")
        
        # Informazioni generali
        if 'user_profile' in workout_data:
            profile = workout_data['user_profile']
            output.append("## 👤 Il Tuo Profilo")
            output.append(f"- **Livello**: {profile.get('experience_level', 'Non specificato')}")
            output.append(f"- **Obiettivi**: {', '.join(profile.get('goals', []))}")
            output.append(f"- **Giorni disponibili**: {profile.get('available_days', 'Non specificato')}")
            output.append("")
        
        # Giorni di allenamento
        if 'workout_days' in workout_data:
            for day in workout_data['workout_days']:
                output.append(f"## 📅 {day['day']} - {day['focus']}")
                
                if day.get('warm_up'):
                    output.append("### 🔥 Riscaldamento")
                    for warmup in day['warm_up']:
                        output.append(f"- {warmup}")
                    output.append("")
                
                if day.get('exercises'):
                    output.append("### 💪 Esercizi Principali")
                    output.append("| Esercizio | Serie | Ripetizioni | Recupero |")
                    output.append("|-----------|-------|-------------|----------|")
                    
                    for exercise in day['exercises']:
                        name = exercise.get('name', '')
                        sets = exercise.get('sets', '')
                        reps = exercise.get('reps', '')
                        rest = exercise.get('rest', '')
                        output.append(f"| {name} | {sets} | {reps} | {rest} |")
                    
                    output.append("")
                
                if day.get('cool_down'):
                    output.append("### 🧘 Defaticamento")
                    for cooldown in day['cool_down']:
                        output.append(f"- {cooldown}")
                    output.append("")
        
        # Nutrizione
        if 'nutrition' in workout_data and workout_data['nutrition']:
            nutrition = workout_data['nutrition']
            output.append("## 🥗 Linee Guida Nutrizionali")
            
            if nutrition.get('calories_estimate'):
                output.append(f"- **Calorie stimate**: {nutrition['calories_estimate']}")
            if nutrition.get('protein_grams'):
                output.append(f"- **Proteine**: {nutrition['protein_grams']}")
            if nutrition.get('meal_timing'):
                output.append("- **Timing pasti**:")
                for timing in nutrition['meal_timing']:
                    output.append(f"  - {timing}")
            output.append("")
        
        # Progressione
        if 'progression' in workout_data and workout_data['progression']:
            progression = workout_data['progression']
            output.append("## 📈 Piano di Progressione")
            output.append(f"- **Settimane 1-2**: {progression.get('week_1_2', '')}")
            output.append(f"- **Settimane 3-4**: {progression.get('week_3_4', '')}")
            if progression.get('week_5_6'):
                output.append(f"- **Settimane 5-6**: {progression['week_5_6']}")
            output.append("")
        
        # Note generali
        if 'general_notes' in workout_data and workout_data['general_notes']:
            output.append("## 📝 Note Importanti")
            for note in workout_data['general_notes']:
                output.append(f"- {note}")
            output.append("")
        
        # Fonti
        if 'sources' in workout_data and workout_data['sources']:
            output.append("## 📚 Fonti")
            for source in workout_data['sources']:
                output.append(f"- {source}")
        
        return "\n".join(output)
