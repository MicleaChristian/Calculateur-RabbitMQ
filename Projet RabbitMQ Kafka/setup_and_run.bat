@echo off
REM Script "Do It All" pour le projet RabbitMQ - Système de Calcul Distribué (Windows)
REM Ce script installe les dépendances, vérifie les prérequis et lance le projet.

echo =====================================================
echo 🚀 Initialisation du Projet RabbitMQ - Calcul Distribué 🚀
echo =====================================================
echo.

REM Fonction pour afficher les messages colorés (basique)
echo [INFO] Démarrage de l'installation automatique...
echo.

REM 1. Vérifier Python et Pip
echo --- ETAPE : Vérification de Python et Pip ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH.
    echo [INFO] Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)
echo [INFO] Python trouvé
python --version

pip --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERREUR] Pip n'est pas disponible.
        echo [INFO] Veuillez réinstaller Python avec pip inclus.
        pause
        exit /b 1
    ) else (
        set PIP_CMD=python -m pip
    )
) else (
    set PIP_CMD=pip
)
echo [INFO] Pip trouvé
%PIP_CMD% --version
echo.

REM 2. Installer les dépendances Python
echo --- ETAPE : Installation des dépendances Python ---
if not exist "requirements.txt" (
    echo [ERREUR] Le fichier requirements.txt est introuvable.
    echo [INFO] Assurez-vous d'être dans le bon répertoire.
    pause
    exit /b 1
)

echo [INFO] Installation des dépendances Python...
%PIP_CMD% install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] L'installation des dépendances Python a échoué.
    pause
    exit /b 1
)
echo [INFO] Dépendances Python installées avec succès.
echo.

REM 3. Vérifier Docker
echo --- ETAPE : Vérification de Docker ---
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker n'est pas installé ou pas dans le PATH.
    echo [INFO] Veuillez installer Docker Desktop depuis https://docs.docker.com/get-docker/
    pause
    exit /b 1
)
echo [INFO] Docker trouvé
docker --version

REM Vérifier si Docker daemon est en cours d'exécution
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Le démon Docker ne semble pas être en cours d'exécution.
    echo [WARN] Veuillez démarrer Docker Desktop et relancer le script.
    pause
    exit /b 1
)
echo [INFO] Le démon Docker est actif.
echo.

REM 4. Vérifier Docker Compose
echo --- ETAPE : Vérification de Docker Compose ---
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE_CMD=docker-compose
    echo [INFO] Docker Compose (v1) trouvé
    docker-compose --version
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE_CMD=docker compose
        echo [INFO] Docker Compose (v2 plugin) trouvé
        docker compose version
    ) else (
        echo [ERREUR] Docker Compose n'est pas installé (ni v1, ni v2).
        echo [INFO] Instructions : https://docs.docker.com/compose/install/
        pause
        exit /b 1
    )
)
echo.

REM 5. Vérifier l'existence du fichier docker-compose.yml
echo --- ETAPE : Vérification du fichier docker-compose.yml ---
if not exist "docker-compose.yml" (
    echo [ERREUR] Le fichier docker-compose.yml est introuvable.
    echo [WARN] Assurez-vous que le fichier est présent à la racine du projet.
    pause
    exit /b 1
)
echo [INFO] Fichier docker-compose.yml trouvé.
echo.

REM 6. Lancer le projet avec Docker Compose
echo --- ETAPE : Lancement du projet avec Docker Compose ---
echo [INFO] Construction des images et démarrage des conteneurs...
echo [INFO] Cela peut prendre quelques minutes lors du premier lancement.

%DOCKER_COMPOSE_CMD% up --build -d
if %errorlevel% neq 0 (
    echo [ERREUR] Le démarrage avec Docker Compose a échoué.
    echo [WARN] Vérifiez les messages d'erreur ci-dessus.
    echo [WARN] Vous pouvez essayer de nettoyer les anciens conteneurs/volumes et réessayer :
    echo [WARN]   %DOCKER_COMPOSE_CMD% down -v
    pause
    exit /b 1
)
echo [INFO] Le système a été démarré avec succès via Docker Compose.
echo.

REM 7. Afficher les instructions finales
echo --- ETAPE : Instructions finales ---
echo 🎉 Le projet RabbitMQ - Calcul Distribué est maintenant lancé ! 🎉
echo.
echo    🌐 Interface Web :            http://localhost:5001
echo    🐰 RabbitMQ Management :   http://localhost:15672
echo       (Identifiants par défaut : admin / admin123)
echo.
echo    Pour voir les logs des conteneurs :
echo       %DOCKER_COMPOSE_CMD% logs -f
echo.
echo    Pour arrêter le système :
echo       %DOCKER_COMPOSE_CMD% down
echo.
echo    Pour arrêter et supprimer les volumes (données RabbitMQ) :
echo       %DOCKER_COMPOSE_CMD% down -v
echo.
echo =====================================================
echo ✨ Profitez bien du système de calcul distribué ! ✨
echo =====================================================

pause 