## Instrukcje deweloperskie 

**Zalecany Python:** Używaj Python 3.11 do pracy deweloperskiej i uruchamiania lokalnego. Plik `server/requirements.txt` zawiera wersje (m.in. `SQLAlchemy==2.0.25`), które mogą być niezgodne z Pythonem 3.14.

- **Wymagania projektu:** znajdziesz w `server/requirements.txt`.

**Utworzenie i użycie wirtualnego środowiska (PowerShell)**:

```powershell
# przejdź do katalogu serwera
cd .\server

# jeśli masz zainstalowany Python 3.11 jako konkretny egzemplarz:
& C:/Users/Fisher/AppData/Local/Programs/Python/Python311/python.exe -m venv .venv

# alternatywnie, gdy korzystasz z py launcher:
py -3.11 -m venv .venv

# zezwól na uruchamianie skryptów w tej sesji (jeśli potrzeba)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# aktywuj środowisko
.\.venv\Scripts\Activate.ps1

# zaktualizuj pip i zainstaluj zależności
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Uruchamianie serwera Flask (opcje)**:

- Preferowane (Flask CLI) — uruchom z katalogu `server` z aktywowanym venv:

```powershell
flask run --host=0.0.0.0

# lub jawnie ustaw fabrykę aplikacji
$env:FLASK_APP = "main:create_app"
flask run --host=0.0.0.0
```

- Alternatywnie uruchom bezpośrednio:

```powershell
python main.py
```

**Uwagi i rozwiązywanie problemów**:

- Jeżeli pojawi się błąd "Failed to find Flask application or factory in module 'app'", upewnij się, że uruchamiasz polecenie z katalogu `server` (aby `main.py` był importowalny), albo ustaw `FLASK_APP` na `main:create_app` jak wyżej.
- Jeśli `pip install -r requirements.txt` zakończy się błędem przy kompilacji natywnych modułów (np. biblioteki face recognition), skomentuj opcjonalne pozycje w `server/requirements.txt` i uruchom instalację ponownie.
- Aby sprawdzić zainstalowane wersje wewnątrz venv:

```powershell
python -c "import sqlalchemy, flask_sqlalchemy; print('SQLAlchemy', sqlalchemy.__version__); print('Flask_SQLAlchemy', flask_sqlalchemy.__version__)"
```

