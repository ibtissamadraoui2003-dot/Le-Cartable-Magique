# rl_agent.py
"""
Agent par apprentissage par renforcement pour le jeu
"""

import numpy as np
import random
import pickle
import os
from collections import defaultdict

class RLAgent:
    """Agent Q-learning pour le jeu éducatif"""
    
    def __init__(self, grid_size=12, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.grid_size = grid_size
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de discount
        self.epsilon = epsilon  # Exploration rate
        
        # Actions possibles : haut, bas, gauche, droite
        self.actions = ['up', 'down', 'left', 'right']
        self.action_indices = {a: i for i, a in enumerate(self.actions)}
        
        # Table Q : état -> valeurs des actions
        self.q_table = defaultdict(lambda: np.zeros(len(self.actions)))
        
        # Statistiques
        self.episodes_trained = 0
        self.total_reward = 0
        
        # Charger modèle existant si disponible
        self.load_model()
    
    def get_state_key(self, map_layout, agent_pos, questions_answered, has_shield=False):
        """Convertit l'état du jeu en clé pour la Q-table"""
        # État simplifié : position + cases autour + questions répondues
        x, y = agent_pos
        
        # Vision de 3x3 autour de l'agent
        vision = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    cell = map_layout[nx][ny]
                    # Encodage simple
                    if cell == 1:  # Mur
                        vision.append('W')
                    elif cell == 2:  # Question
                        pos_key = (nx, ny)
                        if questions_answered.get(pos_key, False):
                            vision.append('Q')  # Question répondue
                        else:
                            vision.append('?')  # Question non répondue
                    elif cell == 3:  # Sortie
                        vision.append('E')
                    else:  # Vide ou piège/bonus
                        vision.append('.')
                else:
                    vision.append('B')  # Bord
        
        # Clé d'état
        state_key = f"{x},{y}|{''.join(vision)}|{int(has_shield)}"
        return state_key
    
    def choose_action(self, state_key, training=True):
        """Choisit une action selon la politique ε-greedy"""
        if training and random.random() < self.epsilon:
            # Exploration : action aléatoire
            return random.choice(self.actions)
        else:
            # Exploitation : meilleure action selon Q-table
            q_values = self.q_table[state_key]
            max_q = np.max(q_values)
            
            # Toutes les actions avec la valeur max
            best_actions = [self.actions[i] for i, q in enumerate(q_values) if q == max_q]
            
            # Si plusieurs actions égales, choix aléatoire parmi elles
            return random.choice(best_actions)
    
    def update_q_value(self, state, action, reward, next_state, done=False):
        """Met à jour la Q-table selon l'algorithme Q-learning"""
        action_idx = self.action_indices[action]
        
        # Valeur Q courante
        current_q = self.q_table[state][action_idx]
        
        if done:
            # État terminal
            target = reward
        else:
            # Meilleure valeur Q pour le prochain état
            next_max_q = np.max(self.q_table[next_state])
            target = reward + self.gamma * next_max_q
        
        # Mise à jour Q-learning
        self.q_table[state][action_idx] = current_q + self.alpha * (target - current_q)
        
        return self.q_table[state][action_idx]
    
    def calculate_reward(self, map_layout, old_pos, new_pos, questions_status, 
                        got_trap=False, got_bonus=False, answered_correct=False,
                        reached_exit=False, step_penalty=-1):
        """Calcule la récompense pour une transition"""
        reward = 0
        
        # Pénalité pour chaque pas
        reward += step_penalty
        
        # Récompense pour avoir bougé (évite stagnation)
        if old_pos != new_pos:
            reward += 0.1
        
        # Cases spéciales
        x, y = new_pos
        cell_type = map_layout[x][y]
        
        if cell_type == 2:  # Question
            pos_key = (x, y)
            if not questions_status.get(pos_key, False):
                # Nouvelle question découverte
                reward += 5
            else:
                # Question déjà répondue
                reward += 0.5
        
        elif cell_type == 3:  # Sortie
            reward += 50  # Grande récompense pour la sortie
        
        # Événements spéciaux
        if got_trap:
            reward -= 20
        
        if got_bonus:
            reward += 15
        
        if answered_correct:
            reward += 30
        
        if reached_exit:
            reward += 100
        
        # Encouragement à explorer les bords
        if x == 0 or x == self.grid_size-1 or y == 0 or y == self.grid_size-1:
            reward -= 1  # Légère pénalité pour les bords
        
        return reward
    
    def save_model(self, filename='rl_agent_model.pkl'):
        """Sauvegarde le modèle entraîné"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'q_table': dict(self.q_table),
                    'episodes_trained': self.episodes_trained,
                    'total_reward': self.total_reward,
                    'alpha': self.alpha,
                    'gamma': self.gamma,
                    'epsilon': self.epsilon
                }, f)
            print(f"✅ Modèle sauvegardé : {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde modèle : {e}")
    
    def load_model(self, filename='rl_agent_model.pkl'):
        """Charge un modèle entraîné"""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                
                self.q_table = defaultdict(lambda: np.zeros(len(self.actions)))
                self.q_table.update(data['q_table'])
                self.episodes_trained = data['episodes_trained']
                self.total_reward = data['total_reward']
                print(f"✅ Modèle chargé : {filename}")
                print(f"   Épisodes entraînés : {self.episodes_trained}")
                print(f"   Récompense totale : {self.total_reward}")
                print(f"   États appris : {len(self.q_table)}")
                return True
        except Exception as e:
            print(f"❌ Erreur chargement modèle : {e}")
        
        return False
    
    def train_episode(self, game_env, max_steps=100):
        """Entraîne l'agent sur un épisode complet"""
        # Réinitialiser l'environnement
        game_env.reset_game()
        game_env.game_mode = 'ai_training'
        
        state = self.get_state_key(
            game_env.map_layout,
            game_env.agent_position,
            game_env.questions_answered,
            game_env.trap_system.has_effect('shield')
        )
        
        total_reward = 0
        steps = 0
        done = False
        
        while not done and steps < max_steps:
            # Choisir une action
            action = self.choose_action(state, training=True)
            
            # Exécuter l'action dans l'environnement
            old_score = game_env.score
            old_pos = tuple(game_env.agent_position)
            
            # Simulation du mouvement (simplifiée pour l'entraînement)
            new_pos = list(old_pos)
            if action == 'up':
                new_pos[0] -= 1
            elif action == 'down':
                new_pos[0] += 1
            elif action == 'left':
                new_pos[1] -= 1
            elif action == 'right':
                new_pos[1] += 1
            
            # Vérifier la validité du mouvement
            if (0 <= new_pos[0] < self.grid_size and 
                0 <= new_pos[1] < self.grid_size and
                game_env.map_layout[new_pos[0]][new_pos[1]] != 1):
                
                game_env.agent_position = new_pos
                steps += 1
                
                # Vérifier les événements
                got_trap = False
                got_bonus = False
                answered_correct = False
                reached_exit = False
                
                # Vérifier sortie
                if game_env.map_layout[new_pos[0]][new_pos[1]] == 3:
                    reached_exit = True
                    done = True
                
                # Nouvel état
                next_state = self.get_state_key(
                    game_env.map_layout,
                    game_env.agent_position,
                    game_env.questions_answered,
                    game_env.trap_system.has_effect('shield')
                )
                
                # Calculer la récompense
                reward = self.calculate_reward(
                    game_env.map_layout,
                    old_pos,
                    tuple(new_pos),
                    game_env.questions_answered,
                    got_trap,
                    got_bonus,
                    answered_correct,
                    reached_exit
                )
                
                total_reward += reward
                
                # Mettre à jour la Q-table
                self.update_q_value(state, action, reward, next_state, done)
                
                # Passer au nouvel état
                state = next_state
            else:
                # Mouvement invalide - pénalité
                reward = -5
                total_reward += reward
                done = True
        
        self.episodes_trained += 1
        self.total_reward += total_reward
        
        return total_reward, steps
    
    def train(self, game_env, episodes=1000):
        """Entraîne l'agent sur plusieurs épisodes"""
        print(f"🎯 Début de l'entraînement sur {episodes} épisodes...")
        
        rewards_history = []
        steps_history = []
        
        for episode in range(episodes):
            reward, steps = self.train_episode(game_env)
            rewards_history.append(reward)
            steps_history.append(steps)
            
            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(rewards_history[-100:])
                avg_steps = np.mean(steps_history[-100:])
                print(f"  Épisode {episode+1}/{episodes} - "
                      f"Récompense moyenne: {avg_reward:.1f} - "
                      f"Pas moyens: {avg_steps:.1f}")
        
        # Sauvegarder après l'entraînement
        self.save_model()
        
        print("✅ Entraînement terminé!")
        print(f"   Épisodes: {self.episodes_trained}")
        print(f"   États appris: {len(self.q_table)}")
        print(f"   Récompense totale: {self.total_reward}")
        
        return rewards_history, steps_history