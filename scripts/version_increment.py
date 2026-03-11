#!/usr/bin/env python3

import subprocess
import re
import sys
import requests

# Configuration initiale
INITIAL_VERSION = "0.0.1"

# Configuration GitHub
GITHUB_REPO_URL = "https://api.github.com/repos/Nehwon/audiobook-master"
GITHUB_TOKEN = "ghp_yourtoken"

# Fonction pour obtenir le nombre de commits depuis GitHub

def get_commit_count():
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(f"{GITHUB_REPO_URL}/commits", headers=headers)
        response.raise_for_status()
        commits = response.json()
        return len(commits)
    except requests.RequestException as e:
        print(f"Erreur lors de l'obtention du nombre de commits depuis GitHub : {e}", file=sys.stderr)
        sys.exit(1)
    
# Fonction pour obtenir la version actuelle

def get_current_version():
    try:
        with open("VERSION_BASE", "r") as f:
            version = f.read().strip()
        return version
    except FileNotFoundError:
        return INITIAL_VERSION

# Fonction pour incrémenter la version

def increment_version(current_version, commit_count):
    # Vérifier le format de la version
    if len(current_version.split(".")) != 3:
        current_version = INITIAL_VERSION
    
    # Découper la version en parties
    parts = current_version.split(".")
    major, minor, fix = map(int, parts)
    
    # Logique d'incrémentation
    if commit_count % 100 == 0:
        # Incrémenter le numéro de major (sur demande de l'utilisateur)
        print("Veuillez confirmer l'incrémentation du numéro de major (y/n): ", end="")
        if input().lower() == "y":
            major += 1
            minor = 0
            fix = 0
        else:
            minor += 1
            fix = 0
    else:
        fix += 1
    
    return f"{major}.{minor}.{fix}"

# Fonction pour mettre à jour la version

def update_version(new_version):
    try:
        with open("VERSION_BASE", "w") as f:
            f.write(new_version)
        print(f"Version mise à jour : {new_version}")
    except IOError as e:
        print(f"Erreur lors de la mise à jour de la version : {e}", file=sys.stderr)
        sys.exit(1)

# Fonction principale

def main():
    commit_count = get_commit_count()
    current_version = get_current_version()
    new_version = increment_version(current_version, commit_count)
    update_version(new_version)

if __name__ == "__main__":
    main()
