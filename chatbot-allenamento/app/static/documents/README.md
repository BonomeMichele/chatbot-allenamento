# 📚 Directory Documenti

Questa directory contiene i documenti utilizzati dal sistema RAG per generare schede di allenamento personalizzate.

## 📋 Formati Supportati

- **PDF** (.pdf)
- **Microsoft Word** (.docx)
- **Testo** (.txt)

## 📁 Documenti Consigliati

### Linee Guida Generali
- `linee_guida_aci.pdf` - Linee guida CONI/ACI per l'allenamento
- `linee_guida_fi.pdf` - Linee guida Fitness Italia (FIF)
- `programming.pdf` - Principi di programmazione dell'allenamento

### Esercizi e Tecnica
- `exercises.pdf` - Catalogo completo degli esercizi con descrizioni
- `anatomy.pdf` - Anatomia funzionale per l'allenamento
- `technique_guide.pdf` - Guide all'esecuzione corretta degli esercizi

### Nutrizione
- `nutrition_basics.pdf` - Principi base di nutrizione sportiva
- `supplements.pdf` - Guida agli integratori

### Specializzazioni
- `strength_training.pdf` - Allenamento per la forza
- `hypertrophy.pdf` - Allenamento per l'ipertrofia
- `endurance.pdf` - Allenamento di resistenza
- `rehabilitation.pdf` - Esercizi riabilitativi

## 🔄 Aggiornamento Documenti

1. **Aggiungi i tuoi documenti** in questa directory
2. **Riavvia l'applicazione** per indicizzare i nuovi file
3. **Verifica l'indicizzazione** nei log dell'applicazione

## 📝 Formato dei Documenti

### Per migliori risultati:

**PDF:**
- Testo selezionabile (non immagini scansionate)
- Struttura chiara con titoli e sezioni
- Lingua italiana

**DOCX:**
- Formattazione strutturata con stili
- Titoli e sottotitoli definiti
- Contenuto testuale (evitare troppe immagini)

**TXT:**
- Codifica UTF-8
- Struttura con separatori chiari
- Paragrafi ben organizzati

## 🏋️ Esempi di Contenuto

### Esercizi
```
SQUAT CON BILANCIERE

Muscoli coinvolti: Quadricipiti, glutei, core
Difficoltà: Intermedio

Esecuzione:
1. Posizionare il bilanciere sui trapezi
2. Piedi alla larghezza delle spalle
3. Scendere mantenendo il petto alto
4. Risalire spingendo con i talloni

Note tecniche:
- Mantenere le ginocchia allineate
- Non superare la punta dei piedi
- Respirazione: inspirare in discesa, espirare in salita

Varianti:
- Squat goblet (principianti)
- Front squat (avanzati)
- Squat bulgaro (unilaterale)
```

### Programmazione
```
PERIODIZZAZIONE LINEARE

Settimane 1-4: Adattamento anatomico
- Volume: Alto (12-15 ripetizioni)
- Intensità: Bassa (60-70% 1RM)
- Recupero: 60-90 secondi

Settimane 5-8: Ipertrofia
- Volume: Medio-alto (8-12 ripetizioni)
- Intensità: Media (70-80% 1RM)
- Recupero: 90-120 secondi

Settimane 9-12: Forza
- Volume: Basso (3-6 ripetizioni)
- Intensità: Alta (80-90% 1RM)
- Recupero: 2-5 minuti
```

### Nutrizione
```
FABBISOGNO PROTEICO

Sedentari: 0.8-1.0 g/kg peso corporeo
Fitness generale: 1.2-1.6 g/kg peso corporeo
Ipertrofia: 1.6-2.2 g/kg peso corporeo
Forza/potenza: 1.4-2.0 g/kg peso corporeo

Fonti proteiche complete:
- Carne magra (pollo, tacchino, manzo)
- Pesce (salmone, tonno, merluzzo)
- Uova
- Latticini magri
- Legumi + cereali (per vegetariani)

Timing proteico:
- 20-30g ogni 3-4 ore
- 30-40g entro 2 ore post-workout
```

## ⚠️ Note Importanti

1. **Copyright**: Assicurati di avere i diritti per utilizzare i documenti
2. **Qualità**: Documenti di alta qualità producono risultati migliori
3. **Lingua**: Il sistema è ottimizzato per contenuti in italiano
4. **Dimensioni**: File troppo grandi potrebbero rallentare l'indicizzazione
5. **Aggiornamenti**: Riavvia l'app dopo aver aggiunto nuovi documenti

## 🔍 Verifica Indicizzazione

Dopo l'avvio dell'applicazione, verifica nei log:

```
INFO - 📚 Caricamento documenti da /path/to/documents
INFO - Caricato: exercises.pdf (15 documenti)
INFO - Caricato: programming.pdf (8 documenti)
INFO - ✅ Totale documenti caricati: 23
INFO - 🔍 Creazione indice vettoriale...
INFO - ✅ Indice creato con successo
```

## 🆘 Problemi Comuni

**File non caricato:**
- Verifica l'estensione (.pdf, .docx, .txt)
- Controlla che il file non sia corrotto
- Assicurati che sia leggibile (non protetto da password)

**Scarsa qualità delle risposte:**
- Aggiungi più documenti specifici per l'argomento
- Verifica che il contenuto sia in italiano
- Controlla che i documenti siano ben strutturati

**Errori di memoria:**
- Riduci la dimensione dei file
- Aumenta la RAM disponibile
- Riduci CHUNK_SIZE nelle configurazioni

## 📖 Fonti Consigliate

### Enti Italiani
- **CONI** - Comitato Olimpico Nazionale Italiano
- **FIF** - Federazione Italiana Fitness
- **ACSM** - American College of Sports Medicine (tradotto)
- **NSCA** - National Strength and Conditioning Association (tradotto)

### Pubblicazioni Scientifiche
- Journal of Strength and Conditioning Research
- Medicine & Science in Sports & Exercise
- European Journal of Applied Physiology
- Sports Medicine

### Libri di Riferimento
- "Scienza e Sviluppo della Ipertrofia Muscolare" - Brad Schoenfeld
- "Periodization Training for Sports" - Tudor Bompa
- "Strength Training Anatomy" - Frederic Delavier
- "The New Rules of Lifting" - Lou Schuler

---

**Ricorda**: Più documenti di qualità aggiungi, migliori saranno le schede generate dal chatbot! 🎯
