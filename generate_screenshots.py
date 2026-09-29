import os

import pygame

from game_ui import GameUI


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_surface(surface, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    pygame.image.save(surface, path)
    print(f"Saved: {path}")


def draw_menu_screenshot(ui):
    screen = ui.screen
    screen.fill(ui.colors['background'])

    title = ui.fonts['title'].render("LE CARTABLE MAGIQUE", True, ui.colors['text'])
    screen.blit(title, title.get_rect(center=(ui.width // 2, 80)))

    subtitle = ui.fonts['normal'].render("Jeu éducatif en Python / PyGame", True, (200, 220, 255))
    screen.blit(subtitle, subtitle.get_rect(center=(ui.width // 2, 130)))

    menu_items = [
        "Mode Humain",
        "Mode IA Simple",
        "Mode IA RL",
        "Entraîner IA RL",
        "Quitter",
    ]

    start_y = 220
    for index, label in enumerate(menu_items):
        button_rect = pygame.Rect(ui.width // 2 - 180, start_y + index * 70, 360, 46)
        color = ui.colors['button_hover'] if index == 0 else ui.colors['button']
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=10)

        text = ui.fonts['normal'].render(label, True, ui.colors['text'])
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

    footer = ui.fonts['small'].render("ZQSD / flèches pour bouger • A/B/C/D pour répondre", True, (180, 220, 180))
    footer_rect = footer.get_rect(center=(ui.width // 2, ui.height - 35))
    screen.blit(footer, footer_rect)

    pygame.display.flip()
    save_surface(screen, "menu.png")


def draw_gameplay_screenshot(ui):
    world_map = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        [1, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
        [1, 2, 0, 0, 0, 2, 0, 0, 0, 0, 2, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    questions_status = {(1, 3): False, (1, 7): True, (3, 1): False, (5, 3): False, (7, 1): False, (7, 5): True, (9, 6): False, (10, 10): False}
    traps = {(2, 5), (6, 1), (8, 10)}
    bonuses = {(4, 8), (8, 4), (10, 1)}
    agent_pos = [5, 2]

    ui.draw_grid(world_map, agent_pos, questions_status, traps, bonuses)
    ui.draw_side_panel(score=240, steps=14, level=1, remaining_questions=6)
    ui.draw_active_effects({
        'speed': {'type': 'speed', 'duration': 2},
        'confusion': {'type': 'confusion', 'duration': 3},
    })
    pygame.display.flip()
    save_surface(ui.screen, "gameplay.png")


def main():
    pygame.init()
    ui = GameUI(grid_size=12, cell_size=50)
    draw_menu_screenshot(ui)
    draw_gameplay_screenshot(ui)
    pygame.quit()


if __name__ == "__main__":
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    main()
