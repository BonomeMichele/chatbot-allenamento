#!/usr/bin/env python3
"""
Script per avviare l'applicazione chatbot allenamento
"""

import os
import sys
import uvicorn
from pathlib import Path

# Aggiungi il percorso dell'app al Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

if __name__ == "__main__":
    # Controlla se il file .env esiste
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("⚠️  File .env non trovato!")
        print("📋 Copia .env.example in .env e configura le tue API keys")
        sys.exit(1)
    
    print("🚀 Avvio del Chatbot Allenamento...")
    print("📊 Dashboard disponibile su: http://localhost:8000")
    print("🔄 Riavvio automatico attivo (--reload)")
    print("⏹️  Premi Ctrl+C per fermare il server")
    
    # Avvia il server con ricaricamento automatico
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
