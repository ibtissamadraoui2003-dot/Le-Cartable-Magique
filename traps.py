# traps.py
"""
Système de pièges et bonus pour le jeu
"""

import random

class TrapSystem:
    """Gère les pièges et bonus dans le jeu"""
    
    def __init__(self):
        self.traps = []
        self.bonuses = []
        self.active_effects = {}
        self.effect_counter = 0
    
    def generate_traps(self, map_layout, num_traps=6):
        """Génère des pièges aléatoirement sur la carte"""
        self.traps = []
        empty_cells = []
        
        # Trouver toutes les cases vides (0) ou avec questions (2) MAIS pas de murs (1)
        for i in range(len(map_layout)):
            for j in range(len(map_layout[0])):
                if map_layout[i][j] in [0, 2]:  # Case vide ou question
                    # Ne pas mettre sur la case de départ (1, 1) ni sur la sortie (3)
                    if not (i == 1 and j == 1) and map_layout[i][j] != 3:
                        # Vérifier que ce n'est pas déjà une sortie
                        is_exit = False
                        for x in range(len(map_layout)):
                            for y in range(len(map_layout[0])):
                                if map_layout[x][y] == 3 and x == i and y == j:
                                    is_exit = True
                                    break
                        if not is_exit:
                            empty_cells.append((i, j))
        
        # Choisir aléatoirement des cases pour les pièges
        if len(empty_cells) >= num_traps:
            trap_cells = random.sample(empty_cells, num_traps)
            for cell in trap_cells:
                trap_type = random.choice(['slow', 'teleport', 'penalty', 'confusion'])
                self.traps.append({
                    'position': cell,
                    'type': trap_type,
                    'active': True,
                    'effect': self.get_trap_effect(trap_type)
                })
    
    def generate_bonuses(self, map_layout, num_bonuses=4):
        """Génère des bonus aléatoirement sur la carte"""
        self.bonuses = []
        empty_cells = []
        
        # Trouver toutes les cases vides (sans pièges et sans questions déjà)
        for i in range(len(map_layout)):
            for j in range(len(map_layout[0])):
                if map_layout[i][j] in [0, 2]:  # Case vide ou question
                    # Vérifier que ce n'est pas déjà un piège, la case de départ ou une sortie
                    is_trap = any(trap['position'] == (i, j) for trap in self.traps)
                    is_exit = (map_layout[i][j] == 3)
                    if not is_trap and not (i == 1 and j == 1) and not is_exit:
                        empty_cells.append((i, j))
        
        # Choisir aléatoirement des cases pour les bonus
        if len(empty_cells) >= num_bonuses:
            bonus_cells = random.sample(empty_cells, num_bonuses)
            for cell in bonus_cells:
                bonus_type = random.choice(['speed', 'points', 'shield', 'hint'])
                self.bonuses.append({
                    'position': cell,
                    'type': bonus_type,
                    'active': True,
                    'effect': self.get_bonus_effect(bonus_type)
                })
    
    def get_trap_effect(self, trap_type):
        """Retourne l'effet d'un piège"""
        effects = {
            'slow': {
                'name': 'Ralentissement',
                'description': 'Tu es ralenti pendant 3 tours!',
                'duration': 3,
                'penalty': -2,
                'message': 'Piège! Tu es ralenti...'
            },
            'teleport': {
                'name': 'Téléportation',
                'description': 'Tu es téléporté à une position aléatoire!',
                'duration': 0,
                'message': 'Piège! Tu es téléporté ailleurs!'
            },
            'penalty': {
                'name': 'Pénalité',
                'description': 'Tu perds 20 points!',
                'duration': 0,
                'penalty': -20,
                'message': 'Piège! -20 points!'
            },
            'confusion': {
                'name': 'Confusion',
                'description': 'Tes contrôles sont inversés pendant 2 tours!',
                'duration': 2,
                'message': 'Piège! Les contrôles sont inversés!'
            }
        }
        return effects.get(trap_type, effects['slow'])
    
    def get_bonus_effect(self, bonus_type):
        """Retourne l'effet d'un bonus"""
        effects = {
            'speed': {
                'name': 'Vitesse',
                'description': 'Tu es plus rapide pendant 4 tours!',
                'duration': 4,
                'bonus': 1,
                'message': 'Bonus! Tu es plus rapide!'
            },
            'points': {
                'name': 'Points bonus',
                'description': '+30 points!',
                'duration': 0,
                'bonus': 30,
                'message': 'Bonus! +30 points!'
            },
            'shield': {
                'name': 'Bouclier',
                'description': 'Immunisé aux pièges pendant 5 tours!',
                'duration': 5,
                'message': 'Bonus! Bouclier activé!'
            },
            'hint': {
                'name': 'Indice',
                'description': 'Indice pour la prochaine question!',
                'duration': 0,
                'message': 'Bonus! Tu obtiens un indice!'
            }
        }
        return effects.get(bonus_type, effects['points'])
    
    def check_position(self, position):
        """Vérifie si une position contient un piège ou un bonus"""
        pos_tuple = tuple(position)
        
        for trap in self.traps:
            if trap['position'] == pos_tuple and trap['active']:
                return ('trap', trap)
        
        for bonus in self.bonuses:
            if bonus['position'] == pos_tuple and bonus['active']:
                return ('bonus', bonus)
        
        return None
    
    def apply_trap_effect(self, trap, agent_position, map_layout):
        """Applique l'effet d'un piège"""
        if trap['type'] == 'teleport':
            # Téléporter à une position aléatoire vide
            empty_cells = []
            for i in range(len(map_layout)):
                for j in range(len(map_layout[0])):
                    if map_layout[i][j] == 0:  # Case vide seulement
                        # Ne pas se téléporter sur la position actuelle
                        if not (i == agent_position[0] and j == agent_position[1]):
                            empty_cells.append([i, j])
            
            if empty_cells:
                return random.choice(empty_cells)
        
        return agent_position
    
    def update_effects(self):
        """Met à jour la durée des effets actifs"""
        to_remove = []
        for effect_id, effect in list(self.active_effects.items()):
            if 'duration' in effect:
                effect['duration'] -= 1
                if effect['duration'] <= 0:
                    to_remove.append(effect_id)
        
        for effect_id in to_remove:
            del self.active_effects[effect_id]
    
    def has_effect(self, effect_type):
        """Vérifie si un effet est actif"""
        for effect in self.active_effects.values():
            if effect.get('type') == effect_type:
                return True
        return False
    
    def add_effect(self, effect_type, effect_data):
        """Ajoute un effet actif"""
        effect_id = f"{effect_type}_{self.effect_counter}"
        self.effect_counter += 1
        self.active_effects[effect_id] = {
            'type': effect_type,
            **effect_data
        }
        return effect_id