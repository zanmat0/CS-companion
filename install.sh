#!/bin/bash

echo "Starter installasjon..."

set -e

if ! command -v python &> /dev/null; then
    echo "Python ikke funnet. Installer det først."
    exit 1
fi

echo "Oppretter virtuelt miljø i ./venv ..."
python -m venv venv

source venv/bin/activate

echo "Installerer avhengigheter fra requirements.txt ..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Installasjon fullført!"
echo "Kjør botten med:"
echo "source venv/bin/activate && python main.py"
