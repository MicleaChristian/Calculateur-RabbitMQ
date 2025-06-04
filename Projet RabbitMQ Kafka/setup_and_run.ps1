# Ce script installe les dépendances, vérifie les prérequis et lance le projet.

# Configuration des couleurs
$Green = [System.Console]::ForegroundColor = 'Green'
$Yellow = [System.Console]::ForegroundColor = 'Yellow' 
$Red = [System.Console]::ForegroundColor = 'Red'
$Blue = [System.Console]::ForegroundColor = 'Blue'
$White = [System.Console]::ForegroundColor = 'White'

function Write-ColorOutput($ForegroundColor) {
    $fc = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $Host.UI.RawUI.ForegroundColor = $fc
}

function Log-Info($message) {
    Write-ColorOutput Green "[INFO] $message"
}

function Log-Warn($message) {
    Write-ColorOutput Yellow "[WARN] $message"
}

function Log-Error($message) {
    Write-ColorOutput Red "[ERREUR] $message"
}

function Log-Step($message) {
    Write-ColorOutput Blue "`n--- ÉTAPE : $message ---"
}

# En-tête
Write-ColorOutput Blue "====================================================="
Write-ColorOutput Blue "🚀 Initialisation du Projet RabbitMQ - Calcul Distribué 🚀"
Write-ColorOutput Blue "====================================================="
Write-Output ""

# 1. Vérifier Python et Pip
Log-Step "Vérification de Python et Pip"

try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python non trouvé"
    }
    Log-Info "Python trouvé : $pythonVersion"
} catch {
    Log-Error "Python n'est pas installé ou pas dans le PATH."
    Log-Info "Veuillez installer Python depuis https://python.org"
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

try {
    $pipVersion = pip --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        $pipVersion = python -m pip --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Pip non trouvé"
        }
        $PipCmd = "python -m pip"
    } else {
        $PipCmd = "pip"
    }
    Log-Info "Pip trouvé : $pipVersion"
} catch {
    Log-Error "Pip n'est pas disponible."
    Log-Info "Veuillez réinstaller Python avec pip inclus."
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Output ""

# 2. Installer les dépendances Python
Log-Step "Installation des dépendances Python"

if (!(Test-Path "requirements.txt")) {
    Log-Error "Le fichier requirements.txt est introuvable."
    Log-Info "Assurez-vous d'être dans le bon répertoire."
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Log-Info "Installation des dépendances Python..."
try {
    Invoke-Expression "$PipCmd install -r requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        throw "Installation échouée"
    }
    Log-Info "Dépendances Python installées avec succès."
} catch {
    Log-Error "L'installation des dépendances Python a échoué."
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Output ""

# 3. Vérifier Docker
Log-Step "Vérification de Docker"

try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker non trouvé"
    }
    Log-Info "Docker trouvé : $dockerVersion"
} catch {
    Log-Error "Docker n'est pas installé ou pas dans le PATH."
    Log-Info "Veuillez installer Docker Desktop depuis https://docs.docker.com/get-docker/"
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# Vérifier si Docker daemon est en cours d'exécution
try {
    docker info | Out-Null 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon non actif"
    }
    Log-Info "Le démon Docker est actif."
} catch {
    Log-Error "Le démon Docker ne semble pas être en cours d'exécution."
    Log-Warn "Veuillez démarrer Docker Desktop et relancer le script."
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Output ""

# 4. Vérifier Docker Compose
Log-Step "Vérification de Docker Compose"

try {
    $dockerComposeV1 = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $DockerComposeCmd = "docker-compose"
        Log-Info "Docker Compose (v1) trouvé : $dockerComposeV1"
    } else {
        $dockerComposeV2 = docker compose version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $DockerComposeCmd = "docker compose"
            Log-Info "Docker Compose (v2 plugin) trouvé : $dockerComposeV2"
        } else {
            throw "Docker Compose non trouvé"
        }
    }
} catch {
    Log-Error "Docker Compose n'est pas installé (ni v1, ni v2)."
    Log-Info "Instructions : https://docs.docker.com/compose/install/"
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Output ""

# 5. Vérifier l'existence du fichier docker-compose.yml
Log-Step "Vérification du fichier docker-compose.yml"

if (!(Test-Path "docker-compose.yml")) {
    Log-Error "Le fichier docker-compose.yml est introuvable."
    Log-Warn "Assurez-vous que le fichier est présent à la racine du projet."
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}
Log-Info "Fichier docker-compose.yml trouvé."

Write-Output ""

# 6. Lancer le projet avec Docker Compose
Log-Step "Lancement du projet avec Docker Compose"
Log-Info "Construction des images et démarrage des conteneurs..."
Log-Info "Cela peut prendre quelques minutes lors du premier lancement."

try {
    Invoke-Expression "$DockerComposeCmd up --build -d"
    if ($LASTEXITCODE -ne 0) {
        throw "Démarrage échoué"
    }
    Log-Info "Le système a été démarré avec succès via Docker Compose."
} catch {
    Log-Error "Le démarrage avec Docker Compose a échoué."
    Log-Warn "Vérifiez les messages d'erreur ci-dessus."
    Log-Warn "Vous pouvez essayer de nettoyer les anciens conteneurs/volumes et réessayer :"
    Log-Warn "  $DockerComposeCmd down -v"
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Output ""

# 7. Afficher les instructions finales
Log-Step "Instructions finales"
Write-ColorOutput Green "🎉 Le projet RabbitMQ - Calcul Distribué est maintenant lancé ! 🎉"
Write-Output ""
Write-ColorOutput Yellow "   🌐 Interface Web :            http://localhost:5001"
Write-ColorOutput Yellow "   🐰 RabbitMQ Management :   http://localhost:15672"
Write-Output "      (Identifiants par défaut : admin / admin123)"
Write-Output ""
Write-ColorOutput Yellow "   Pour voir les logs des conteneurs :"
Write-ColorOutput Blue "      $DockerComposeCmd logs -f"
Write-Output ""
Write-ColorOutput Yellow "   Pour arrêter le système :"
Write-ColorOutput Blue "      $DockerComposeCmd down"
Write-Output ""
Write-ColorOutput Yellow "   Pour arrêter et supprimer les volumes (données RabbitMQ) :"
Write-ColorOutput Blue "      $DockerComposeCmd down -v"
Write-Output ""
Write-ColorOutput Blue "====================================================="
Write-ColorOutput Blue "✨ Profitez bien du système de calcul distribué ! ✨"
Write-ColorOutput Blue "====================================================="

Read-Host "Appuyez sur Entrée pour continuer" 