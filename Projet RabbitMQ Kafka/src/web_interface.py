#!/usr/bin/env python3
"""
Interface web pour le système de calcul distribué
Usage: python web_interface.py
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, Response
from flask_cors import CORS
import pika

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rabbitmq_config import *
from utils.message_utils import *

app = Flask(__name__)
CORS(app)

# Variables globales pour les statistiques
stats = {
    'sent_tasks': 0,
    'received_results': 0,
    'operations': {'add': 0, 'sub': 0, 'mul': 0, 'div': 0},
    'recent_results': [],
    'web_results': [],  # Résultats des tâches web uniquement
    'auto_results': [], # Résultats des tâches automatiques uniquement
    'queue_status': {},
    'last_update': datetime.now().isoformat()
}

# Template HTML principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧮 Système de Calcul Distribué - RabbitMQ</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 10px;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #e17055;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .results-container {
            max-height: 400px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background: #f8f9fa;
        }
        
        .result-item {
            padding: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .result-add { border-color: #00b894; }
        .result-sub { border-color: #74b9ff; }
        .result-mul { border-color: #a29bfe; }
        .result-div { border-color: #fd79a8; }
        
        .queue-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        
        .status-online { border-color: #00b894; }
        .status-busy { border-color: #fdcb6e; }
        .status-offline { border-color: #e17055; }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .hidden {
            display: none;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧮 Système de Calcul Distribué</h1>
            <p>Interface Web pour RabbitMQ</p>
        </div>
        
        <div class="grid">
            <!-- Formulaire d'envoi de tâches -->
            <div class="card">
                <h2>📤 Envoyer une Tâche</h2>
                <div id="taskAlert" class="alert hidden"></div>
                <form id="taskForm">
                    <div class="form-group">
                        <label for="n1">Premier nombre (n1):</label>
                        <input type="number" id="n1" step="any" value="10" required>
                    </div>
                    <div class="form-group">
                        <label for="operation">Opération:</label>
                        <select id="operation" required>
                            <option value="add">Addition (+)</option>
                            <option value="sub">Soustraction (-)</option>
                            <option value="mul">Multiplication (×)</option>
                            <option value="div">Division (÷)</option>
                            <option value="all">Toutes les opérations</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="n2">Deuxième nombre (n2):</label>
                        <input type="number" id="n2" step="any" value="5" required>
                    </div>
                    <button type="submit" class="btn">
                        <span id="submitText">Envoyer</span>
                        <span id="submitLoading" class="loading hidden"></span>
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="generateRandom()">
                        🎲 Aléatoire
                    </button>
                </form>
            </div>
            
            <!-- Statistiques -->
            <div class="card">
                <h2>📊 Statistiques</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="statSent">0</div>
                        <div class="stat-label">Tâches envoyées</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statReceived">0</div>
                        <div class="stat-label">Résultats reçus</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statAdd">0</div>
                        <div class="stat-label">Additions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statSub">0</div>
                        <div class="stat-label">Soustractions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statMul">0</div>
                        <div class="stat-label">Multiplications</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="statDiv">0</div>
                        <div class="stat-label">Divisions</div>
                    </div>
                </div>
                <button class="btn btn-secondary" onclick="refreshStats()">🔄 Actualiser</button>
                <button class="btn btn-danger" onclick="clearStats()">🗑️ Effacer</button>
            </div>
        </div>
        
        <!-- État des queues -->
        <div class="card">
            <h2>📋 État des Queues</h2>
            <div id="queueStatus">
                <div class="loading"></div> Chargement...
            </div>
            <button class="btn btn-secondary" onclick="refreshQueues()">🔄 Actualiser les Queues</button>
        </div>
        
        <!-- Résultats récents -->
        <div class="card">
            <h2>📥 Résultats des Calculs</h2>
            
            <!-- Filtres -->
            <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center;">
                <label style="margin: 0; font-weight: normal;">Affichage :</label>
                <button class="btn btn-secondary" onclick="showResults('all')" id="btnAll">
                    🔄 Tous
                </button>
                <button class="btn btn-success" onclick="showResults('web')" id="btnWeb">
                    👤 Mes tâches
                </button>
                <button class="btn" onclick="showResults('auto')" id="btnAuto" style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);">
                    🤖 Automatiques
                </button>
            </div>
            
            <!-- Section pour les résultats de l'utilisateur -->
            <div id="webResultsSection" style="display: none;">
                <h3 style="color: #00b894; margin-bottom: 15px;">👤 Vos Résultats</h3>
                <div class="results-container" id="webResultsContainer">
                    <p>Aucun résultat de vos tâches pour le moment...</p>
                </div>
            </div>
            
            <!-- Section pour les résultats automatiques -->
            <div id="autoResultsSection" style="display: none;">
                <h3 style="color: #6c5ce7; margin-bottom: 15px;">🤖 Résultats Automatiques</h3>
                <div class="results-container" id="autoResultsContainer">
                    <p>Aucun résultat automatique pour le moment...</p>
                </div>
            </div>
            
            <!-- Section pour tous les résultats (vue par défaut) -->
            <div id="allResultsSection">
                <div class="results-container" id="resultsContainer">
                    <p>Aucun résultat pour le moment...</p>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <button class="btn btn-secondary" onclick="refreshCurrentResults()">🔄 Actualiser</button>
                <button class="btn" onclick="toggleAutoRefresh()">
                    <span id="autoRefreshText">▶️ Activer Auto-refresh</span>
                    <span id="autoRefreshIndicator" style="display: none; color: #00b894; margin-left: 10px;">🟢 ACTIF</span>
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval = null;
        let autoRefreshActive = false;
        let currentResultsView = 'all'; // 'all', 'web', 'auto'
        
        // Wait for DOM to be fully loaded
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM fully loaded and ready');
            
            // Test basic functionality
            const taskForm = document.getElementById('taskForm');
            console.log('Task form found:', taskForm);
            
            if (taskForm) {
                // Add form submit event listener
                taskForm.addEventListener('submit', handleFormSubmit);
                console.log('Form submit listener added');
            } else {
                console.error('Task form not found!');
            }
            
            // Load initial data
            refreshStats();
            refreshQueues();
            refreshCurrentResults();
        });
        
        // Show/hide result sections based on filter
        function showResults(type) {
            console.log('Switching to results view:', type);
            currentResultsView = type;
            
            // Hide all sections
            document.getElementById('allResultsSection').style.display = 'none';
            document.getElementById('webResultsSection').style.display = 'none';
            document.getElementById('autoResultsSection').style.display = 'none';
            
            // Reset button styles
            const buttons = ['btnAll', 'btnWeb', 'btnAuto'];
            buttons.forEach(id => {
                const btn = document.getElementById(id);
                btn.style.opacity = '0.7';
                btn.style.transform = 'none';
            });
            
            // Show selected section and highlight button
            if (type === 'all') {
                document.getElementById('allResultsSection').style.display = 'block';
                document.getElementById('btnAll').style.opacity = '1';
                document.getElementById('btnAll').style.transform = 'translateY(-2px)';
            } else if (type === 'web') {
                document.getElementById('webResultsSection').style.display = 'block';
                document.getElementById('btnWeb').style.opacity = '1';
                document.getElementById('btnWeb').style.transform = 'translateY(-2px)';
            } else if (type === 'auto') {
                document.getElementById('autoResultsSection').style.display = 'block';
                document.getElementById('btnAuto').style.opacity = '1';
                document.getElementById('btnAuto').style.transform = 'translateY(-2px)';
            }
            
            // Refresh the current view
            refreshCurrentResults();
        }
        
        // Refresh results based on current view
        function refreshCurrentResults() {
            if (currentResultsView === 'all') {
                refreshResults();
            } else if (currentResultsView === 'web') {
                refreshWebResults();
            } else if (currentResultsView === 'auto') {
                refreshAutoResults();
            }
        }
        
        // Handle form submission
        async function handleFormSubmit(e) {
            console.log('=== FORM SUBMIT TRIGGERED ===');
            e.preventDefault();
            
            try {
                const submitBtn = document.querySelector('button[type="submit"]');
                const submitText = document.getElementById('submitText');
                const submitLoading = document.getElementById('submitLoading');
                
                console.log('Elements found:', {submitBtn, submitText, submitLoading});
                
                // Show loading state
                if (submitText && submitLoading) {
                    submitText.style.display = 'none';
                    submitLoading.style.display = 'inline-block';
                }
                if (submitBtn) {
                    submitBtn.disabled = true;
                }
                
                // Get form data
                const n1 = parseFloat(document.getElementById('n1').value);
                const n2 = parseFloat(document.getElementById('n2').value);
                const operation = document.getElementById('operation').value;
                
                const data = { n1, n2, operation };
                console.log('Sending data:', data);
                
                // Send request
                const response = await fetch('/api/send_task', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                console.log('Response status:', response.status);
                const result = await response.json();
                console.log('Response data:', result);
                
                // Handle response
                if (result.success) {
                    showAlert('taskAlert', 'Tâche envoyée avec succès! ✅', 'success');
                    setTimeout(() => {
                        refreshStats();
                        // Switch to web results view to show user's tasks
                        if (currentResultsView === 'all') {
                            showResults('web');
                        } else {
                            refreshCurrentResults();
                        }
                    }, 500); // Refresh stats after a short delay
                } else {
                    showAlert('taskAlert', 'Erreur: ' + (result.error || 'Erreur inconnue'), 'error');
                }
                
            } catch (error) {
                console.error('Error in form submit:', error);
                showAlert('taskAlert', 'Erreur de connexion: ' + error.message, 'error');
            }
            
            // Always restore button state
            const submitBtn = document.querySelector('button[type="submit"]');
            const submitText = document.getElementById('submitText');
            const submitLoading = document.getElementById('submitLoading');
            
            if (submitText && submitLoading) {
                submitText.style.display = 'inline';
                submitLoading.style.display = 'none';
            }
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        }
        
        // Generate random values
        function generateRandom() {
            console.log('Generating random values...');
            try {
                document.getElementById('n1').value = Math.round(Math.random() * 100 * 100) / 100;
                document.getElementById('n2').value = Math.round(Math.random() * 100 * 100) / 100;
                
                const operations = ['add', 'sub', 'mul', 'div', 'all'];
                document.getElementById('operation').value = operations[Math.floor(Math.random() * operations.length)];
                
                console.log('Random values generated successfully');
            } catch (error) {
                console.error('Error generating random values:', error);
            }
        }
        
        // Show alert message
        function showAlert(elementId, message, type) {
            try {
                const alert = document.getElementById(elementId);
                if (alert) {
                    alert.textContent = message;
                    alert.className = `alert alert-${type}`;
                    alert.style.display = 'block';
                    
                    setTimeout(() => {
                        alert.style.display = 'none';
                    }, 5000);
                }
            } catch (error) {
                console.error('Error showing alert:', error);
            }
        }
        
        // Refresh statistics
        async function refreshStats() {
            try {
                console.log('Refreshing stats...');
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('statSent').textContent = stats.sent_tasks || 0;
                document.getElementById('statReceived').textContent = stats.received_results || 0;
                document.getElementById('statAdd').textContent = stats.operations?.add || 0;
                document.getElementById('statSub').textContent = stats.operations?.sub || 0;
                document.getElementById('statMul').textContent = stats.operations?.mul || 0;
                document.getElementById('statDiv').textContent = stats.operations?.div || 0;
                
                console.log('Stats refreshed successfully');
            } catch (error) {
                console.error('Error refreshing stats:', error);
            }
        }
        
        // Refresh queue status
        async function refreshQueues() {
            try {
                console.log('Refreshing queues...');
                const container = document.getElementById('queueStatus');
                container.innerHTML = '<div class="loading"></div> Chargement...';
                
                const response = await fetch('/api/queue_status');
                const status = await response.json();
                
                let html = '';
                for (const [queue, count] of Object.entries(status)) {
                    const statusClass = count > 0 ? 'status-busy' : 'status-online';
                    html += `
                        <div class="queue-status ${statusClass}">
                            <span><strong>${queue.toUpperCase()}</strong></span>
                            <span>${count} messages</span>
                        </div>
                    `;
                }
                
                container.innerHTML = html || '<p>Aucune queue trouvée</p>';
                console.log('Queues refreshed successfully');
            } catch (error) {
                console.error('Error refreshing queues:', error);
                document.getElementById('queueStatus').innerHTML = '<p style="color: red;">Erreur lors du chargement des queues</p>';
            }
        }
        
        // Refresh results
        async function refreshResults() {
            try {
                console.log('Refreshing all results...');
                const response = await fetch('/api/recent_results');
                const results = await response.json();
                
                displayResults(results, 'resultsContainer', 'Aucun résultat pour le moment...');
                console.log('All results refreshed successfully');
            } catch (error) {
                console.error('Error refreshing results:', error);
            }
        }
        
        // Refresh web results only
        async function refreshWebResults() {
            try {
                console.log('Refreshing web results...');
                const response = await fetch('/api/web_results');
                const results = await response.json();
                
                displayResults(results, 'webResultsContainer', 'Aucun résultat de vos tâches pour le moment...');
                console.log('Web results refreshed successfully');
            } catch (error) {
                console.error('Error refreshing web results:', error);
            }
        }
        
        // Refresh auto results only
        async function refreshAutoResults() {
            try {
                console.log('Refreshing auto results...');
                const response = await fetch('/api/auto_results');
                const results = await response.json();
                
                displayResults(results, 'autoResultsContainer', 'Aucun résultat automatique pour le moment...');
                console.log('Auto results refreshed successfully');
            } catch (error) {
                console.error('Error refreshing auto results:', error);
            }
        }
        
        // Common function to display results in any container
        function displayResults(results, containerId, emptyMessage) {
            const container = document.getElementById(containerId);
            
            if (!results || results.length === 0) {
                container.innerHTML = `<p>${emptyMessage}</p>`;
                return;
            }
            
            let html = '';
            results.slice().reverse().forEach(result => {
                const timestamp = new Date(result.timestamp).toLocaleString();
                const opSymbol = result.op === 'add' ? '+' : result.op === 'sub' ? '-' : result.op === 'mul' ? '×' : '÷';
                const sourceIcon = result.source === 'web' ? '👤' : '🤖';
                const sourceLabel = result.source === 'web' ? 'Vous' : 'Auto';
                
                html += `
                    <div class="result-item result-${result.op}">
                        <div>
                            <strong>${result.n1} ${opSymbol} ${result.n2} = ${result.result}</strong>
                            <span style="float: right; font-size: 0.8em; color: #666;">${sourceIcon} ${sourceLabel}</span>
                        </div>
                        <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                            ${timestamp} | Worker: ${result.worker_id} | Temps: ${result.processing_time?.toFixed(1) || 'N/A'}s
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        // Toggle auto-refresh
        function toggleAutoRefresh() {
            console.log('Toggling auto-refresh...');
            try {
                const btn = document.getElementById('autoRefreshText');
                const indicator = document.getElementById('autoRefreshIndicator');
                
                if (autoRefreshActive) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshActive = false;
                    btn.textContent = '▶️ Activer Auto-refresh';
                    if (indicator) indicator.style.display = 'none';
                } else {
                    autoRefreshInterval = setInterval(() => {
                        refreshStats();
                        refreshCurrentResults(); // Use current view instead of always refreshing all
                        refreshQueues();
                    }, 3000);
                    autoRefreshActive = true;
                    btn.textContent = '⏸️ Désactiver Auto-refresh';
                    if (indicator) indicator.style.display = 'inline';
                }
                console.log('Auto-refresh toggled. Active:', autoRefreshActive);
            } catch (error) {
                console.error('Error toggling auto-refresh:', error);
            }
        }
        
        // Clear statistics
        async function clearStats() {
            try {
                if (confirm('Êtes-vous sûr de vouloir effacer les statistiques ?')) {
                    console.log('Clearing stats...');
                    await fetch('/api/clear_stats', { method: 'POST' });
                    refreshStats();
                    refreshCurrentResults();
                    console.log('Stats cleared successfully');
                }
            } catch (error) {
                console.error('Error clearing stats:', error);
            }
        }
    </script>
</body>
</html>
'''


class RabbitMQWebInterface:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.result_consumer_thread = None
        self.consuming = False
        
    def connect_to_rabbitmq(self):
        """Établit la connexion à RabbitMQ"""
        try:
            connection_params = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            )
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # Déclarer toutes les queues
            for operation, queue_name in TASK_QUEUES.items():
                self.channel.queue_declare(queue=queue_name, durable=True)
            
            self.channel.queue_declare(queue=RESULT_QUEUE, durable=True)
            self.channel.exchange_declare(exchange=ALL_OPERATIONS_EXCHANGE, exchange_type='fanout')
            
            return True
            
        except Exception as e:
            print(f"Erreur de connexion RabbitMQ: {e}")
            return False
    
    def send_task(self, n1, n2, operation):
        """Envoie une tâche de calcul"""
        print(f"🔧 [SEND_TASK] Début envoi tâche: n1={n1}, n2={n2}, operation={operation}")
        
        if not self.connect_to_rabbitmq():
            print(f"❌ [SEND_TASK] Échec connexion RabbitMQ")
            return False
            
        try:
            if operation == 'all':
                print(f"📤 [SEND_TASK] Envoi vers toutes les opérations via exchange")
                for op in ['add', 'sub', 'mul', 'div']:
                    task_message = create_task_message(n1, n2, op, source="web")
                    print(f"📨 [SEND_TASK] Message créé pour {op}: {task_message}")
                    self.channel.basic_publish(
                        exchange=ALL_OPERATIONS_EXCHANGE,
                        routing_key='',
                        body=serialize_message(task_message),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    print(f"✅ [SEND_TASK] Message {op} publié vers exchange {ALL_OPERATIONS_EXCHANGE}")
                stats['sent_tasks'] += 4
                print(f"📊 [SEND_TASK] Stats mises à jour: {stats['sent_tasks']} tâches envoyées")
            else:
                task_message = create_task_message(n1, n2, operation, source="web")
                queue_name = TASK_QUEUES[operation]
                print(f"📨 [SEND_TASK] Message créé pour {operation}: {task_message}")
                print(f"📤 [SEND_TASK] Envoi vers queue: {queue_name}")
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=serialize_message(task_message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(f"✅ [SEND_TASK] Message publié vers queue {queue_name}")
                stats['sent_tasks'] += 1
                print(f"📊 [SEND_TASK] Stats mises à jour: {stats['sent_tasks']} tâches envoyées")
                
            stats['last_update'] = datetime.now().isoformat()
            print(f"🎉 [SEND_TASK] Tâche envoyée avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ [SEND_TASK] Erreur envoi tâche: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print(f"🔌 [SEND_TASK] Connexion fermée")
    
    def get_queue_status(self):
        """Récupère l'état des queues"""
        if not self.connect_to_rabbitmq():
            return {}
            
        try:
            status = {}
            
            # Vérifier les queues de tâches
            for operation, queue_name in TASK_QUEUES.items():
                method = self.channel.queue_declare(queue=queue_name, durable=True, passive=True)
                status[f"task_{operation}"] = method.method.message_count
            
            # Vérifier la queue des résultats
            method = self.channel.queue_declare(queue=RESULT_QUEUE, durable=True, passive=True)
            status["results"] = method.method.message_count
            
            stats['queue_status'] = status
            return status
            
        except Exception as e:
            print(f"Erreur récupération statut queues: {e}")
            return {}
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
    
    def start_result_consumer(self):
        """Démarre le consommateur de résultats en arrière-plan"""
        def consume_results():
            if not self.connect_to_rabbitmq():
                return
                
            def process_result(channel, method, properties, body):
                try:
                    message_str = body.decode('utf-8')
                    result_message = deserialize_message(message_str)
                    
                    # Mettre à jour les statistiques
                    stats['received_results'] += 1
                    stats['operations'][result_message['op']] += 1
                    
                    # Ajouter aux résultats récents (garder seulement les 50 derniers)
                    stats['recent_results'].append(result_message)
                    if len(stats['recent_results']) > 50:
                        stats['recent_results'].pop(0)
                    
                    # Séparer par source (en supposant que les tâches sans source sont automatiques)
                    source = result_message.get('source', 'auto')  # Fallback pour compatibilité
                    if source == 'web':
                        stats['web_results'].append(result_message)
                        if len(stats['web_results']) > 50:
                            stats['web_results'].pop(0)
                    else:
                        stats['auto_results'].append(result_message)
                        if len(stats['auto_results']) > 50:
                            stats['auto_results'].pop(0)
                    
                    stats['last_update'] = datetime.now().isoformat()
                    
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    print(f"Erreur traitement résultat: {e}")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=RESULT_QUEUE,
                on_message_callback=process_result
            )
            
            self.consuming = True
            try:
                self.channel.start_consuming()
            except Exception as e:
                print(f"Erreur consommation: {e}")
            finally:
                self.consuming = False
        
        if not self.consuming:
            self.result_consumer_thread = threading.Thread(target=consume_results, daemon=True)
            self.result_consumer_thread.start()


# Instance globale
rabbitmq_interface = RabbitMQWebInterface()


@app.route('/')
def index():
    """Page principale"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/send_task', methods=['POST'])
def api_send_task():
    """API pour envoyer une tâche"""
    print(f"=== /api/send_task called ===")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        print(f"Request content type: {request.content_type}")
        data = request.get_json()
        print(f"Received JSON data: {data}")
        
        n1 = float(data['n1'])
        n2 = float(data['n2'])
        operation = data['operation']
        
        print(f"Parsed values: n1={n1}, n2={n2}, operation={operation}")
        
        if operation not in ['add', 'sub', 'mul', 'div', 'all']:
            print(f"Invalid operation: {operation}")
            return jsonify({'success': False, 'error': 'Opération non supportée'})
        
        print(f"Calling rabbitmq_interface.send_task...")
        success = rabbitmq_interface.send_task(n1, n2, operation)
        print(f"send_task returned: {success}")
        
        if success:
            print(f"Task sent successfully")
            return jsonify({'success': True})
        else:
            print(f"Task sending failed")
            return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi'})
            
    except Exception as e:
        print(f"Exception in api_send_task: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques"""
    return jsonify(stats)


@app.route('/api/queue_status')
def api_queue_status():
    """API pour récupérer l'état des queues"""
    status = rabbitmq_interface.get_queue_status()
    return jsonify(status)


@app.route('/api/recent_results')
def api_recent_results():
    """API pour récupérer les résultats récents"""
    return jsonify(stats['recent_results'])


@app.route('/api/web_results')
def api_web_results():
    """API pour récupérer les résultats des tâches web uniquement"""
    return jsonify(stats['web_results'])


@app.route('/api/auto_results')
def api_auto_results():
    """API pour récupérer les résultats des tâches automatiques uniquement"""
    return jsonify(stats['auto_results'])


@app.route('/api/clear_stats', methods=['POST'])
def api_clear_stats():
    """API pour effacer les statistiques"""
    global stats
    stats = {
        'sent_tasks': 0,
        'received_results': 0,
        'operations': {'add': 0, 'sub': 0, 'mul': 0, 'div': 0},
        'recent_results': [],
        'web_results': [],
        'auto_results': [],
        'queue_status': {},
        'last_update': datetime.now().isoformat()
    }
    return jsonify({'success': True})


def main():
    print("🚀 Démarrage de l'interface web...")
    
    # Démarrer le consommateur de résultats
    rabbitmq_interface.start_result_consumer()
    
    print("✅ Interface web disponible sur http://localhost:5000")
    print("⚡ Auto-refresh des résultats activé")
    print("🔧 Appuyez sur Ctrl+C pour arrêter")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt de l'interface web...")


if __name__ == '__main__':
    main() 