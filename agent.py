# agent.py
"""
Sprint 2 : Agent Q-Learning pour notre jeu éducatif
"""

import numpy as np
import random
from collections import defaultdict

class QLearningAgent:
    """Agent qui apprend avec l'algorithme Q-Learning"""
    
    def __init__(self, state_size, action_size, learning_rate=0.3, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.995, min_exploration_rate=0.01):
        """
        Initialise l'agent Q-Learning
        
        Args:
            state_size: Nombre d'états possibles
            action_size: Nombre d'actions possibles
            learning_rate (alpha): Taux d'apprentissage (0.1)
            discount_factor (gamma): Importance des récompenses futures (0.9)
            exploration_rate (epsilon): Probabilité d'exploration (1.0 = 100%)
            exploration_decay: Réduction d'exploration après chaque épisode
            min_exploration_rate: Exploration minimale (0.01 = 1%)
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        
        # Initialiser la Q-table avec des zéros
        # Utilisation de defaultdict pour créer des états non vus
        self.q_table = defaultdict(lambda: np.zeros(action_size))
        
        # Statistiques
        self.total_rewards = []
        self.episode_lengths = []
        
    def get_state_key(self, state):
        """
        Convertit un état en clé pour la Q-table
        
        Args:
            state: L'état (tuple ou autre)
            
        Returns:
            Une clé hashable (ici, un tuple)
        """
        # Pour notre environnement, state est déjà un tuple (x, y)
        return tuple(state)
    
    def choose_action(self, state, training=True):
        """
        Choisit une action selon la politique ε-greedy
        
        Args:
            state: État actuel
            training: Si True, utilise l'exploration
            
        Returns:
            action: Action choisie (0 à action_size-1)
        """
        state_key = self.get_state_key(state)
        
        if training and random.random() < self.exploration_rate:
            # Exploration : action aléatoire
            return random.randint(0, self.action_size - 1)
        else:
            # Exploitation : meilleure action selon Q-table
            q_values = self.q_table[state_key]
            # En cas d'égalité, choisir au hasard parmi les meilleures
            max_q = np.max(q_values)
            best_actions = np.where(q_values == max_q)[0]
            return random.choice(best_actions)
    
    def learn(self, state, action, reward, next_state, done):
        """
        Met à jour la Q-table avec l'expérience (s, a, r, s')
        
        Args:
            state: État actuel
            action: Action prise
            reward: Récompense obtenue
            next_state: Nouvel état
            done: Si l'épisode est terminé
        """
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Valeur Q actuelle
        current_q = self.q_table[state_key][action]
        
        if done:
            # Pas d'état futur si terminé
            target_q = reward
        else:
            # Meilleure valeur Q pour le prochain état
            next_max_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.discount_factor * next_max_q
        
        # Mise à jour de la Q-table avec la formule Q-Learning
        self.q_table[state_key][action] = current_q + self.learning_rate * (target_q - current_q)
    
    def update_exploration_rate(self):
        """Réduit le taux d'exploration après chaque épisode"""
        self.exploration_rate = max(self.min_exploration_rate, 
                                   self.exploration_rate * self.exploration_decay)
    
    def save(self, filename="q_agent.pkl"):
        """Sauvegarde la Q-table dans un fichier"""
        import pickle
        with open(filename, 'wb') as f:
            # Convertir defaultdict en dict normal pour la sauvegarde
            q_table_dict = dict(self.q_table)
            pickle.dump({
                'q_table': q_table_dict,
                'exploration_rate': self.exploration_rate,
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor
            }, f)
        print(f"✅ Agent sauvegardé dans {filename}")
    
    def load(self, filename="q_agent.pkl"):
        """Charge la Q-table depuis un fichier"""
        import pickle
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.q_table = defaultdict(lambda: np.zeros(self.action_size), data['q_table'])
                self.exploration_rate = data['exploration_rate']
                self.learning_rate = data.get('learning_rate', self.learning_rate)
                self.discount_factor = data.get('discount_factor', self.discount_factor)
            print(f"✅ Agent chargé depuis {filename}")
            return True
        except FileNotFoundError:
            print(f"⚠️  Fichier {filename} non trouvé. Agent non chargé.")
            return False
    
    def get_stats(self):
        """Retourne des statistiques sur l'agent"""
        num_states = len(self.q_table)
        total_q_values = sum(len(q) for q in self.q_table.values())
        
        return {
            "states_explores": num_states,
            "q_values_stored": total_q_values,
            "exploration_rate": self.exploration_rate,
            "avg_reward": np.mean(self.total_rewards[-100:]) if self.total_rewards else 0
        }
    
    def print_q_table_sample(self, num_samples=5):
        """Affiche un échantillon de la Q-table"""
        print("\n📊 ÉCHANTILLON DE LA Q-TABLE :")
        print("=" * 50)
        
        items = list(self.q_table.items())
        if not items:
            print("Q-table vide !")
            return
            
        for i, (state, q_values) in enumerate(items[:num_samples]):
            print(f"État {state}:")
            for action, q_value in enumerate(q_values):
                action_name = ["Haut", "Bas", "Gauche", "Droite"][action]
                print(f"  {action_name}: {q_value:.4f}")
            print()