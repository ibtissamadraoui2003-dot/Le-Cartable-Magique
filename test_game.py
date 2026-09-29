#!/usr/bin/env python3
"""
Test simple du jeu PyGame
"""

import pygame
import sys

def main():
    print("🎮 Démarrage du jeu...")
    
    # Initialiser PyGame
    pygame.init()
    
    # Créer la fenêtre
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Le Cartable Magique - TEST")
    
    # Couleurs
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    
    # Police
    font = pygame.font.SysFont('Arial', 36)
    
    # Position de l'agent
    agent_x, agent_y = 400, 300
    agent_size = 50
    
    # Score
    score = 0
    running = True
    
    print("✅ Jeu initialisé. Utilise les flèches pour bouger, ESC pour quitter.")
    
    # Boucle principale
    while running:
        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    agent_y -= 10
                    score += 1
                elif event.key == pygame.K_DOWN:
                    agent_y += 10
                    score += 1
                elif event.key == pygame.K_LEFT:
                    agent_x -= 10
                    score += 1
                elif event.key == pygame.K_RIGHT:
                    agent_x += 10
                    score += 1
        
        # Remplir l'écran
        screen.fill(BLACK)
        
        # Dessiner l'agent
        pygame.draw.rect(screen, GREEN, (agent_x, agent_y, agent_size, agent_size))
        
        # Dessiner le score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Instructions
        instructions = font.render("Flèches: bouger | ESC: quitter", True, (255, 255, 0))
        screen.blit(instructions, (20, 550))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        
        # Limiter à 60 FPS
        pygame.time.Clock().tick(60)
    
    # Quitter
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()