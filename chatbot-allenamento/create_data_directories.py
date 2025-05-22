#!/usr/bin/env python3
"""
Script per creare le directory dei dati
"""

import os
from pathlib import Path

# Directory base
base_dir = Path(__file__).parent

# Directory da creare
directories = [
    base_dir / "app" / "data",
    base_dir / "app" / "data" / "chats",
    base_dir / "app" / "data" / "workouts", 
    base_dir / "app" / "data" / "indexes",
]

def create_directories():
    """Crea tutte le directory necessarie"""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Creata directory: {directory}")
        
        # Crea file .gitkeep per mantenere le directory vuote in git
        gitkeep_file = directory / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()
            print(f"📝 Creato .gitkeep in: {directory}")

if __name__ == "__main__":
    print("🗂️  Creazione directory dati...")
    create_directories()
    print("✨ Tutte le directory sono state create con successo!")
