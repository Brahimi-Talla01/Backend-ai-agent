from groq import Groq
import os
import random
import time
from dotenv import load_dotenv
from config import (
    Config, 
    GroqConfig, 
    WelcomeAgentConfig, 
    SecurityConfig
)

# Charger les variables d'environnement
load_dotenv()

class WelcomeAgent:
    def __init__(self):
        """Initialiser le client Groq et configurer l'agent"""
        
        # Vérification de la clé API
        if not Config.GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY non trouvée dans les variables d'environnement")
        
        print(f"🔑 Initialisation avec la clé API: {Config.GROQ_API_KEY[:20]}...")
        
        # Configuration Groq
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = GroqConfig.DEFAULT_MODEL
        self.temperature = GroqConfig.TEMPERATURE
        self.max_tokens = GroqConfig.MAX_TOKENS
        self.top_p = GroqConfig.TOP_P
        
        # Historique de conversation
        self.conversation_history = []
        self.max_history = GroqConfig.MAX_CONVERSATION_HISTORY
        
        # Informations de l'entreprise
        self.company_name = WelcomeAgentConfig.COMPANY_INFO["name"]
        self.company_specialties = WelcomeAgentConfig.COMPANY_INFO["specialties"]
        self.company_zones = WelcomeAgentConfig.COMPANY_INFO["zones"]
        self.company_experience = WelcomeAgentConfig.COMPANY_INFO["experience"]
        
        # Créer le prompt système dynamique
        self.system_prompt = self._create_system_prompt()
        
        print(f"✅ WelcomeAgent initialisé pour {self.company_name}")
        print(f"🤖 Modèle: {self.model}")
        print(f"🏗️ Spécialités: {', '.join(self.company_specialties[:3])}...")

    def _create_system_prompt(self):
        """Créer le prompt système personnalisé avec les informations de l'entreprise"""
        specialties_text = ', '.join(self.company_specialties)
        zones_text = ', '.join(self.company_zones)
        
        return f"""Tu es WelcomeAgent, l'assistant IA officiel de {self.company_name}, une entreprise spécialisée dans le BTP (Bâtiment et Travaux Publics) avec {self.company_experience}.

INFORMATIONS SUR L'ENTREPRISE :
- Nom : {self.company_name}
- Domaine : BTP - Bâtiment et Travaux Publics
- Spécialités : {specialties_text}
- Zones d'intervention : {zones_text}
- Expérience : {self.company_experience}

PERSONNALITÉ ET TON :
- Professionnel mais accessible et chaleureux
- Expert en construction, rénovation, et travaux publics
- Toujours prêt à aider et orienter les visiteurs
- Utilise un français correct et des termes techniques appropriés
- Représente fièrement {self.company_name}

TES MISSIONS PRINCIPALES :
1. Accueillir chaleureusement les visiteurs du site web
2. Présenter les services et l'expertise de {self.company_name}
3. Identifier le type de visiteur (client, employeur, confrère)
4. Répondre aux questions techniques de base sur le BTP
5. Orienter vers les bons contacts pour devis et projets (Avec le numéro de téléphone suivant: +237 691 733 730 ou à via l'address email: noujiengenering@gmail.com)
6. Expliquer nos processus de travail et notre approche qualité

SERVICES À PROMOUVOIR :
{chr(10).join(f"- {service}" for service in self.company_specialties)}

TYPES D'UTILISATEURS À IDENTIFIER :
- CLIENT : Particulier ou entreprise cherchant des services BTP
- EMPLOYEUR : Recruteur ou entreprise partenaire
- CONFRÈRE : Professionnel du BTP ou partenaire technique

RÈGLES IMPORTANTES :
- Reste TOUJOURS dans le domaine du BTP/construction
- Si on te pose des questions hors-sujet, redirige poliment vers le BTP
- Encourage les visiteurs à prendre contact pour des devis gratuits
- Sois concret et pratique dans tes réponses
- N'invente JAMAIS de prix ou de délais précis
- Dirige vers un expert pour les questions techniques très complexes
- Mentionne régulièrement le nom {self.company_name}
- Valorise l'expertise et l'expérience de l'entreprise

RÉPONSES PERSONNALISÉES :
- Pour un CLIENT : présente nos services, processus de devis, réalisations
- Pour un EMPLOYEUR : met en avant notre expertise, équipe, références
- Pour un CONFRÈRE : échange sur les techniques, possibilités de collaboration

ZONE GÉOGRAPHIQUE :
Nous intervenons principalement sur : {zones_text}

Commence toujours par identifier le type de visiteur pour personnaliser tes réponses et représenter au mieux {self.company_name}."""

    def _should_redirect(self, message):
        """Vérifier si le message contient des sujets à rediriger"""
        message_lower = message.lower()
        
        for topic in WelcomeAgentConfig.FORBIDDEN_TOPICS:
            if topic in message_lower:
                return True
        
        # Vérifier si c'est vraiment lié au BTP
        btp_keywords = [
            'construction', 'bâtiment', 'maison', 'rénovation', 'travaux',
            'maçonnerie', 'charpente', 'couverture', 'béton', 'pierre',
            'devis', 'projet', 'btp', 'entrepreneur', 'artisan'
        ]
        
        has_btp_keyword = any(keyword in message_lower for keyword in btp_keywords)
        
        return not has_btp_keyword and len(message.split()) > 5

    def process_message(self, user_message):
        """Traiter un message utilisateur et retourner la réponse de l'agent"""
        try:
            # Vérifier si c'est un sujet à rediriger
            if self._should_redirect(user_message):
                return random.choice(WelcomeAgentConfig.REDIRECT_RESPONSES).format(
                    company_name=self.company_name
                )
            
            # Ajouter le message utilisateur à l'historique
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Limiter l'historique pour éviter les tokens excessifs
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            # Préparer les messages pour Groq
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Ajouter l'historique de conversation
            messages.extend(self.conversation_history)
            
            print(f"🤖 Envoi à Groq: {len(messages)} messages, modèle {self.model}")
            
            # Appel à l'API Groq avec timeout
            start_time = time.time()
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=GroqConfig.FREQUENCY_PENALTY,
                presence_penalty=GroqConfig.PRESENCE_PENALTY,
                stream=False
            )
            
            response_time = time.time() - start_time
            print(f"⚡ Réponse Groq reçue en {response_time:.2f}s")
            
            # Extraire la réponse
            agent_response = completion.choices[0].message.content
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                "role": "assistant", 
                "content": agent_response
            })
            
            # Log des tokens utilisés
            if hasattr(completion, 'usage'):
                print(f"📊 Tokens utilisés: {completion.usage.total_tokens}")
            
            return agent_response
            
        except Exception as e:
            print(f"Erreur dans WelcomeAgent.process_message: {str(e)}")
            print(f"Type d'erreur: {type(e)}")
            
            # Message d'erreur personnalisé pour l'entreprise
            return f"Désolé, je rencontre un problème technique temporaire. Pour toute urgence, n'hésitez pas à contacter directement {self.company_name}. Vous pouvez également réessayer dans quelques instants."
    
    def reset_conversation(self):
        """Réinitialiser l'historique de conversation"""
        self.conversation_history = []
        
        welcome_msg = WelcomeAgentConfig.WELCOME_MESSAGES["default"].format(
            company_name=self.company_name
        )
        
        print("🔄 Conversation réinitialisée")
        return welcome_msg
    
    def get_conversation_length(self):
        """Obtenir le nombre de messages dans la conversation"""
        return len(self.conversation_history)
    
    def get_company_info(self):
        """Obtenir les informations de l'entreprise"""
        return {
            "name": self.company_name,
            "specialties": self.company_specialties,
            "zones": self.company_zones,
            "experience": self.company_experience
        }
    
    def switch_model(self, model_name):
        """Changer de modèle Groq"""
        if model_name in GroqConfig.MODELS.values():
            self.model = model_name
            print(f"🔄 Modèle changé vers: {model_name}")
            return True
        else:
            print(f"❌ Modèle non reconnu: {model_name}")
            return False
    
    def adjust_creativity(self, temperature):
        """Ajuster la créativité de l'agent (0.0 à 1.0)"""
        if 0.0 <= temperature <= 1.0:
            self.temperature = temperature
            print(f"🎨 Créativité ajustée à: {temperature}")
            return True
        else:
            print(f"❌ Température invalide: {temperature} (doit être entre 0.0 et 1.0)")
            return False