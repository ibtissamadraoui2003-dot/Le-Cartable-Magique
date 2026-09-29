# test_env.py
"""
Test de notre environnement RL
"""

from environment import SchoolEnvironment
import time

def test_environment():
    """Test manuel de l'environnement"""
    
    print("🎒 Initialisation de l'environnement 'Le Cartable Magique'...")
    env = SchoolEnvironment()
    
    print("\n=== ÉTAT INITIAL ===")
    env.render()
    
    print("\n=== TEST 1: Déplacement vers une question ===")
    # Action 3 = droite
    state, reward, done, info = env.step(3)
    print(f"État: {state}, Récompense: {reward}, Terminé: {done}")
    print(f"Info: {info}")
    env.render()
    
    time.sleep(1)  # Petite pause
    
    print("\n=== TEST 2: Répondre à la question (automatique) ===")
    # On est déjà sur la case question, donc l'action de déplacement
    # déclenche automatiquement la réponse
    state, reward, done, info = env.step(3)  # Droite vers case vide
    print(f"État: {state}, Récompense: {reward}, Terminé: {done}")
    print(f"Info: {info}")
    env.render()
    
    time.sleep(1)
    
    print("\n=== TEST 3: Aller vers la sortie ===")
    # Séquence: droite, droite (pour atteindre la sortie)
    actions = [3, 3]  # Droite, droite
    
    for i, action in enumerate(actions):
        print(f"\nAction {i+1}: {'droite'}")
        state, reward, done, info = env.step(action)
        print(f"État: {state}, Récompense: {reward}, Terminé: {done}")
        print(f"Info: {info}")
        env.render()
        
        if done:
            print("🎓 Diplôme obtenu avec succès!")
            break
            
        time.sleep(1)
    
    print("\n=== TEST 4: Réinitialisation ===")
    state = env.reset()
    print(f"État après reset: {state}")
    env.render()

def test_wall_collision():
    """Test des collisions avec les murs"""
    print("\n=== TEST COLLISION MUR ===")
    env = SchoolEnvironment()
    env.reset()
    
    print("Tentative d'aller vers le haut (devrait être un mur)...")
    state, reward, done, info = env.step(0)  # Haut
    print(f"Récompense: {reward} (devrait être -2)")
    print(f"Message: {info.get('message', '')}")
    env.render()

def run_manual_control():
    """Contrôle manuel pour tester l'environnement"""
    print("\n🎮 CONTRÔLE MANUEL")
    print("Actions: 0=Haut, 1=Bas, 2=Gauche, 3=Droite, q=Quitter")
    print("-" * 40)
    
    env = SchoolEnvironment()
    env.reset()
    env.render()
    
    while True:
        action_str = input("\nAction (0-3, q): ").strip().lower()
        
        if action_str == 'q':
            print("Au revoir!")
            break
            
        try:
            action = int(action_str)
            if action not in [0, 1, 2, 3]:
                print("Action invalide. Utilise 0, 1, 2, ou 3.")
                continue
                
            state, reward, done, info = env.step(action)
            print(f"Récompense: {reward}")
            print(f"Info: {info.get('message', '')}")
            env.render()
            
            if done:
                print("\n✨ Épisode terminé! Appuie sur Entrée pour recommencer.")
                input()
                env.reset()
                env.render()
                
        except ValueError:
            print("Entrée invalide. Utilise 0, 1, 2, 3, ou q.")

if __name__ == "__main__":
    print("=" * 50)
    print("TEST COMPLET DE L'ENVIRONNEMENT RL")
    print("=" * 50)
    
    # Exécuter les tests
    #test_environment()
    #test_wall_collision()
    
    # Décommenter la ligne suivante pour le contrôle manuel
    run_manual_control()