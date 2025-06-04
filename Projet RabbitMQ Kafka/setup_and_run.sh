#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================="
echo -e "🚀 Initialisation du Projet RabbitMQ - Calcul Distribué 🚀"
echo -e "=====================================================${NC}"
echo ""

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERREUR] $1${NC}"
}

log_step() {
    echo -e "\n${BLUE}--- ÉTAPE : $1 ---${NC}"
}

# 1. Vérifier Python et Pip
log_step "Vérification de Python et Pip"
if ! command -v python3 &> /dev/null
then
    log_error "Python 3 n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi
log_info "Python 3 trouvé : $(python3 --version)"

if ! command -v pip3 &> /dev/null
then
    if ! python3 -m pip --version &> /dev/null
    then
        log_error "Pip3 n'est pas installé. Veuillez l'installer pour continuer."
        log_info "Essayez : sudo apt install python3-pip (Debian/Ubuntu) ou brew install python3 (macOS)"
        exit 1
    else
      PIP_CMD="python3 -m pip"
    fi
else
    PIP_CMD="pip3"
fi
log_info "Pip trouvé : $($PIP_CMD --version)"
echo ""

# 2. Installer les dépendances Python
log_step "Installation des dépendances Python (requirements.txt)"
if [ -f "requirements.txt" ]; then
    if $PIP_CMD install -r requirements.txt; then
        log_info "Dépendances Python installées avec succès."
    else
        log_error "L'installation des dépendances Python a échoué."
        exit 1
    fi
else
    log_error "Le fichier requirements.txt est introuvable. Assurez-vous d'être dans le bon répertoire."
    exit 1
fi
echo ""

# 3. Vérifier Docker
log_step "Vérification de Docker"
if ! command -v docker &> /dev/null
then
    log_error "Docker n'est pas installé. Veuillez l'installer pour continuer."
    log_info "Instructions : https://docs.docker.com/get-docker/"
    exit 1
fi
log_info "Docker trouvé : $(docker --version)"

# Vérifier si Docker daemon est en cours d'exécution
if ! docker info &> /dev/null; then
    log_error "Le démon Docker ne semble pas être en cours d'exécution."
    log_warn "Veuillez démarrer Docker Desktop ou le service Docker et relancer le script."
    exit 1
fi
log_info "Le démon Docker est actif."
echo ""

# 4. Vérifier Docker Compose
log_step "Vérification de Docker Compose"
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    log_info "Docker Compose (v1) trouvé : $(docker-compose --version)"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    log_info "Docker Compose (v2 plugin) trouvé : $(docker compose version)"
else
    log_error "Docker Compose n'est pas installé (ni v1, ni v2)."
    log_info "Instructions : https://docs.docker.com/compose/install/"
    exit 1
fi
echo ""

# 5. Vérifier l'existence du fichier docker-compose.yml
log_step "Vérification du fichier docker-compose.yml"
if [ ! -f "docker-compose.yml" ]; then
    log_error "Le fichier docker-compose.yml est introuvable."
    log_warn "Assurez-vous que le fichier est présent à la racine du projet."
    exit 1
fi
log_info "Fichier docker-compose.yml trouvé."
echo ""

# 6. Lancer le projet avec Docker Compose
log_step "Lancement du projet avec Docker Compose"
log_info "Construction des images et démarrage des conteneurs..."
log_info "Cela peut prendre quelques minutes lors du premier lancement."

if $DOCKER_COMPOSE_CMD up --build -d; then
    log_info "Le système a été démarré avec succès via Docker Compose."
else
    log_error "Le démarrage avec Docker Compose a échoué."
    log_warn "Vérifiez les messages d'erreur ci-dessus."
    log_warn "Vous pouvez essayer de nettoyer les anciens conteneurs/volumes et réessayer :"
    log_warn "  $DOCKER_COMPOSE_CMD down -v"
    exit 1
fi
echo ""

# 7. Afficher les instructions finales
log_step "Instructions finales"
echo -e "${GREEN}🎉 Le projet RabbitMQ - Calcul Distribué est maintenant lancé ! 🎉${NC}"
echo ""
echo -e "   🌐 ${YELLOW}Interface Web :${NC}            http://localhost:5001"
echo -e "   🐰 ${YELLOW}RabbitMQ Management :${NC}   http://localhost:15672"
echo -e "      (Identifiants par défaut pour RabbitMQ via Docker Compose : ${BLUE}admin / admin123${NC})"
echo ""
echo -e "   ${YELLOW}Pour voir les logs des conteneurs :${NC}"
echo -e "      ${BLUE}$DOCKER_COMPOSE_CMD logs -f${NC}"
echo ""
echo -e "   ${YELLOW}Pour arrêter le système :${NC}"
echo -e "      ${BLUE}$DOCKER_COMPOSE_CMD down${NC}"
echo ""
echo -e "   ${YELLOW}Pour arrêter et supprimer les volumes (données RabbitMQ) :${NC}"
echo -e "      ${BLUE}$DOCKER_COMPOSE_CMD down -v${NC}"
echo ""
echo -e "${BLUE}====================================================="
echo -e "✨ Profitez bien du système de calcul distribué ! ✨"
echo -e "=====================================================${NC}"

exit 0 