/**
 * Script per visualizzazione avanzata delle schede di allenamento
 */

class WorkoutDisplayManager {
    constructor() {
        this.initializeWorkoutFeatures();
    }
    
    initializeWorkoutFeatures() {
        // Gestisce le animazioni delle schede
        this.setupWorkoutAnimations();
        
        // Gestisce l'interattività delle tabelle
        this.setupTableInteractions();
        
        // Gestisce i tooltip per gli esercizi
        this.setupExerciseTooltips();
        
        // Gestisce la stampa delle schede
        this.setupPrintFeatures();
    }
    
    setupWorkoutAnimations() {
        // Osserva quando vengono aggiunte nuove schede
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList?.contains('workout-card')) {
                        this.animateWorkoutCard(node);
                    }
                });
            });
        });
        
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            observer.observe(chatContainer, { childList: true, subtree: true });
        }
    }
    
    animateWorkoutCard(workoutCard) {
        // Anima l'apparizione della scheda
        workoutCard.style.opacity = '0';
        workoutCard.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            workoutCard.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            workoutCard.style.opacity = '1';
            workoutCard.style.transform = 'translateY(0)';
        }, 100);
        
        // Anima gli elementi interni con delay
        const sections = workoutCard.querySelectorAll('.workout-day, .profile-section, .nutrition-section, .progression-section');
        sections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                section.style.transition = 'all 0.4s ease-out';
                section.style.opacity = '1';
                section.style.transform = 'translateX(0)';
            }, 200 + (index * 100));
        });
        
        // Anima le tabelle esercizi
        const tables = workoutCard.querySelectorAll('.exercise-table');
        tables.forEach((table, index) => {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach((row, rowIndex) => {
                row.style.opacity = '0';
                row.style.transform = 'translateY(10px)';
                
                setTimeout(() => {
                    row.style.transition = 'all 0.3s ease-out';
                    row.style.opacity = '1';
                    row.style.transform = 'translateY(0)';
                }, 600 + (index * 200) + (rowIndex * 50));
            });
        });
    }
    
    setupTableInteractions() {
        // Aggiungi hover effects e interazioni alle tabelle
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.exercise-table tbody tr')) {
                const row = e.target.closest('tr');
                this.highlightExerciseRow(row);
            }
        });
        
        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.exercise-table tbody tr')) {
                const row = e.target.closest('tr');
                this.unhighlightExerciseRow(row);
            }
        });
        
        // Click per espandere dettagli esercizio
        document.addEventListener('click', (e) => {
            if (e.target.closest('.exercise-table tbody tr')) {
                const row = e.target.closest('tr');
                this.toggleExerciseDetails(row);
            }
        });
    }
    
    highlightExerciseRow(row) {
        row.style.transform = 'scale(1.02)';
        row.style.boxShadow = '0 4px 20px rgba(251, 191, 36, 0.3)';
        row.style.zIndex = '10';
        row.style.position = 'relative';
    }
    
    unhighlightExerciseRow(row) {
        row.style.transform = 'scale(1)';
        row.style.boxShadow = 'none';
        row.style.zIndex = 'auto';
    }
    
    toggleExerciseDetails(row) {
        const exerciseName = row.querySelector('strong')?.textContent;
        if (!exerciseName) return;
        
        // Verifica se i dettagli sono già visibili
        let detailsRow = row.nextElementSibling;
        if (detailsRow && detailsRow.classList.contains('exercise-details')) {
            // Chiudi i dettagli
            detailsRow.style.maxHeight = '0';
            detailsRow.style.opacity = '0';
            setTimeout(() => detailsRow.remove(), 300);
            return;
        }
        
        // Crea e mostra i dettagli
        this.showExerciseDetails(row, exerciseName);
    }
    
    showExerciseDetails(row, exerciseName) {
        const detailsRow = document.createElement('tr');
        detailsRow.classList.add('exercise-details');
        detailsRow.innerHTML = `
            <td colspan="100%" class="exercise-details-content">
                <div class="exercise-info">
                    <h4>💡 Dettagli per ${exerciseName}</h4>
                    <div class="exercise-tips">
                        <div class="tip-section">
                            <strong>🎯 Muscoli target:</strong>
                            <p>Informazioni sui muscoli principali coinvolti nell'esercizio.</p>
                        </div>
                        <div class="tip-section">
                            <strong>⚠️ Attenzione:</strong>
                            <p>Mantieni sempre la forma corretta e non sacrificare la tecnica per il peso.</p>
                        </div>
                        <div class="tip-section">
                            <strong>📈 Progressione:</strong>
                            <p>Aumenta gradualmente il peso o le ripetizioni quando l'esercizio diventa facile.</p>
                        </div>
                    </div>
                </div>
            </td>
        `;
        
        // Styling per i dettagli
        const content = detailsRow.querySelector('.exercise-details-content');
        content.style.cssText = `
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.3);
            border-radius: 8px;
            padding: 0;
            max-height: 0;
            overflow: hidden;
            transition: all 0.3s ease-out;
        `;
        
        const exerciseInfo = detailsRow.querySelector('.exercise-info');
        exerciseInfo.style.cssText = `
            padding: 15px;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease-out 0.1s;
        `;
        
        // Inserisci dopo la riga corrente
        row.parentNode.insertBefore(detailsRow, row.nextSibling);
        
        // Anima l'apertura
        setTimeout(() => {
            content.style.maxHeight = '200px';
            content.style.padding = '0';
            exerciseInfo.style.opacity = '1';
            exerciseInfo.style.transform = 'translateY(0)';
        }, 10);
    }
    
    setupExerciseTooltips() {
        // Crea tooltip per informazioni rapide
        this.createTooltipElement();
        
        document.addEventListener('mouseover', (e) => {
            const exerciseCell = e.target.closest('.exercise-table td strong');
            if (exerciseCell) {
                this.showTooltip(e, exerciseCell.textContent);
            }
        });
        
        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.exercise-table td strong')) {
                this.hideTooltip();
            }
        });
        
        document.addEventListener('mousemove', (e) => {
            if (this.tooltip && this.tooltip.style.display === 'block') {
                this.updateTooltipPosition(e);
            }
        });
    }
    
    createTooltipElement() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'exercise-tooltip';
        this.tooltip.style.cssText = `
            position: fixed;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            max-width: 200px;
            z-index: 1000;
            display: none;
            pointer-events: none;
            transition: opacity 0.2s ease;
        `;
        document.body.appendChild(this.tooltip);
    }
    
    showTooltip(event, exerciseName) {
        const tips = this.getExerciseTip(exerciseName);
        this.tooltip.innerHTML = `<strong>${exerciseName}</strong><br>${tips}`;
        this.tooltip.style.display = 'block';
        this.updateTooltipPosition(event);
        
        setTimeout(() => {
            this.tooltip.style.opacity = '1';
        }, 10);
    }
    
    hideTooltip() {
        this.tooltip.style.opacity = '0';
        setTimeout(() => {
            this.tooltip.style.display = 'none';
        }, 200);
    }
    
    updateTooltipPosition(event) {
        const x = event.clientX + 10;
        const y = event.clientY - 10;
        
        this.tooltip.style.left = x + 'px';
        this.tooltip.style.top = y + 'px';
    }
    
    getExerciseTip(exerciseName) {
        const tips = {
            'squat': 'Mantieni i piedi alla larghezza delle spalle, scendi fino a 90°',
            'panca': 'Contrai i pettorali, mantieni i gomiti a 45°',
            'stacco': 'Schiena dritta, bilanciere vicino alle gambe',
            'rematore': 'Spremere le scapole, gomiti vicino al corpo',
            'push-up': 'Corpo allineato, scendi fino a sfiorare il suolo',
            'plank': 'Mantieni il corpo dritto, non alzare i glutei'
        };
        
        const exerciseLower = exerciseName.toLowerCase();
        for (const [key, tip] of Object.entries(tips)) {
            if (exerciseLower.includes(key)) {
                return tip;
            }
        }
        
        return 'Clicca sulla riga per maggiori dettagli';
    }
    
    setupPrintFeatures() {
        // Aggiungi pulsante stampa alle schede
        document.addEventListener('click', (e) => {
            if (e.target.closest('.workout-card')) {
                this.addPrintButton(e.target.closest('.workout-card'));
            }
        });
    }
    
    addPrintButton(workoutCard) {
        // Evita di aggiungere più pulsanti
        if (workoutCard.querySelector('.print-workout-btn')) return;
        
        const printBtn = document.createElement('button');
        printBtn.className = 'print-workout-btn';
        printBtn.innerHTML = '<i class="fa-solid fa-print"></i> Stampa Scheda';
        printBtn.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        `;
        
        printBtn.addEventListener('mouseenter', () => {
            printBtn.style.background = 'rgba(255, 255, 255, 0.3)';
            printBtn.style.transform = 'translateY(-1px)';
        });
        
        printBtn.addEventListener('mouseleave', () => {
            printBtn.style.background = 'rgba(255, 255, 255, 0.2)';
            printBtn.style.transform = 'translateY(0)';
        });
        
        printBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.printWorkout(workoutCard);
        });
        
        workoutCard.style.position = 'relative';
        workoutCard.appendChild(printBtn);
    }
    
    printWorkout(workoutCard) {
        // Crea una finestra di stampa con la scheda
        const printWindow = window.open('', '_blank');
        const workoutHtml = workoutCard.outerHTML;
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Scheda di Allenamento</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    body {
                        font-family: 'Inter', sans-serif;
                        margin: 20px;
                        background: white;
                        color: #333;
                    }
                    .workout-card {
                        background: white !important;
                        color: #333 !important;
                        box-shadow: none !important;
                        border: 2px solid #10b981;
                        max-width: none;
                    }
                    .workout-title {
                        color: #10b981 !important;
                        text-shadow: none !important;
                    }
                    .workout-day h3 {
                        color: #059669 !important;
                        border-bottom-color: #10b981 !important;
                    }
                    .exercise-table {
                        background: white !important;
                    }
                    .exercise-table th {
                        background: #f0fdf4 !important;
                        color: #166534 !important;
                    }
                    .exercise-table td {
                        border-bottom: 1px solid #d1fae5;
                    }
                    .print-workout-btn {
                        display: none !important;
                    }
                    @media print {
                        body { margin: 0; }
                        .workout-card { border: none; }
                    }
                </style>
            </head>
            <body>
                ${workoutHtml}
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    }
    
    // Funzione per esportare la scheda come testo
    exportWorkoutAsText(workoutCard) {
        const title = workoutCard.querySelector('.workout-title')?.textContent || 'Scheda Allenamento';
        let textContent = `${title}\n${'='.repeat(50)}\n\n`;
        
        // Profilo utente
        const profileSection = workoutCard.querySelector('.profile-section');
        if (profileSection) {
            textContent += 'PROFILO UTENTE:\n';
            const profileItems = profileSection.querySelectorAll('li');
            profileItems.forEach(item => {
                textContent += `• ${item.textContent}\n`;
            });
            textContent += '\n';
        }
        
        // Giorni di allenamento
        const workoutDays = workoutCard.querySelectorAll('.workout-day');
        workoutDays.forEach(day => {
            const dayTitle = day.querySelector('h3')?.textContent || '';
            textContent += `${dayTitle}\n${'-'.repeat(30)}\n`;
            
            // Esercizi
            const table = day.querySelector('.exercise-table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 4) {
                        const name = cells[0].textContent.trim();
                        const sets = cells[1].textContent.trim();
                        const reps = cells[2].textContent.trim();
                        const rest = cells[3].textContent.trim();
                        textContent += `${name} - ${sets} serie x ${reps} rep (${rest})\n`;
                    }
                });
            }
            textContent += '\n';
        });
        
        // Crea e scarica il file
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title.replace(/[^a-z0-9]/gi, '_')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Inizializza il manager quando il DOM è caricato
document.addEventListener('DOMContentLoaded', () => {
    window.workoutDisplayManager = new WorkoutDisplayManager();
});

// Funzioni utility globali per l'interazione con le schede
window.printWorkout = function(workoutCard) {
    if (window.workoutDisplayManager) {
        window.workoutDisplayManager.printWorkout(workoutCard);
    }
};

window.exportWorkout = function(workoutCard) {
    if (window.workoutDisplayManager) {
        window.workoutDisplayManager.exportWorkoutAsText(workoutCard);
    }
};
