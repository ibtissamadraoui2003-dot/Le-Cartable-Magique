# main_game.py
"""
Jeu principal avec interface graphique
"""

import pygame
import sys
import random
import time
from game_ui import GameUI
from questions_db import QuestionDatabase
from traps import TrapSystem
from sounds import SoundManager
from rl_agent import RLAgent


class MainGame:
    """Jeu principal avec toutes les fonctionnalités"""
    
    def __init__(self):
        # Définir la taille de la grille ici
        self.GRID_SIZE = 12
        
        self.ui = GameUI(grid_size=self.GRID_SIZE, cell_size=50)
        self.questions_db = QuestionDatabase()
        self.trap_system = TrapSystem()
        
        # Initialiser le gestionnaire de sons
        self.sound_manager = SoundManager()
        
        # Mode de jeu : 'human', 'ai_simple', 'ai_rl'
        self.game_mode = 'human'  # Par défaut mode humain
        
        # Agent RL
        self.rl_agent = RLAgent(grid_size=self.GRID_SIZE)
        self.ai_training = False
        self.ai_episodes = 1000
        
        # Variables pour l'IA
        self.ai_last_action_time = 0
        self.ai_speed = 0.3  # secondes entre mouvements
        self.ai_state_history = []
        
        # Menu
        self.menu_active = True
        self.menu_selection = 0
        self.menu_options = [
            ("🎮 Mode Humain", "human"),
            ("🤖 Mode IA Simple", "ai_simple"),
            ("🧠 Mode IA RL", "ai_rl"),
            ("🎓 Entraîner IA RL", "train_rl"),
            ("🚪 Quitter", "quit")
        ]
        
        # État du jeu
        self.reset_game()
    
    def reset_game(self):
        """Réinitialise le jeu"""
        self.score = 0
        self.steps = 0
        self.level = 1
        self.game_state = 'playing'
        self.current_question = None
        self.question_position = None
        self.agent_position = [1, 1]
        
        # Réinitialiser l'IA
        self.ai_state_history = []
        
        # Initialiser le gestionnaire de sons
        if hasattr(self, 'sound_manager'):
            self.sound_manager.load_sounds()
            self.sound_manager.play_background_music()
        
        # Générer la carte et les éléments
        self.generate_level()
    
    def generate_level(self):
        """Génère un niveau de jeu"""
        # Carte 12x12 CORRIGÉE
        self.map_layout = [
            [1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,2,0,0,0,2,0,0,0,1],
            [1,0,1,1,0,1,0,1,1,0,1,1],
            [1,2,0,0,0,0,2,0,0,0,0,1],
            [1,1,1,0,1,1,1,1,0,1,1,1],
            [1,0,0,2,0,0,0,0,2,0,0,1],
            [1,0,1,1,1,0,1,1,1,1,0,1],
            [1,2,0,0,0,2,0,0,0,0,2,1],
            [1,1,0,1,1,1,0,1,1,0,1,1],
            [1,0,0,0,0,0,3,0,0,0,0,1],
            [1,0,0,0,1,0,0,0,1,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        # Positions des questions
        self.question_positions = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.map_layout[i][j] == 2:
                    self.question_positions.append((i, j))
        
        # Réinitialiser les questions répondues
        self.questions_answered = {pos: False for pos in self.question_positions}
        
        # Générer pièges et bonus
        self.trap_system.generate_traps(self.map_layout, num_traps=6)
        self.trap_system.generate_bonuses(self.map_layout, num_bonuses=4)
        
        # Position de départ
        self.agent_position = [1, 1]
        
        # Réinitialiser les effets
        self.trap_system.active_effects = {}
    
    def move_agent(self, direction):
        """Déplace l'agent dans une direction"""
        if self.game_state != 'playing':
            return False
        
        new_position = self.agent_position.copy()
        
        # Gérer les effets actifs (confusion inverse les contrôles)
        if self.trap_system.has_effect('confusion'):
            if direction == 'up':
                direction = 'down'
            elif direction == 'down':
                direction = 'up'
            elif direction == 'left':
                direction = 'right'
            elif direction == 'right':
                direction = 'left'
        
        # Calculer la nouvelle position
        if direction == 'up':
            new_position[0] -= 1
        elif direction == 'down':
            new_position[0] += 1
        elif direction == 'left':
            new_position[1] -= 1
        elif direction == 'right':
            new_position[1] += 1
        else:
            return False
        
        # Vérifier les limites et les murs
        if (0 <= new_position[0] < self.GRID_SIZE and 
            0 <= new_position[1] < self.GRID_SIZE and
            self.map_layout[new_position[0]][new_position[1]] != 1):
            
            # ANIMATION DE PAS
            self.ui.add_animation('step', tuple(new_position))
            
            # SON DE PAS
            if hasattr(self, 'sound_manager'):
                self.sound_manager.play_sound('step')
            
            # Appliquer les pénalités/bonus de vitesse
            move_penalty = -1  # Pénalité de base par mouvement
            
            if self.trap_system.has_effect('slow'):
                move_penalty -= 2
            
            if self.trap_system.has_effect('speed'):
                move_penalty += 1
            
            self.score += move_penalty
            self.steps += 1
            
            # Vérifier les pièges et bonus
            trap_bonus_check = self.trap_system.check_position(new_position)
            
            if trap_bonus_check:
                type_, item = trap_bonus_check
                
                if type_ == 'trap':
                    # ANIMATION PIÈGE
                    self.ui.add_animation('wrong', tuple(new_position))
                    
                    # SON PIÈGE
                    if hasattr(self, 'sound_manager'):
                        self.sound_manager.play_sound('trap')
                    
                    # Appliquer le piège
                    if not self.trap_system.has_effect('shield'):
                        self.score += item['effect'].get('penalty', 0)
                        
                        # Message du piège
                        print(f"⚠️ {item['effect']['message']}")
                        
                        # Appliquer l'effet spécial
                        if item['type'] == 'teleport':
                            new_position = self.trap_system.apply_trap_effect(
                                item, new_position, self.map_layout
                            )
                        else:
                            # Ajouter l'effet
                            self.trap_system.add_effect(
                                item['type'],
                                {'duration': item['effect'].get('duration', 0)}
                            )
                    
                    # Désactiver le piège
                    item['active'] = False
                
                elif type_ == 'bonus':
                    # ANIMATION BONUS
                    self.ui.add_animation('correct', tuple(new_position))
                    
                    # SON BONUS
                    if hasattr(self, 'sound_manager'):
                        self.sound_manager.play_sound('bonus')
                    
                    # Appliquer le bonus
                    self.score += item['effect'].get('bonus', 0)
                    
                    # Message du bonus
                    print(f"🎁 {item['effect']['message']}")
                    
                    # Ajouter l'effet
                    if item['type'] != 'points':
                        self.trap_system.add_effect(
                            item['type'],
                            {'duration': item['effect'].get('duration', 0)}
                        )
                    
                    # Désactiver le bonus
                    item['active'] = False
            
            # Mettre à jour la position
            self.agent_position = new_position
            
            # Vérifier si on est sur une question
            pos_tuple = tuple(new_position)
            if pos_tuple in self.question_positions:
                if not self.questions_answered[pos_tuple]:
                    self.ask_question(pos_tuple)
                    return True
            
            # Vérifier si on est sur la sortie (case valeur 3)
            if self.map_layout[new_position[0]][new_position[1]] == 3:
                self.complete_level()
                return True
            
            # Mettre à jour les effets
            self.trap_system.update_effects()
            
            return True
        
        return False  # Mouvement invalide
    
    def ask_question(self, position):
        """Pose une question à l'agent"""
        difficulty = 'easy' if self.level < 3 else 'medium' if self.level < 6 else 'hard'
        self.current_question = self.questions_db.get_random_question(difficulty)
        self.game_state = 'question'
        self.question_position = position
    
    def answer_question(self, answer):
        """Traite la réponse à une question"""
        if not self.current_question:
            return
        
        is_correct = self.questions_db.check_answer(self.current_question, answer)
        
        if is_correct:
            points = 20 if self.level < 3 else 30 if self.level < 6 else 50
            self.score += points
            self.questions_answered[self.question_position] = True
            
            # ANIMATION BONNE RÉPONSE
            self.ui.add_animation('correct', self.question_position)
            
            # SON BONNE RÉPONSE
            if hasattr(self, 'sound_manager'):
                self.sound_manager.play_sound('bonus')
            
            print(f"✅ Bonne réponse! +{points} points")
        else:
            self.score -= 10
            
            # ANIMATION MAUVAISE RÉPONSE
            self.ui.add_animation('wrong', self.question_position)
            
            # SON MAUVAISE RÉPONSE
            if hasattr(self, 'sound_manager'):
                self.sound_manager.play_sound('trap')
            
            print(f"❌ Mauvaise réponse! -10 points")
        
        self.current_question = None
        self.game_state = 'playing'
    
    def complete_level(self):
        """Termine le niveau actuel"""
        # Points bonus pour les questions restantes
        unanswered = sum(1 for answered in self.questions_answered.values() if not answered)
        bonus = 100 - (unanswered * 20)
        self.score += max(bonus, 0)
        
        print(f"🎉 Niveau {self.level} terminé!")
        print(f"📊 Score du niveau: {bonus} points bonus")
        
        # SON NIVEAU TERMINÉ
        if hasattr(self, 'sound_manager'):
            self.sound_manager.play_sound('bonus')
        
        # Passer au niveau suivant
        self.level += 1
        if self.level <= 5:
            self.generate_level()
        else:
            self.game_state = 'game_over'
            print("🏆 Jeu terminé! Tu as fini tous les niveaux!")
    
    def get_ai_action_simple(self):
        """IA simple : évite les murs, cherche les questions et la sortie"""
        x, y = self.agent_position
        
        # Directions possibles
        directions = []
        
        # Vérifier chaque direction
        for direction, (dx, dy) in [('up', (-1, 0)), ('down', (1, 0)), 
                                    ('left', (0, -1)), ('right', (0, 1))]:
            nx, ny = x + dx, y + dy
            
            # Vérifier si la case est valide
            if (0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE and
                self.map_layout[nx][ny] != 1):
                
                # Priorité 1 : Sortie
                if self.map_layout[nx][ny] == 3:
                    return direction
                
                # Priorité 2 : Question non répondue
                if (nx, ny) in self.question_positions:
                    if not self.questions_answered[(nx, ny)]:
                        return direction
                
                directions.append(direction)
        
        # Si aucune priorité, mouvement aléatoire valide
        if directions:
            return random.choice(directions)
        
        return None  # Aucun mouvement possible
    
    def get_ai_action_rl(self):
        """IA RL : utilise la Q-table pour choisir l'action"""
        # Obtenir l'état courant
        state_key = self.rl_agent.get_state_key(
            self.map_layout,
            self.agent_position,
            self.questions_answered,
            self.trap_system.has_effect('shield')
        )
        
        # Choisir l'action (mode exploitation uniquement)
        action = self.rl_agent.choose_action(state_key, training=False)
        
        # Sauvegarder l'état pour l'affichage
        self.ai_state_history.append({
            'state': state_key[:20] + "...",  # Tronquer pour l'affichage
            'action': action,
            'q_values': self.rl_agent.q_table[state_key].tolist()
        })
        
        # Garder seulement les 10 derniers états
        if len(self.ai_state_history) > 10:
            self.ai_state_history.pop(0)
        
        return action
    
    def update_ai(self):
        """Met à jour l'IA selon le mode sélectionné"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.ai_last_action_time < self.ai_speed:
            return False
        
        self.ai_last_action_time = current_time
        
        # Choisir l'action selon le mode
        if self.game_mode == 'ai_simple':
            action = self.get_ai_action_simple()
        elif self.game_mode == 'ai_rl':
            action = self.get_ai_action_rl()
        else:
            return False
        
        if action:
            self.move_agent(action)
            return True
        
        return False
    
    def draw_menu(self):
        """Dessine le menu principal"""
        self.ui.screen.fill((30, 30, 50))
        
        # Titre
        title = self.ui.fonts['title'].render("LE CARTABLE MAGIQUE", True, (240, 240, 240))
        title_rect = title.get_rect(center=(self.ui.width//2, 100))
        self.ui.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.ui.fonts['normal'].render("Choisissez un mode de jeu", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(self.ui.width//2, 160))
        self.ui.screen.blit(subtitle, subtitle_rect)
        
        # Options du menu
        option_height = 60
        start_y = 250
        
        for i, (text, mode) in enumerate(self.menu_options):
            color = (100, 200, 255) if i == self.menu_selection else (200, 200, 200)
            
            option_text = self.ui.fonts['normal'].render(text, True, color)
            option_rect = option_text.get_rect(center=(self.ui.width//2, start_y + i * option_height))
            
            # Fond pour l'option sélectionnée
            if i == self.menu_selection:
                highlight_rect = option_rect.inflate(40, 20)
                pygame.draw.rect(self.ui.screen, (60, 60, 90), highlight_rect, border_radius=10)
                pygame.draw.rect(self.ui.screen, (100, 100, 150), highlight_rect, 2, border_radius=10)
            
            self.ui.screen.blit(option_text, option_rect)
        
        # Instructions
        instructions = [
            "Utilisez ↑ ↓ pour naviguer",
            "ESPACE ou ENTRÉE pour sélectionner"
        ]
        
        inst_y = start_y + len(self.menu_options) * option_height + 50
        for j, inst in enumerate(instructions):
            inst_text = self.ui.fonts['small'].render(inst, True, (150, 150, 150))
            inst_rect = inst_text.get_rect(center=(self.ui.width//2, inst_y + j * 30))
            self.ui.screen.blit(inst_text, inst_rect)
    
    def handle_menu_click(self, pos):
        """Gère le clic souris sur le menu"""
        option_height = 60
        start_y = 250

        for i, (_, mode) in enumerate(self.menu_options):
            rect = pygame.Rect(self.ui.width // 2 - 180, start_y + i * option_height - 20, 360, 50)
            if rect.collidepoint(pos):
                if mode == 'quit':
                    return 'quit'

                if mode == 'train_rl':
                    print("🎓 Début de l'entraînement RL...")
                    self.rl_agent.train(self, episodes=self.ai_episodes)
                    print("✅ Entraînement terminé!")
                    return 'menu'

                self.game_mode = mode
                self.menu_active = False
                print(f"🎮 Mode sélectionné: {mode}")
                return 'play'

        return 'menu'

    def handle_menu_events(self):
        """Gère les événements dans le menu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return self.handle_menu_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'

                elif event.key in (pygame.K_UP, pygame.K_z):
                    self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    if hasattr(self, 'sound_manager'):
                        self.sound_manager.play_sound('step')

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    if hasattr(self, 'sound_manager'):
                        self.sound_manager.play_sound('step')

                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    _, selected_mode = self.menu_options[self.menu_selection]

                    if selected_mode == 'quit':
                        return 'quit'

                    elif selected_mode == 'train_rl':
                        print("🎓 Début de l'entraînement RL...")
                        self.rl_agent.train(self, episodes=self.ai_episodes)
                        print("✅ Entraînement terminé!")
                        return 'menu'

                    else:
                        self.game_mode = selected_mode
                        self.menu_active = False
                        print(f"🎮 Mode sélectionné: {selected_mode}")
                        return 'play'

        return 'menu'
    
    def draw_ai_info(self):
        """Affiche les informations de l'IA"""
        if self.game_mode not in ['ai_simple', 'ai_rl']:
            return
        
        # Panneau d'info IA
        panel_x = self.ui.grid_size * self.ui.cell_size + 10
        panel_y = 400
        panel_width = self.ui.side_panel_width - 20
        panel_height = 200
        
        # Fond
        pygame.draw.rect(self.ui.screen, (40, 40, 70), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.ui.screen, (80, 80, 130), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Titre
        mode_text = "🤖 IA Simple" if self.game_mode == 'ai_simple' else "🧠 IA RL"
        title = self.ui.fonts['small'].render(f"MODE: {mode_text}", True, (100, 255, 100))
        self.ui.screen.blit(title, (panel_x + 10, panel_y + 10))
        
        y_offset = panel_y + 40
        
        if self.game_mode == 'ai_rl' and hasattr(self, 'rl_agent') and self.rl_agent:
            # Infos RL
            info_lines = [
                f"Épisodes entraînés: {self.rl_agent.episodes_trained}",
                f"États appris: {len(self.rl_agent.q_table)}",
                f"Récompense totale: {self.rl_agent.total_reward:.0f}"
            ]
            
            for line in info_lines:
                text = self.ui.fonts['small'].render(line, True, (200, 200, 200))
                self.ui.screen.blit(text, (panel_x + 10, y_offset))
                y_offset += 25
            
            # Dernières décisions
            if hasattr(self, 'ai_state_history') and self.ai_state_history:
                y_offset += 10
                history_title = self.ui.fonts['small'].render("Dernières décisions:", True, (255, 200, 100))
                self.ui.screen.blit(history_title, (panel_x + 10, y_offset))
                y_offset += 25
                
                for i, hist in enumerate(self.ai_state_history[-3:]):
                    text = f"{hist['action']}: Q={max(hist['q_values']):.2f}"
                    hist_text = self.ui.fonts['small'].render(text, True, (200, 200, 255))
                    self.ui.screen.blit(hist_text, (panel_x + 20, y_offset))
                    y_offset += 20
    
    def run(self):
        """Boucle principale du jeu"""
        clock = pygame.time.Clock()
        
        while self.ui.running:
            # Menu principal
            if self.menu_active:
                menu_result = self.handle_menu_events()
                
                if menu_result == 'quit':
                    self.ui.running = False
                    break
                elif menu_result == 'play':
                    self.reset_game()
                
                self.draw_menu()
                self.ui.update()
                clock.tick(60)
                continue
            
            # Gérer les événements en mode jeu
            event_result = self.ui.handle_events()
            
            if event_result:
                if isinstance(event_result, tuple) and event_result[0] == 'click':
                    pos = event_result[1]
                    
                    if self.game_state == 'game_over':
                        restart_rect, quit_rect = self.ui.draw_game_over(self.score, self.score > 0)
                        
                        if restart_rect.collidepoint(pos):
                            self.reset_game()
                        elif quit_rect.collidepoint(pos):
                            self.menu_active = True  # Retour au menu
                
                elif event_result == 'quit':
                    self.ui.running = False
                
                elif event_result == 'restart':
                    self.reset_game()
                
                elif event_result in ['up', 'down', 'left', 'right']:
                    if self.game_state == 'question':
                        mapping = {'left': 'a', 'up': 'b', 'down': 'c', 'right': 'd'}
                        self.answer_question(mapping[event_result])
                    elif self.game_mode == 'human' and self.game_state == 'playing':
                        self.move_agent(event_result)

                elif event_result in ['a', 'b', 'c', 'd']:
                    if self.game_state == 'question':
                        self.answer_question(event_result)
                
                elif event_result == 'm':  # Touche M pour retour au menu
                    self.menu_active = True
            
            # Mise à jour de l'IA
            if self.game_mode in ['ai_simple', 'ai_rl'] and self.game_state == 'playing':
                self.update_ai()
            
            # Dessiner l'interface
            if self.game_state == 'playing':
                active_traps = [trap['position'] for trap in self.trap_system.traps if trap['active']]
                active_bonuses = [bonus['position'] for bonus in self.trap_system.bonuses if bonus['active']]
                
                self.ui.draw_grid(
                    self.map_layout,
                    self.agent_position,
                    self.questions_answered,
                    active_traps,
                    active_bonuses
                )
                
                remaining_questions = sum(1 for answered in self.questions_answered.values() if not answered)
                self.ui.draw_side_panel(
                    score=self.score,
                    steps=self.steps,
                    level=self.level,
                    remaining_questions=remaining_questions
                )
                
                # Infos IA
                self.draw_ai_info()
                
                if self.trap_system.active_effects:
                    self.ui.draw_active_effects(self.trap_system.active_effects)
            
            elif self.game_state == 'question' and self.current_question:
                active_traps = [trap['position'] for trap in self.trap_system.traps if trap['active']]
                active_bonuses = [bonus['position'] for bonus in self.trap_system.bonuses if bonus['active']]
                
                self.ui.draw_grid(
                    self.map_layout,
                    self.agent_position,
                    self.questions_answered,
                    active_traps,
                    active_bonuses
                )
                
                self.ui.draw_question_popup(
                    self.current_question['question'],
                    self.current_question['choices']
                )
            
            elif self.game_state == 'game_over':
                success = self.score > 0
                self.ui.draw_game_over(self.score, success)
            
            # Mettre à jour les animations
            self.ui.update_animations()
            
            # Mettre à jour l'affichage
            self.ui.update()
            
            # Limiter à 60 FPS
            clock.tick(60)
        
        # Sauvegarder le modèle RL avant de quitter
        if hasattr(self, 'rl_agent') and self.game_mode == 'ai_rl':
            self.rl_agent.save_model()
        
        # Quitter proprement
        self.ui.quit()

if __name__ == "__main__":
    print("🎮 Démarrage du jeu 'Le Cartable Magique'...")
    print("=" * 50)
    print("Contrôles:")
    print("  Mode Humain:")
    print("    Z/↑ : Haut     Q/← : Gauche")
    print("    S/↓ : Bas      D/→ : Droite")
    print("    ESPACE : Passer")
    print("    R : Recommencer")
    print("    M : Menu")
    print("    ÉCHAP : Quitter")
    print("=" * 50)
    
    game = MainGame()
    game.run()