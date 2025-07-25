from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agents.welcome_agent import WelcomeAgent
from config import Config, load_config, SecurityConfig
import time
from collections import defaultdict

load_dotenv()

if not load_config():
      exit(1)

app = Flask(__name__)

# Configuration CORS avec les paramètres du fichier config
CORS(app, resources={
      r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
      }
})

# Rate limiting simple (stockage en mémoire)
request_counts = defaultdict(lambda: {"count": 0, "reset_time": time.time() + 60})

def check_rate_limit(client_ip):
      """Vérifier le rate limiting"""
      current_time = time.time()
      client_data = request_counts[client_ip]
      
      # Reset du compteur si 1 minute écoulée
      if current_time > client_data["reset_time"]:
            client_data["count"] = 0
            client_data["reset_time"] = current_time + 60
      
      # Vérifier la limite
      if client_data["count"] >= SecurityConfig.RATE_LIMIT_PER_MINUTE:
            return False
      
      client_data["count"] += 1
      return True

def validate_message(message):
      """Valider le message utilisateur"""
      if not message:
            return False, "Message vide"
      
      if len(message) < SecurityConfig.MIN_MESSAGE_LENGTH:
            return False, "Message trop court"
      
      if len(message) > SecurityConfig.MAX_MESSAGE_LENGTH:
            return False, "Message trop long"
      
      # Vérifier les mots interdits
      message_lower = message.lower()
      for blocked_word in SecurityConfig.BLOCKED_WORDS:
            if blocked_word in message_lower:
                  return False, f"Contenu non autorisé détecté"
      
      return True, None

# Initialiser l'agent
welcome_agent = WelcomeAgent()

@app.route('/api/welcome', methods=['POST'])
def chat_with_welcome_agent():
      try:
            # Obtenir l'IP du client pour le rate limiting
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            
            # Vérifier le rate limiting
            if not check_rate_limit(client_ip):
                  return jsonify({
                        'error': 'Trop de requêtes. Veuillez patienter avant de réessayer.',
                        'rate_limit_exceeded': True
                  }), 429
            
            print(f"🔄 Requête reçue de {client_ip}")
            
            # Récupérer le message depuis le frontend
            data = request.get_json()
            print(f"Data reçue: {data}")
            
            if not data or 'message' not in data:
                  print("Erreur: Message manquant")
                  return jsonify({
                        'error': 'Message requis'
                  }), 400
            
            user_message = data['message']
            
            # Valider le message
            is_valid, error_msg = validate_message(user_message)
            if not is_valid:
                  print(f"Validation échouée: {error_msg}")
                  return jsonify({
                        'error': error_msg
                  }), 400
            
            print(f"Message utilisateur: {user_message}")
            
            # Traiter le message avec l'agent
            print("Appel à welcome_agent.process_message...")
            response = welcome_agent.process_message(user_message)
            print(f"Réponse générée ({len(response)} caractères)")
            
            return jsonify({
                  'response': response,
                  'timestamp': time.time()
            })
        
      except Exception as e:
            print(f"ERREUR dans chat_with_welcome_agent: {str(e)}")
            print(f"Type d'erreur: {type(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                  'error': 'Erreur interne du serveur. Veuillez réessayer.',
                  'error_type': 'server_error'
            }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
      """Route de test pour vérifier que le serveur fonctionne"""
      return jsonify({
            'status': 'OK',
            'message': 'WelcomeAgent backend is running!',
            'config': {
                  'model': welcome_agent.model,
                  'company': welcome_agent.company_name,
                  'version': '1.0.0'
            }
      })

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
      """Réinitialiser la conversation"""
      try:
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            
            if not check_rate_limit(client_ip):
                  return jsonify({
                  'error': 'Trop de requêtes. Veuillez patienter.'
                  }), 429
            
            message = welcome_agent.reset_conversation()
            return jsonify({
                  'response': message,
                  'conversation_reset': True
            })
      except Exception as e:
            print(f"Erreur reset: {str(e)}")
            return jsonify({
                  'error': 'Erreur lors de la réinitialisation'
            }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
      """Obtenir des statistiques sur la conversation"""
      try:
            return jsonify({
                  'conversation_length': welcome_agent.get_conversation_length(),
                  'model_used': welcome_agent.model,
                  'company_info': {
                  'name': welcome_agent.company_name,
                  'specialties': welcome_agent.company_specialties
                  }
            })
      except Exception as e:
            print(f"Erreur stats: {str(e)}")
            return jsonify({
                  'error': 'Erreur lors de la récupération des statistiques'
            }), 500

if __name__ == '__main__':
      print("Démarrage du serveur WelcomeAgent...")
      print(f"API disponible sur: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
      print(f"Health check: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}/api/health")
      
      app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
      )