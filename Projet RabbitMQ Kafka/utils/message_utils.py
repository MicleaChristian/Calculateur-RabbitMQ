"""Utilitaires pour la gestion des messages"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any


def create_task_message(n1: float, n2: float, operation: str, source="auto") -> Dict[str, Any]:
    """
    Crée un message de tâche de calcul
    
    Args:
        n1: Premier nombre
        n2: Deuxième nombre  
        operation: Type d'opération (add, sub, mul, div)
        source: Source de la tâche ("auto" pour automatique, "web" pour interface web)
    """
    return {
        "n1": n1,
        "n2": n2,
        "operation": operation,
        "source": source,
        "request_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat()
    }


def create_result_message(task_message: Dict[str, Any], result: float, 
                         worker_id: str, processing_time: float) -> Dict[str, Any]:
    """Crée un message de résultat au format JSON"""
    return {
        "n1": task_message["n1"],
        "n2": task_message["n2"],
        "op": task_message["operation"],
        "result": result,
        "source": task_message.get("source", "auto"),
        "request_id": task_message["request_id"],
        "worker_id": worker_id,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }


def serialize_message(message: Dict[str, Any]) -> str:
    """Sérialise un message en JSON"""
    return json.dumps(message, indent=2)


def deserialize_message(message_str: str) -> Dict[str, Any]:
    """Désérialise un message JSON"""
    return json.loads(message_str)


def perform_operation(operation: str, n1: float, n2: float) -> float:
    """Effectue l'opération mathématique demandée"""
    operations = {
        'add': lambda x, y: x + y,
        'sub': lambda x, y: x - y,
        'mul': lambda x, y: x * y,
        'div': lambda x, y: x / y if y != 0 else float('inf')
    }
    
    if operation not in operations:
        raise ValueError(f"Opération non supportée: {operation}")
    
    return operations[operation](n1, n2)


def validate_task_message(message: Dict[str, Any]) -> bool:
    """Valide qu'un message de tâche a tous les champs requis"""
    required_fields = ["n1", "n2", "operation", "request_id", "timestamp"]
    return all(field in message for field in required_fields)


def format_result_display(result_message: Dict[str, Any]) -> str:
    """Formate un message de résultat pour l'affichage"""
    return (f"[{result_message['timestamp']}] "
            f"Résultat: {result_message['n1']} {result_message['op']} {result_message['n2']} "
            f"= {result_message['result']} "
            f"(Worker: {result_message['worker_id']}, "
            f"Temps: {result_message['processing_time']:.1f}s, "
            f"ID: {result_message['request_id'][:8]})") 