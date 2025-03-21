# Clone le dépôt Git du projet
git clone https://github.com/Sans-Interdit/Beauvoir_DWWM_Project.git

# Se déplacer dans le dossier du backend du projet
cd Beauvoir_DWWM_Project/back

# Créer un fichier .env contenant les clés d'API et de chiffrement (à remplir avec des valeurs réelles)
(
echo API_KEY=""   # Clé API utilisée par l'application (à compléter)
echo HASH_KEY="" # Clé de chiffrement utilisée pour la sécurité des données (à compléter)
) > .env

# Garde la console ouverte après l'exécution du script (Windows)
cmd /k