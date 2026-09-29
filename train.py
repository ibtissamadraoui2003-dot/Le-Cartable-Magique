# train.py
"""
Sprint 2 : Entraînement de l'agent Q-Learning
"""

import numpy as np
import time
import matplotlib.pyplot as plt
from environment import SchoolEnvironment
from agent import QLearningAgent

def train_agent(episodes=500, max_steps=100, render_every=100, save_every=100):
    """
    Entraîne l'agent Q-Learning
    
    Args:
        episodes: Nombre d'épisodes d'entraînement
        max_steps: Nombre maximum de pas par épisode
        render_every: Affiche l'environnement tous les N épisodes
        save_every: Sauvegarde l'agent tous les N épisodes
    """
    print("=" * 60)
    print("        ENTRAÎNEMENT Q-LEARNING")
    print("=" * 60)
    
    # Créer l'environnement et l'agent
    env = SchoolEnvironment()
    agent = QLearningAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_size(),
        learning_rate=0.1,      # α: vitesse d'apprentissage
        discount_factor=0.9,    # γ: importance du futur
        exploration_rate=1.0,   # ε: exploration initiale (100%)
        exploration_decay=0.995,# Réduction d'exploration
        min_exploration_rate=0.01  # Exploration minimale (1%)
    )
    
    print(f"🎯 Paramètres d'entraînement:")
    print(f"   - Épisodes: {episodes}")
    print(f"   - Pas maximum par épisode: {max_steps}")
    print(f"   - Taux d'apprentissage (α): {agent.learning_rate}")
    print(f"   - Facteur de discount (γ): {agent.discount_factor}")
    print(f"   - Exploration initiale (ε): {agent.exploration_rate}")
    print()
    
    # Statistiques
    stats = {
        'rewards': [],
        'steps': [],
        'exploration_rates': []
    }
    
    # Boucle d'entraînement
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        steps = 0
        
        # Afficher périodiquement
        if episode % render_every == 0 and episode > 0:
            print(f"\n📈 Épisode {episode}:")
            print(f"   Exploration rate: {agent.exploration_rate:.4f}")
            print(f"   Récompense moyenne (100 derniers): {np.mean(stats['rewards'][-100:]):.2f}")
        
        # Un épisode complet
        while not done and steps < max_steps:
            # L'agent choisit une action
            action = agent.choose_action(state, training=True)
            
            # Exécute l'action dans l'environnement
            next_state, reward, done, info = env.step(action)
            
            # L'agent apprend de l'expérience
            agent.learn(state, action, reward, next_state, done)
            
            # Mettre à jour les statistiques
            state = next_state
            total_reward += reward
            steps += 1
            
            # Afficher les premiers épisodes pour comprendre
            if episode < 3 and steps % 5 == 0:
                print(f"   Épisode {episode}, Step {steps}:")
                print(f"     État: {state}, Action: {action}, Récompense: {reward:.1f}")
                if 'message' in info:
                    print(f"     Info: {info['message']}")
        
        # Sauvegarde périodique
        if episode % save_every == 0 and episode > 0:
            agent.save(f"q_agent_episode_{episode}.pkl")
        
        # Mettre à jour les taux après chaque épisode
        agent.update_exploration_rate()
        
        # Enregistrer les statistiques
        stats['rewards'].append(total_reward)
        stats['steps'].append(steps)
        stats['exploration_rates'].append(agent.exploration_rate)
        
        # Afficher les résultats de l'épisode
        if episode % 50 == 0 or episode == episodes - 1:
            print(f"Épisode {episode:4d} | "
                  f"Récompense: {total_reward:7.1f} | "
                  f"Steps: {steps:3d} | "
                  f"ε: {agent.exploration_rate:.4f}")
    
    # Sauvegarde finale
    agent.save("q_agent_final.pkl")
    
    print("\n✅ Entraînement terminé !")
    print(f"📊 Statistiques finales:")
    stats_data = agent.get_stats()
    for key, value in stats_data.items():
        print(f"   {key}: {value}")
    
    return agent, stats

def plot_training_results(stats):
    """Affiche les graphiques des résultats d'entraînement"""
    
    # Créer une figure avec 3 sous-graphiques
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # 1. Récompenses par épisode
    axes[0, 0].plot(stats['rewards'], alpha=0.6, linewidth=0.8)
    axes[0, 0].set_title('Récompense par Épisode')
    axes[0, 0].set_xlabel('Épisode')
    axes[0, 0].set_ylabel('Récompense Totale')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Moyenne glissante sur 100 épisodes
    window_size = 100
    if len(stats['rewards']) > window_size:
        moving_avg = np.convolve(stats['rewards'], np.ones(window_size)/window_size, mode='valid')
        axes[0, 0].plot(range(window_size-1, len(stats['rewards'])), moving_avg, 
                       'r-', linewidth=2, label=f'Moyenne {window_size} épisodes')
        axes[0, 0].legend()
    
    # 2. Nombre de pas par épisode
    axes[0, 1].plot(stats['steps'], alpha=0.6, linewidth=0.8, color='green')
    axes[0, 1].set_title('Pas par Épisode')
    axes[0, 1].set_xlabel('Épisode')
    axes[0, 1].set_ylabel('Nombre de Pas')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Taux d'exploration
    axes[1, 0].plot(stats['exploration_rates'], alpha=0.8, linewidth=1.5, color='orange')
    axes[1, 0].set_title('Taux d\'Exploration (ε)')
    axes[1, 0].set_xlabel('Épisode')
    axes[1, 0].set_ylabel('Taux d\'Exploration')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Histogramme des récompenses
    axes[1, 1].hist(stats['rewards'], bins=50, alpha=0.7, color='purple', edgecolor='black')
    axes[1, 1].set_title('Distribution des Récompenses')
    axes[1, 1].set_xlabel('Récompense')
    axes[1, 1].set_ylabel('Fréquence')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Résultats d\'Entraînement - Q-Learning', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('training_results.png', dpi=100)
    print("📈 Graphiques sauvegardés dans 'training_results.png'")
    plt.show()

def demo_agent(agent_filename="q_agent_final.pkl", num_episodes=3):
    """Démonstration de l'agent entraîné"""
    print("\n" + "=" * 60)
    print("        DÉMONSTRATION DE L'AGENT")
    print("=" * 60)
    
    env = SchoolEnvironment()
    agent = QLearningAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_size()
    )
    
    # Charger l'agent entraîné
    if not agent.load(agent_filename):
        print("❌ Impossible de charger l'agent. Entraîne d'abord !")
        return
    
    print(f"✅ Agent chargé depuis {agent_filename}")
    print(f"📊 Exploration rate: {agent.exploration_rate:.4f}")
    
    for episode in range(num_episodes):
        print(f"\n🎬 DÉMO - Épisode {episode + 1}")
        print("-" * 40)
        
        state = env.reset()
        total_reward = 0
        done = False
        step = 0
        
        env.render()
        
        while not done and step < 50:
            # L'agent choisit une action (sans exploration)
            action = agent.choose_action(state, training=False)
            
            # Exécute l'action
            next_state, reward, done, info = env.step(action)
            
            # Afficher les détails
            action_names = ["Haut", "Bas", "Gauche", "Droite"]
            print(f"\nStep {step}:")
            print(f"  État: {state} → Action: {action_names[action]} → Récompense: {reward:.1f}")
            if 'message' in info and info['message']:
                print(f"  Info: {info['message']}")
            
            env.render()
            
            # Mettre à jour
            state = next_state
            total_reward += reward
            step += 1
            
            # Petite pause pour voir
            time.sleep(0.5)
            
            if done:
                print(f"\n🎉 Épisode terminé en {step} pas !")
                print(f"🏆 Récompense totale: {total_reward:.1f}")
                break
        
        if not done:
            print(f"\n⏰ Épisode interrompu après {step} pas")
            print(f"📊 Récompense totale: {total_reward:.1f}")
    
    # Afficher un échantillon de la Q-table
    agent.print_q_table_sample(num_samples=3)

if __name__ == "__main__":
    # Menu principal
    print("🤖 MENU PRINCIPAL - AGENT Q-LEARNING")
    print("1. Entraîner un nouvel agent")
    print("2. Démonstration avec agent existant")
    print("3. Entraîner + graphiques")
    
    choice = input("\nChoisis une option (1, 2 ou 3): ").strip()
    
    if choice == "1":
        # Entraînement simple
        episodes = int(input("Nombre d'épisodes (défaut: 500): ") or "500")
        agent, stats = train_agent(episodes=episodes)
        
        # Demander si on veut voir la démo
        if input("\nVoir la démonstration? (o/n): ").lower() == 'o':
            demo_agent()
            
    elif choice == "2":
        # Démonstration seulement
        demo_agent()
        
    elif choice == "3":
        # Entraînement avec graphiques
        episodes = int(input("Nombre d'épisodes (défaut: 1000): ") or "1000")
        agent, stats = train_agent(episodes=episodes)
        plot_training_results(stats)
        
        if input("\nVoir la démonstration? (o/n): ").lower() == 'o':
            demo_agent()
    else:
        print("Option invalide. Exécution par défaut...")
        agent, stats = train_agent(episodes=500)
        plot_training_results(stats)