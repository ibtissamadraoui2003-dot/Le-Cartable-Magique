# test_agent.py
"""
Test rapide de l'agent Q-Learning
"""

from environment import SchoolEnvironment
from agent import QLearningAgent

def quick_test():
    """Test rapide de l'agent"""
    print("🧪 TEST RAPIDE Q-LEARNING")
    
    # Créer environnement et agent
    env = SchoolEnvironment()
    agent = QLearningAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_size(),
        learning_rate=0.1,
        discount_factor=0.9
    )
    
    # Test de base
    state = env.reset()
    print(f"État initial: {state}")
    
    # L'agent choisit une action (exploration à 100% donc aléatoire)
    action = agent.choose_action(state)
    action_names = ["Haut", "Bas", "Gauche", "Droite"]
    print(f"Action choisie: {action_names[action]} ({action})")
    
    # Exécute l'action
    next_state, reward, done, info = env.step(action)
    print(f"Nouvel état: {next_state}")
    print(f"Récompense: {reward}")
    print(f"Terminé: {done}")
    
    # L'agent apprend
    agent.learn(state, action, reward, next_state, done)
    print("\n✅ Agent a appris de l'expérience!")
    
    # Afficher un peu de Q-table
    print("\nÉtat de la Q-table après un pas:")
    agent.print_q_table_sample(num_samples=2)

if __name__ == "__main__":
    quick_test()
    input("\nAppuyez sur Entrée pour quitter...")