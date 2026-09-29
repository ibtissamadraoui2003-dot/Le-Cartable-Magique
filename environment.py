# environment.py
"""
Sprint 1 : Classe Environment propre pour le jeu éducatif
"""

import numpy as np
import time

class SchoolEnvironment:
    """Environnement RL pour le jeu éducatif 'Le Cartable Magique'"""
    
    def __init__(self, map_size=5):
        """
        Initialise l'environnement
        
        Args:
            map_size: Taille de la grille (carrée)
        """
        self.map_size = map_size
        
        # Définir la carte (identique au Sprint 0)
        self.world_map = np.array([
            [1, 1, 1, 1, 1],
            [1, 0, 2, 0, 3],
            [1, 1, 0, 1, 1],
            [1, 2, 0, 2, 1],
            [1, 1, 1, 1, 1]
        ])
        
        # Questions avec leurs positions
        self.questions = {
            (1, 2): {
                "question": "2 + 2 = ?",
                "answer": "4",
                "answered": False,
                "reward_correct": 10,
                "reward_wrong": -5
            },
            (3, 1): {
                "question": "Capitale de la France ?",
                "answer": "Paris",
                "answered": False,
                "reward_correct": 10,
                "reward_wrong": -5
            },
            (3, 3): {
                "question": "L'homme est un mammifère. Vrai ou faux ?",
                "answer": "Vrai",
                "answered": False,
                "reward_correct": 10,
                "reward_wrong": -5
            }
        }
        
        # Positions importantes
        self.start_pos = np.array([1, 1])  # Position de départ
        self.exit_pos = np.array([1, 4])   # Position de la sortie
        
        # Récompenses
        self.rewards = {
            "empty": -0.5,      # Case vide
            "wall": -2,       # Mur
            "exit": 200,      # Sortie
            "step": -0.1      # Pénalité par pas (optionnel)
        }
        
        # État du jeu
        self.reset()
        
    def reset(self):
        """
        Réinitialise l'environnement à son état initial
        
        Returns:
            state: L'état initial
        """
        # Réinitialiser la position de l'agent
        self.agent_pos = self.start_pos.copy()
        
        # Réinitialiser toutes les questions
        for pos in self.questions:
            self.questions[pos]["answered"] = False
            
        # Réinitialiser les variables d'état
        self.done = False
        self.total_reward = 0
        self.steps = 0
        
        # Retourner l'état initial
        return self._get_state()
    
    def _get_state(self):
        """
        Convertit la position actuelle en état
        
        Returns:
            state: Un tuple (x, y) pour l'instant
                   Plus tard: (x, y, q1, q2, q3)
        """
        # Pour le Sprint 1, état simple = position
        return tuple(self.agent_pos)
    
    def _is_valid_position(self, pos):
        """
        Vérifie si une position est valide (dans les limites et pas un mur)
        
        Args:
            pos: Position à vérifier [ligne, colonne]
            
        Returns:
            bool: True si valide
        """
        # Vérifier les limites
        if (pos[0] < 0 or pos[0] >= self.map_size or 
            pos[1] < 0 or pos[1] >= self.map_size):
            return False
            
        # Vérifier si c'est un mur
        if self.world_map[pos[0], pos[1]] == 1:
            return False
            
        return True
    
    def step(self, action):
        """
        Exécute une action dans l'environnement
        
        Args:
            action: 0=haut, 1=bas, 2=gauche, 3=droite
            
        Returns:
            next_state: Nouvel état après l'action
            reward: Récompense obtenue
            done: True si l'épisode est terminé
            info: Informations supplémentaires
        """
        if self.done:
            raise ValueError("L'épisode est terminé. Appelle reset() d'abord.")
            
        self.steps += 1
        reward = 0
        info = {}
        
        # 1. Calculer la nouvelle position
        new_pos = self.agent_pos.copy()
        
        if action == 0:    # Haut
            new_pos[0] -= 1
        elif action == 1:  # Bas
            new_pos[0] += 1
        elif action == 2:  # Gauche
            new_pos[1] -= 1
        elif action == 3:  # Droite
            new_pos[1] += 1
        else:
            raise ValueError(f"Action invalide: {action}. Doit être 0, 1, 2 ou 3.")
        
        # 2. Vérifier si le mouvement est valide
        if not self._is_valid_position(new_pos):
            # C'est un mur ou hors limites
            reward += self.rewards["wall"]
            info["hit_wall"] = True
            info["message"] = "Ouch! Vous avez heurté un mur."
        else:
            # Mouvement valide, mettre à jour la position
            self.agent_pos = new_pos
            
            # 3. Vérifier le type de case et donner la récompense
            cell_type = self.world_map[new_pos[0], new_pos[1]]
            
            if cell_type == 0:  # Case vide
                reward += self.rewards["empty"]
                info["cell_type"] = "empty"
                
            elif cell_type == 2:  # Question
                info["cell_type"] = "question"
                pos_key = tuple(new_pos)
                
                if pos_key in self.questions:
                    question_info = self.questions[pos_key]
                    
                    if not question_info["answered"]:
                        # Marquer comme répondue et donner récompense positive
                        # (Pour l'instant, on suppose que l'agent répond toujours correctement)
                        question_info["answered"] = True
                        reward += question_info["reward_correct"]
                        info["question_answered"] = True
                        info["question_text"] = question_info["question"]
                        info["message"] = f"Bonne réponse! {question_info['reward_correct']} points."
                    else:
                        info["message"] = "Question déjà répondue."
                        reward += 0
                        
            elif cell_type == 3:  # Sortie
                info["cell_type"] = "exit"
                reward += self.rewards["exit"]
                self.done = True
                info["message"] = "Félicitations! Diplôme obtenu!"
        
        # Pénalité pour chaque pas (optionnel)
        reward += self.rewards["step"]
        
        # Mettre à jour la récompense totale
        self.total_reward += reward
        
        # Préparer le retour
        next_state = self._get_state()
        info["total_reward"] = self.total_reward
        info["steps"] = self.steps
        
        return next_state, reward, self.done, info
    
    def render(self, mode='human'):
        """
        Affiche l'état actuel de l'environnement
        
        Args:
            mode: 'human' pour affichage texte, 'rgb_array' pour image (futur)
        """
        if mode == 'human':
            print("\n" + "="*30)
            print(f"Step: {self.steps} | Reward total: {self.total_reward:.1f}")
            print("="*30)
            
            for i in range(self.map_size):
                for j in range(self.map_size):
                    pos = np.array([i, j])
                    
                    # Afficher l'agent
                    if np.array_equal(pos, self.agent_pos):
                        print("A", end=" ")
                    else:
                        cell = self.world_map[i, j]
                        if cell == 0:
                            print(".", end=" ")
                        elif cell == 1:
                            print("#", end=" ")
                        elif cell == 2:
                            # Vérifier si la question est répondue
                            if (i, j) in self.questions and self.questions[(i, j)]["answered"]:
                                print("✓", end=" ")  # Question répondue
                            else:
                                print("Q", end=" ")  # Question non répondue
                        elif cell == 3:
                            print(">", end=" ")  # Sortie
                print()  # Nouvelle ligne
            
            # Afficher les questions non répondues
            unanswered = []
            for pos, q in self.questions.items():
                if not q["answered"]:
                    unanswered.append(q["question"])
            
            if unanswered:
                print("\nQuestions restantes:")
                for i, q in enumerate(unanswered, 1):
                    print(f"  {i}. {q}")
            
            if self.done:
                print("\n✅ ÉPISODE TERMINÉ !")
    
    def get_actions(self):
        """
        Retourne la liste des actions possibles
        
        Returns:
            list: [0, 1, 2, 3] pour haut, bas, gauche, droite
        """
        return [0, 1, 2, 3]
    
    def get_state_size(self):
        """
        Retourne la taille de l'espace d'états
        """
        return 2  # Pour l'instant, seulement (x, y)
    
    def get_action_size(self):
        """
        Retourne la taille de l'espace d'actions
        """
        return 4  # 4 directions