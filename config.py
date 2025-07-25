import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration générale de l'application"""
    
    # Configuration Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")   
    FLASK_PORT = int(os.getenv("FLASK_PORT", 10000)) 
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true" 
    
    # Configuration CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")  
    
    # Configuration API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Validation des variables d'environnement
    @classmethod
    def validate_config(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY manquante dans le fichier .env ou dans les variables Render")
        return True


class GroqConfig:
    """Configuration spécifique pour Groq"""
    
    MODELS = {
        "fast": "llama3-8b-8192",          
        "balanced": "llama3-70b-8192",      
        "mixtral": "mixtral-8x7b-32768",    
    }
    
    DEFAULT_MODEL = MODELS["fast"]
    
    # Paramètres de génération
    TEMPERATURE = 0.7          
    MAX_TOKENS = 1024          
    TOP_P = 1.0              
    FREQUENCY_PENALTY = 0.0    
    PRESENCE_PENALTY = 0.0    
    
    # Limites de conversation
    MAX_CONVERSATION_HISTORY = 10    
    
    # Timeout et retry
    REQUEST_TIMEOUT = 30      
    MAX_RETRIES = 3          

class WelcomeAgentConfig:
    """Configuration professionnelle de l'assistant WelcomeAgent pour N.E.GROUP (Secteur BTP)."""
    
    COMPANY_INFO = {
            "name": "Nouji Engennering Group Sarl",
            "abbreviation": "N.E.GROUP",
            "domain": "BTP - Bâtiment et Travaux Publics",
            "specialties": [
                  "Construction neuve",
                  "Rénovation et réhabilitation", 
                  "Gros œuvre et second œuvre",
                  "Maçonnerie générale",
                  "Charpente et couverture",
                  "Aménagements extérieurs",
                  "Études techniques et conseils en ingénierie"
            ],
            "zones": ["Yaoundé", "Centre", "Cameroun"],  
            "experience": "Plus de 15 ans d'expertise dans le secteur du BTP",
            "certifications": ["ISO 9001", "Qualification BTP", "Ministère des Travaux Public"]  
      }
    
    USER_TYPES = {
            "client": "Particulier ou entreprise à la recherche de services de construction, rénovation ou aménagement",
            "employer": "Professionnel ou structure souhaitant collaborer ou sous-traiter avec N.E.GROUP",
            "colleague": "Acteur du secteur BTP : architecte, ingénieur, maître d'œuvre, etc."
    }
    
    WELCOME_MESSAGES = {
            "default": (
                  "Bonjour et bienvenue chez Nouji Engineering Group Sarl ! "
                  "Je suis WelcomeAgent, votre assistant virtuel dédié au secteur du BTP. "
                  "Comment puis-je vous accompagner aujourd’hui ?"
            ),
            "client": (
                  "Bonjour et merci de votre intérêt ! En tant que client, je peux vous orienter "
                  "vers nos services adaptés à votre projet de construction ou de rénovation. "
                  "Souhaitez-vous un devis, une consultation ou en savoir plus sur nos réalisations ?"
            ),
            "employer": (
                  "Bienvenue ! Nous serions ravis d’envisager une collaboration. "
                  "Souhaitez-vous découvrir nos compétences, références ou modalités de partenariat ?"
            ),
            "colleague": (
                  "Bonjour confrère du BTP ! Échangeons volontiers sur nos pratiques, nos expertises "
                  "et les opportunités de collaboration dans le secteur du bâtiment."
            )
      }
    
    # Sujets à éviter
    FORBIDDEN_TOPICS = [
            "politique", 
            "religion", 
            "santé ou conseils médicaux", 
            "conseils juridiques", 
            "finances personnelles", 
            "crypto-monnaie", 
            "questions hors BTP"
      ]
    
    # Réponses de redirection
    REDIRECT_RESPONSES = [
            "Je suis spécialisé dans le domaine du BTP. Souhaitez-vous en savoir plus sur nos services ou obtenir un devis ?",
            "Mon domaine d'expertise est la construction et la rénovation. Parlez-moi de votre projet pour que je puisse vous orienter.",
            "Concentrons-nous sur ce que nous maîtrisons : le BTP. Avez-vous un chantier en vue ou des travaux à planifier ?"    
      ]

class LoggingConfig:
    """Configuration pour les logs"""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/welcome_agent.log"
    
    # Logs spécifiques
    LOG_CONVERSATIONS = True     
    LOG_API_CALLS = True        
    LOG_ERRORS = True            
    
class SecurityConfig:
    """Configuration de sécurité"""
    
    # Rate limiting (requêtes par minute)
    RATE_LIMIT_PER_MINUTE = 30
    
    # Filtres de contenu
    MAX_MESSAGE_LENGTH = 1000    
    MIN_MESSAGE_LENGTH = 1       
    
    # Mots interdits (spam/abus)
    BLOCKED_WORDS = [
        "spam", "hack", "malware", "injures"
    ]

# Fonction utilitaire pour charger la config
def load_config():
    """Charger et valider la configuration"""
    try:
        Config.validate_config()
        print("✅ Configuration chargée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

# Export des configurations
__all__ = [
    'Config',
    'GroqConfig', 
    'WelcomeAgentConfig',
    'LoggingConfig',
    'SecurityConfig',
    'load_config'
]