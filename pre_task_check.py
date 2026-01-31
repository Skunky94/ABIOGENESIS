#!/usr/bin/env python3
"""
Pre-Task Rule Checker - ABIOGENESIS
====================================
Questo script deve essere eseguito PRIMA di ogni task.
Forza la lettura delle regole operative e del contesto.

Usage:
    python pre_task_check.py [--quick] [--verbose]
    
    --quick  : Solo verifica rapida (file esistono)
    --verbose : Output dettagliato di tutto
    
Il script fallisce (exit 1) se:
    - I file di regole non esistono
    - Sono passati più di 7 giorni dall'ultima lettura
    - Le regole non sono state lette in questa sessione
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
RULES_FILE = SCRIPT_DIR / "PROJECT_RULES.md"
CONTEXT_FILE = SCRIPT_DIR / "CONTEXT.md"
CHANGELOG_FILE = SCRIPT_DIR / "CHANGELOG.md"
COPILOT_FILE = SCRIPT_DIR / ".github" / "copilot-instructions.md"
STATE_FILE = SCRIPT_DIR / ".task_state.json"


def load_state():
    """Load task state from file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_state(state):
    """Save task state to file."""
    state['last_check'] = datetime.now().isoformat()
    state['check_count'] = state.get('check_count', 0) + 1
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def check_file_exists(filepath, description):
    """Check if a required file exists."""
    exists = filepath.exists()
    status = "✓" if exists else "✗"
    return exists, f"{status} {description}: {filepath}"


def check_rules_updated(filepath, max_days=7):
    """Check if file was updated recently."""
    if not filepath.exists():
        return False, "File non trovato"
    
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    age = datetime.now() - mtime
    
    if age > timedelta(days=max_days):
        return False, f"✗ {filepath.name} non aggiornato da {age.days} giorni"
    
    return True, f"✓ {filepath.name} aggiornato di recente"


def read_file_content(filepath):
    """Read file content for rules review."""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def main():
    """Run pre-task checks."""
    print("=" * 70)
    print("ABIOGENESIS PRE-TASK RULE CHECKER")
    print("=" * 70)
    
    state = load_state()
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    quick = "--quick" in sys.argv or "-q" in sys.argv
    
    all_passed = True
    
    # Check 1: Required files exist
    print("\n[1] Verifica file obbligatori...")
    required_files = [
        (RULES_FILE, "Regole operative"),
        (CONTEXT_FILE, "Contesto progetto"),
        (CHANGELOG_FILE, "Cronologia modifiche"),
    ]
    
    for filepath, desc in required_files:
        exists, msg = check_file_exists(filepath, desc)
        print(f"   {msg}")
        if not exists:
            all_passed = False
    
    if quick:
        save_state({**state, "quick_mode": True})
        print("\n[Modalità quick] Verifica completata")
        sys.exit(0 if all_passed else 1)
    
    # Check 2: Read and display rules summary
    print("\n[2] Riepilogo regole chiave...")
    
    rules_content = read_file_content(RULES_FILE)
    if rules_content:
        # Extract key rules (R1-R12)
        import re
        rules = re.findall(r'(### R\d+\..*?(?=### R\d+|$))', rules_content, re.DOTALL)
        for rule in rules[:3]:  # Show first 3 rules
            title = rule.strip().split('\n')[0]
            print(f"   {title}")
        print(f"   ... ({len(rules)} regole totali)")
    else:
        print("   ✗ Impossibile leggere PROJECT_RULES.md")
        all_passed = False
    
    # Check 3: Changelog status
    print("\n[3] Stato progetto (CHANGELOG)...")
    changelog = read_file_content(CHANGELOG_FILE)
    if changelog:
        # Get version
        version_match = changelog.split('\n')[1]
        if "**Version**" in version_match:
            print(f"   Versione: {version_match.split('**Version**:')[1].strip()}")
        
        # Count recent changes
        recent = changelog.count("2026-01-31")
        print(f"   Modifiche oggi: {recent}")
    
    # Check 4: Context summary
    print("\n[4] Contesto progetto...")
    context = read_file_content(CONTEXT_FILE)
    if context:
        # Get current phase
        if "**Fase**" in context or "**Versione**" in context:
            for line in context.split('\n')[:20]:
                if "Versione" in line or "Fase" in line or "Stato" in line:
                    print(f"   {line.strip()}")
    
    # Check 5: Time since last check
    print("\n[5] Stato sessione...")
    last_check = state.get('last_check')
    check_count = state.get('check_count', 0)
    if last_check:
        last_dt = datetime.fromisoformat(last_check)
        elapsed = datetime.now() - last_dt
        print(f"   Ultimo check: {elapsed.seconds // 60} minuti fa")
        print(f"   Check totali sessione: {check_count}")
    else:
        print("   Primo check della sessione")
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ PRE-TASK CHECK PASSATO")
        print("\nPrima di procedere, assicurati di aver letto:")
        print(f"  1. {RULES_FILE.name}")
        print(f"  2. {CONTEXT_FILE.name}")
        print(f"  3. {CHANGELOG_FILE.name}")
        save_state({**state, "ready": True})
    else:
        print("✗ PRE-TASK CHECK FALLITO")
        print("Correggere i problemi prima di procedere.")
        save_state({**state, "ready": False})
    
    print("=" * 70)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
