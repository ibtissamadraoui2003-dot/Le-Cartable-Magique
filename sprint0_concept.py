# sprint0_concept.py
"""
Ce fichier est juste un brouillon pour tester nos idées.
On ne code pas encore l'environnement RL proprement.
"""

# 1. La carte du monde (notre labyrinthe 5x5)
world_map = [
    [1, 1, 1, 1, 1],
    [1, 0, 2, 0, 3],
    [1, 1, 0, 1, 1],
    [1, 2, 0, 2, 1],
    [1, 1, 1, 1, 1]
]

# 2. Les questions associées aux positions (ligne, colonne)
questions_db = {
    (1, 2): {"question": "2 + 2 = ?", "answer": "4", "answered": False},
    (3, 1): {"question": "Capitale de la France ?", "answer": "Paris", "answered": False},
    (3, 3): {"question": "L'homme est un mammifère. Vrai ou faux ?", "answer": "Vrai", "answered": False}
}

# 3. Position initiale de l'agent
agent_pos = [3, 2]  # Ligne 1, Colonne 1 (attention, index commence à 0)

# 4. Afficher la carte
def print_map():
    for i in range(len(world_map)):
        for j in range(len(world_map[i])):
            if [i, j] == agent_pos:
                print("A", end=" ")  # A pour Agent
            else:
                # Convertir les nombres en symboles
                if world_map[i][j] == 0:
                    print(".", end=" ")
                elif world_map[i][j] == 1:
                    print("#", end=" ")
                elif world_map[i][j] == 2:
                    print("Q", end=" ")
                elif world_map[i][j] == 3:
                    print(">", end=" ")
        print()  # Nouvelle ligne

# 5. Simuler un mouvement simple
def move(direction):
    """Direction: 0=haut, 1=bas, 2=gauche, 3=droite"""
    new_pos = agent_pos.copy()
    
    if direction == 0:    new_pos[0] -= 1
    elif direction == 1:  new_pos[0] += 1
    elif direction == 2:  new_pos[1] -= 1
    elif direction == 3:  new_pos[1] += 1
    
    # Vérifier les murs
    if world_map[new_pos[0]][new_pos[1]] == 1:
        print("Ouch ! Mur. Récompense = -2")
        return -2, False  # Récompense, épisode terminé ?
    
    # Si c'est valide, mettre à jour la position
    agent_pos[0], agent_pos[1] = new_pos
    
    # Vérifier le type de case
    cell_type = world_map[new_pos[0]][new_pos[1]]
    
    if cell_type == 0:
        print("Déplacement. Récompense = -1")
        return -1, False
    elif cell_type == 2:
        print("Vous êtes dans une salle de question !")
        # Vérifier si la question a déjà été répondue
        pos_tuple = (new_pos[0], new_pos[1])
        if questions_db[pos_tuple]["answered"]:
            print("Question déjà répondue. Récompense = 0")
            return 0, False
        else:
            # Simuler une réponse (pour l'instant, toujours correcte)
            print(f"Question: {questions_db[pos_tuple]['question']}")
            # Dans la vraie version, on demanderait à l'utilisateur ou à l'agent
            questions_db[pos_tuple]["answered"] = True
            print("Bonne réponse ! Récompense = +10")
            return 10, False
    elif cell_type == 3:
        print("Félicitations ! Diplôme obtenu ! Récompense = +100")
        return 100, True  # Épisode terminé
    
    return 0, False

# 6. Test manuel de notre concept
print("=== TEST DU CONCEPT - LE CARTABLE MAGIQUE ===")
print("Carte initiale :")
print_map()

print("\n--- Simulation de mouvement ---")
print("1. On va à droite (vers la question)...")
reward, done = move(3)  # Droite
print_map()
print(f"Récompense: {reward}, Épisode terminé: {done}")

print("\n2. On répond à la question (automatique pour ce test)...")
# La réponse a déjà été traitée dans move() car on est sur une case 2
print_map()

print("\n3. On va à droite deux fois (vers la sortie)...")
reward1, done1 = move(3)  # Droite vers case vide
reward2, done2 = move(3)  # Droite vers la sortie
print_map()
print(f"Récompense finale: {reward2}, Épisode terminé: {done2}")

print("\n=== RÉSUMÉ DU CONCEPT ===")
print("✅ Carte définie (5x5 avec murs, questions, sortie)")
print("✅ Logique de mouvement et collisions")
print("✅ Système de questions/réponses simplifié")
print("✅ Récompenses définies pour chaque cas")
print("\nProchaine étape (Sprint 1): Coder cela dans une classe Environment propre!")