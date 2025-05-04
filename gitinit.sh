# Inicjalizuj repozytorium Git
git init

# Dodaj wszystkie pliki do poczekalni
git add .

# Stwórz pierwszy commit
git commit -m "Początkowa struktura projektu"

# Dodaj zdalne repozytorium (zastąp URL własnym adresem repozytorium)
git remote add origin https://github.com/twinizer/python.git

# Opcjonalnie sprawdź, czy zdalne repozytorium zostało poprawnie dodane
git remote -v

# Pobierz zmiany ze zdalnego repozytorium i spróbuj je połączyć
git pull origin main --allow-unrelated-histories

# Pobierz informacje ze zdalnego repozytorium bez łączenia
git fetch origin

# Zobacz różnice
git diff origin/main

# Prześlij zmiany do zdalnego repozytorium
git push -u origin main

# merge z opcją pozwalającą na łączenie niepowiązanych historii:
git merge origin/main --allow-unrelated-histories

git status