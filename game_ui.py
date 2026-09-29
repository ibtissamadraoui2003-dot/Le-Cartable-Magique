# game_ui.py - VERSION CORRIGÉE
"""
Interface graphique PyGame pour le jeu éducatif
"""

import pygame
import sys
from pygame.locals import *

class GameUI:
    """Interface graphique PyGame"""
    
    def __init__(self, grid_size=12, cell_size=50):
        pygame.init()
    
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.side_panel_width = 350
        
        # Augmenter la hauteur pour le panneau IA
        self.width = grid_size * cell_size + self.side_panel_width
        self.height = grid_size * cell_size + 250  # +100 pour l'info IA
        
        # Création de la fenêtre
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Le Cartable Magique - RL Éducatif")
            
            # Couleurs
        self.colors = {
            'background': (30, 30, 50),
            'grid': (50, 50, 80),
            'wall': (100, 100, 150),
            'empty': (40, 40, 70),
            'agent': (0, 200, 100),
            'question': (255, 200, 50),
            'question_answered': (100, 200, 100),
            'exit': (255, 100, 100),
            'trap': (200, 50, 50),
            'bonus': (50, 200, 255),
            'text': (240, 240, 240),
            'panel': (40, 40, 60),
            'button': (80, 120, 200),
            'button_hover': (100, 140, 220)
        }
        
        # Polices
        self.fonts = {
            'title': pygame.font.SysFont('Arial', 36, bold=True),
            'normal': pygame.font.SysFont('Arial', 24),
            'small': pygame.font.SysFont('Arial', 18),
            'question': pygame.font.SysFont('Arial', 22)
        }
        
        # État du jeu
        self.running = True
        self.current_question = None
        self.question_answered = False
        
        # Animations
        self.animations = []
        
        # Charger les images (sprites simples)
        self.load_sprites()
    
    def load_sprites(self):
        """Crée des sprites simples pour le jeu"""
        self.sprites = {}
        
        # Agent (carré vert avec yeux)
        agent_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.rect(agent_surface, self.colors['agent'], (0, 0, self.cell_size-10, self.cell_size-10), border_radius=10)
        # Yeux
        pygame.draw.circle(agent_surface, (255, 255, 255), (20, 20), 8)
        pygame.draw.circle(agent_surface, (255, 255, 255), (self.cell_size-30, 20), 8)
        pygame.draw.circle(agent_surface, (0, 0, 0), (20, 20), 4)
        pygame.draw.circle(agent_surface, (0, 0, 0), (self.cell_size-30, 20), 4)
        self.sprites['agent'] = agent_surface
        
        # Question (point d'interrogation)
        question_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.circle(question_surface, self.colors['question'], 
                          (self.cell_size//2 - 5, self.cell_size//2 - 5), 
                          (self.cell_size - 20)//2)
        # Texte "?"
        font = pygame.font.SysFont('Arial', 40, bold=True)
        text = font.render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.cell_size//2 - 5, self.cell_size//2 - 5))
        question_surface.blit(text, text_rect)
        self.sprites['question'] = question_surface
        
        # Question répondue (coche)
        answered_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.circle(answered_surface, self.colors['question_answered'], 
                          (self.cell_size//2 - 5, self.cell_size//2 - 5), 
                          (self.cell_size - 20)//2)
        # Coche
        font = pygame.font.SysFont('Arial', 40, bold=True)
        text = font.render("✓", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.cell_size//2 - 5, self.cell_size//2 - 5))
        answered_surface.blit(text, text_rect)
        self.sprites['question_answered'] = answered_surface
        
        # Sortie (porte)
        exit_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.rect(exit_surface, self.colors['exit'], 
                        (10, 10, self.cell_size-30, self.cell_size-30), 
                        border_radius=5, width=3)
        # Texte "EXIT"
        font = pygame.font.SysFont('Arial', 20, bold=True)
        text = font.render("EXIT", True, self.colors['exit'])
        text_rect = text.get_rect(center=(self.cell_size//2 - 5, self.cell_size//2 - 5))
        exit_surface.blit(text, text_rect)
        self.sprites['exit'] = exit_surface
        
        # Piège (crâne)
        trap_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.circle(trap_surface, self.colors['trap'], 
                          (self.cell_size//2 - 5, self.cell_size//2 - 5), 
                          (self.cell_size - 20)//2)
        # Crâne
        font = pygame.font.SysFont('Arial', 30, bold=True)
        text = font.render("☠", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.cell_size//2 - 5, self.cell_size//2 - 5))
        trap_surface.blit(text, text_rect)
        self.sprites['trap'] = trap_surface
        
        # Bonus (étoile)
        bonus_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
        pygame.draw.circle(bonus_surface, self.colors['bonus'], 
                          (self.cell_size//2 - 5, self.cell_size//2 - 5), 
                          (self.cell_size - 20)//2)
        # Étoile
        font = pygame.font.SysFont('Arial', 30, bold=True)
        text = font.render("★", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.cell_size//2 - 5, self.cell_size//2 - 5))
        bonus_surface.blit(text, text_rect)
        self.sprites['bonus'] = bonus_surface
    
    def add_animation(self, anim_type, position, value=None):
        """Ajoute une animation simple"""
        self.animations.append({
            'type': anim_type,
            'pos': position,
            'value': value,
            'start_time': pygame.time.get_ticks()
        })
    
    def update_animations(self):
        """Met à jour les animations"""
        current_time = pygame.time.get_ticks()
        self.animations = [anim for anim in self.animations 
                          if current_time - anim['start_time'] < 1000]
    
    def draw_grid(self, world_map, agent_pos, questions_status, traps, bonuses):
        """Dessine la grille de jeu"""
        # Fond
        self.screen.fill(self.colors['background'])
        
        # Header
        header_rect = pygame.Rect(0, 0, self.width, 100)
        pygame.draw.rect(self.screen, (40, 40, 70), header_rect)
        
        # Titre
        title = self.fonts['title'].render("LE CARTABLE MAGIQUE", True, self.colors['text'])
        title_rect = title.get_rect(center=(self.width//2, 50))
        self.screen.blit(title, title_rect)
        
        # Dessiner la grille
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect = pygame.Rect(
                    j * self.cell_size, 
                    100 + i * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                
                cell_type = world_map[i][j]
                
                if cell_type == 1:  # Mur
                    color = self.colors['wall']
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, (80, 80, 130), rect, 2)
                    
                elif cell_type in [0, 2, 3]:  # Vide, Question ou Sortie
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)
                    pygame.draw.rect(self.screen, self.colors['grid'], rect, 1)
                    
                    # Dessiner les éléments spéciaux selon le type de case
                    if cell_type == 2:  # Question
                        sprite_key = 'question_answered' if questions_status.get((i, j), False) else 'question'
                        sprite_rect = self.sprites[sprite_key].get_rect(center=rect.center)
                        self.screen.blit(self.sprites[sprite_key], sprite_rect)
                        
                    elif cell_type == 3:  # Sortie
                        sprite_rect = self.sprites['exit'].get_rect(center=rect.center)
                        self.screen.blit(self.sprites['exit'], sprite_rect)
                
                # Dessiner les pièges
                if (i, j) in traps:
                    sprite_rect = self.sprites['trap'].get_rect(center=rect.center)
                    self.screen.blit(self.sprites['trap'], sprite_rect)
                    
                # Dessiner les bonus
                if (i, j) in bonuses:
                    sprite_rect = self.sprites['bonus'].get_rect(center=rect.center)
                    self.screen.blit(self.sprites['bonus'], sprite_rect)
        
        # Dessiner l'agent
        agent_rect = pygame.Rect(
            agent_pos[1] * self.cell_size + 5,
            100 + agent_pos[0] * self.cell_size + 5,
            self.cell_size - 10,
            self.cell_size - 10
        )
        self.screen.blit(self.sprites['agent'], agent_rect)
        
        # Dessiner les animations
        current_time = pygame.time.get_ticks()
        for anim in self.animations[:]:
            elapsed = current_time - anim['start_time']
            if elapsed > 1000:
                continue
                
            progress = elapsed / 1000.0
            pos_x = anim['pos'][1] * self.cell_size + self.cell_size // 2
            pos_y = 100 + anim['pos'][0] * self.cell_size + self.cell_size // 2
            
            if anim['type'] == 'step':
                radius = int(5 + progress * 20)
                alpha = int(255 * (1 - progress))
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, alpha), (radius, radius), radius, 2)
                self.screen.blit(s, (pos_x - radius, pos_y - radius))
                
            elif anim['type'] == 'correct':
                radius = int(10 + progress * 30)
                alpha = int(255 * (1 - progress))
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, alpha), (radius, radius), radius, 4)
                self.screen.blit(s, (pos_x - radius, pos_y - radius))
                
            elif anim['type'] == 'wrong':
                radius = int(10 + progress * 30)
                alpha = int(255 * (1 - progress))
                s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, alpha), (radius, radius), radius, 4)
                self.screen.blit(s, (pos_x - radius, pos_y - radius))
                
            elif anim['type'] == 'score' and anim['value'] is not None:
                offset_y = -progress * 50
                alpha = int(255 * (1 - progress))
                color = (0, 255, 0, alpha) if anim['value'] > 0 else (255, 0, 0, alpha)
                text = f"+{anim['value']}" if anim['value'] > 0 else f"{anim['value']}"
                
                font = pygame.font.SysFont('Arial', 20, bold=True)
                text_surf = font.render(text, True, color)
                text_surf.set_alpha(alpha)
                self.screen.blit(text_surf, (pos_x - 15, pos_y + offset_y))
        
        # Légende
        self.draw_legend()
    
    def draw_legend(self):
        """Dessine la légende en bas"""
        legend_y = 100 + self.grid_size * self.cell_size + 10
        legend_items = [
            ("Agent", 'agent'),
            ("Question", 'question'),
            ("Répondu", 'question_answered'),
            ("Sortie", 'exit'),
            ("Piège", 'trap'),
            ("Bonus", 'bonus')
        ]
        
        spacing = self.width // len(legend_items)
        
        for i, (text, sprite_type) in enumerate(legend_items):
            x = i * spacing + 20
            
            scaled_sprite = pygame.transform.scale(self.sprites[sprite_type], (30, 30))
            sprite_rect = scaled_sprite.get_rect(midleft=(x, legend_y + 15))
            self.screen.blit(scaled_sprite, sprite_rect)
            
            label = self.fonts['small'].render(text, True, self.colors['text'])
            self.screen.blit(label, (x + 40, legend_y + 5))
    
    def draw_side_panel(self, score=0, steps=0, level=1, remaining_questions=0):
        """Dessine le panneau latéral avec les informations"""
        panel_rect = pygame.Rect(
            self.grid_size * self.cell_size, 
            100, 
            self.side_panel_width, 
            self.grid_size * self.cell_size
        )
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect)
        
        y_offset = 120
        spacing = 40
        
        # Titre du panneau
        panel_title = self.fonts['normal'].render("INFORMATIONS", True, self.colors['text'])
        self.screen.blit(panel_title, (self.grid_size * self.cell_size + 20, y_offset))
        y_offset += spacing
        
        # Score
        score_text = self.fonts['small'].render(f"Score: {score}", True, self.colors['text'])
        self.screen.blit(score_text, (self.grid_size * self.cell_size + 30, y_offset))
        y_offset += 30
        
        # Pas
        steps_text = self.fonts['small'].render(f"Pas: {steps}", True, self.colors['text'])
        self.screen.blit(steps_text, (self.grid_size * self.cell_size + 30, y_offset))
        y_offset += 30
        
        # Niveau
        level_text = self.fonts['small'].render(f"Niveau: {level}", True, self.colors['text'])
        self.screen.blit(level_text, (self.grid_size * self.cell_size + 30, y_offset))
        y_offset += 30
        
        # Questions restantes
        questions_text = self.fonts['small'].render(f"Questions restantes: {remaining_questions}", True, self.colors['text'])
        self.screen.blit(questions_text, (self.grid_size * self.cell_size + 30, y_offset))
        y_offset += 40
        
        # Contrôles
        controls_title = self.fonts['small'].render("CONTROLES:", True, self.colors['text'])
        self.screen.blit(controls_title, (self.grid_size * self.cell_size + 20, y_offset))
        y_offset += 30
        
        controls = [
            "Z / ↑ : Haut",
            "Q / ← : Gauche",
            "S / ↓ : Bas",
            "D / → : Droite",
            "ESPACE : Passer",
            "R : Recommencer",
            "ECHAP : Quitter",
            "A/B/C/D : Répondre"
        ]
        
        for control in controls:
            control_text = self.fonts['small'].render(control, True, self.colors['text'])
            self.screen.blit(control_text, (self.grid_size * self.cell_size + 30, y_offset))
            y_offset += 25
    
    def draw_active_effects(self, active_effects):
        """Dessine les effets actifs en bas de l'écran"""
        effects_y = 100 + self.grid_size * self.cell_size + 50
        
        if not active_effects:
            return
        
        effects_title = self.fonts['small'].render("EFFETS ACTIFS:", True, self.colors['text'])
        self.screen.blit(effects_title, (20, effects_y))
        
        x_offset = 150
        for effect_id, effect in active_effects.items():
            effect_type = effect['type']
            duration = effect.get('duration', 0)
            
            # Couleur selon le type d'effet
            if effect_type in ['speed', 'shield', 'hint', 'points']:
                color = (100, 255, 100)  # Vert pour les bonus
            else:
                color = (255, 100, 100)  # Rouge pour les pièges
            
            effect_text = self.fonts['small'].render(
                f"{effect_type}: {duration}t", True, color
            )
            self.screen.blit(effect_text, (x_offset, effects_y))
            x_offset += 120
    
    def draw_question_popup(self, question_text, choices=None):
        """Dessine une popup de question"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Rectangle de la popup
        popup_width = 600
        popup_height = 400
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(self.screen, (60, 60, 90), popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 150), popup_rect, 3, border_radius=15)
        
        # Titre
        title = self.fonts['normal'].render("QUESTION", True, self.colors['text'])
        title_rect = title.get_rect(center=(self.width//2, popup_y + 40))
        self.screen.blit(title, title_rect)
        
        # Question (avec wrap de texte)
        question_lines = self.wrap_text(question_text, self.fonts['question'], popup_width - 100)
        for i, line in enumerate(question_lines):
            question_surf = self.fonts['question'].render(line, True, self.colors['text'])
            question_rect = question_surf.get_rect(center=(self.width//2, popup_y + 100 + i * 30))
            self.screen.blit(question_surf, question_rect)
        
        # Choix multiples
        if choices:
            for i, choice in enumerate(choices):
                choice_text = f"{chr(65 + i)}) {choice}"  # A) ..., B) ..., etc.
                choice_surf = self.fonts['normal'].render(choice_text, True, self.colors['text'])
                choice_rect = choice_surf.get_rect(midleft=(popup_x + 100, popup_y + 200 + i * 40))
                self.screen.blit(choice_surf, choice_rect)
        
        # Instructions
        instructions = "Appuie sur A, B, C ou D pour répondre"
        instr_surf = self.fonts['small'].render(instructions, True, (200, 200, 100))
        instr_rect = instr_surf.get_rect(center=(self.width//2, popup_y + popup_height - 50))
        self.screen.blit(instr_surf, instr_rect)
    
    def draw_game_over(self, score, success=True):
        """Dessine l'écran de fin de jeu"""
        # Fond
        self.screen.fill((20, 20, 40))
        
        # Titre
        if success:
            title = self.fonts['title'].render("FÉLICITATIONS !", True, (100, 255, 100))
            message = "Diplôme obtenu avec succès !"
        else:
            title = self.fonts['title'].render("GAME OVER", True, (255, 100, 100))
            message = "Tu as rencontré trop de pièges..."
        
        title_rect = title.get_rect(center=(self.width//2, 100))
        self.screen.blit(title, title_rect)
        
        # Message
        msg_surf = self.fonts['normal'].render(message, True, self.colors['text'])
        msg_rect = msg_surf.get_rect(center=(self.width//2, 180))
        self.screen.blit(msg_surf, msg_rect)
        
        # Score
        score_text = f"Score final: {score}"
        score_surf = self.fonts['title'].render(score_text, True, (255, 255, 100))
        score_rect = score_surf.get_rect(center=(self.width//2, 280))
        self.screen.blit(score_surf, score_rect)
        
        # Boutons
        button_width = 200
        button_height = 60
        button_y = 400
        
        # Bouton Recommencer
        restart_rect = pygame.Rect(self.width//2 - button_width - 20, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, self.colors['button'], restart_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), restart_rect, 2, border_radius=10)
        restart_text = self.fonts['normal'].render("RECOMMENCER", True, self.colors['text'])
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Bouton Quitter
        quit_rect = pygame.Rect(self.width//2 + 20, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, (200, 80, 80), quit_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), quit_rect, 2, border_radius=10)
        quit_text = self.fonts['normal'].render("QUITTER", True, self.colors['text'])
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        return restart_rect, quit_rect
    
    def wrap_text(self, text, font, max_width):
        """Retourne le texte sur plusieurs lignes pour qu'il rentre dans max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width, _ = font.size(test_line)
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def update(self):
        """Met à jour l'affichage"""
        pygame.display.flip()
    
    def handle_events(self):
        """Gère les événements PyGame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                return 'quit'
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    return 'quit'
                
                # DÉPLACEMENTS
                elif event.key in (K_z, K_UP):
                    return 'up'
                elif event.key in (K_q, K_LEFT):
                    return 'left'
                elif event.key in (K_s, K_DOWN):
                    return 'down'
                elif event.key in (K_d, K_RIGHT):
                    return 'right'
                
                # AUTRES CONTROLES
                elif event.key == K_SPACE:
                    return 'space'
                elif event.key == K_r:
                    return 'restart'
                
                # RÉPONSES (minuscules !)
                elif event.key == K_a:
                    return 'a'
                elif event.key == K_b:
                    return 'b'
                elif event.key == K_c:
                    return 'c'
                elif event.key == K_d:
                    return 'd'
            
            elif event.type == MOUSEBUTTONDOWN:
                return ('click', event.pos)
        
        return None
    
    def quit(self):
        """Quitte PyGame proprement"""
        pygame.quit()
        sys.exit()