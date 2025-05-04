#!/bin/bash
# Usuń poprzednie pliki
clear
echo "Starting publication process..."
#flatedit


python -m venv venv
source venv/bin/activate


# Upewnij się że mamy najnowsze narzędzia
pip install --upgrade pip build twine

# Sprawdź czy jesteśmy w virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Aktywuj najpierw virtualenv!"
    exit 1
fi


pip install -r requirements.txt

# Uninstall and reinstall to be safe
pip uninstall -y twinizer
pip install -e .

python update/src.py -f twinizer/__init__.py --type patch
python update/src.py -f twinizer/_version.py --type patch
python update/src.py -f pyproject.toml --type patch
# python update/project.sh
python update/changelog.py
#python increment.py
bash update/git.sh
bash update/pypi.sh
