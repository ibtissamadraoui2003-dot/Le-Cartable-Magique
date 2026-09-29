# questions_db.py
"""
Base de données de questions d'informatique
"""

import random

class QuestionDatabase:
    """Gère les questions d'informatique"""
    
    def __init__(self):
        self.questions = self.load_questions()
        self.used_questions = set()
    
    def load_questions(self):
        """Charge toutes les questions par catégorie et difficulté"""
        return {
            'easy': [
                {
                    'question': "Quel langage est principalement utilisé pour le style des pages web?",
                    'choices': ["HTML", "CSS", "JavaScript", "Python"],
                    'answer': 1,  # CSS
                    'category': 'Web'
                },
                {
                    'question': "Que signifie 'CPU'?",
                    'choices': ["Central Processing Unit", "Computer Personal Unit", "Central Power Unit", "Computer Processing Unit"],
                    'answer': 0,
                    'category': 'Hardware'
                },
                {
                    'question': "Quel est le système de numération utilisé par les ordinateurs?",
                    'choices': ["Décimal", "Binaire", "Hexadécimal", "Octal"],
                    'answer': 1,
                    'category': 'Fondamentaux'
                },
                {
                    'question': "Quel langage est souvent utilisé pour l'analyse de données?",
                    'choices': ["Java", "Python", "C++", "Ruby"],
                    'answer': 1,
                    'category': 'Programmation'
                },
                {
                    'question': "Que signifie 'RAM'?",
                    'choices': ["Random Access Memory", "Readily Available Memory", "Random Available Memory", "Read Access Memory"],
                    'answer': 0,
                    'category': 'Hardware'
                },
                {
                    'question': "Quel navigateur web est développé par Google?",
                    'choices': ["Firefox", "Safari", "Chrome", "Edge"],
                    'answer': 2,
                    'category': 'Web'
                },
                {
                    'question': "Quel système d'exploitation est open-source?",
                    'choices': ["Windows", "macOS", "Linux", "iOS"],
                    'answer': 2,
                    'category': 'OS'
                }
            ],
            'medium': [
                {
                    'question': "Quelle structure de données fonctionne sur le principe 'Last In, First Out' (LIFO)?",
                    'choices': ["File", "Pile", "Liste chaînée", "Arbre"],
                    'answer': 1,
                    'category': 'Structures de données'
                },
                {
                    'question': "Quel protocole est utilisé pour envoyer des emails?",
                    'choices': ["HTTP", "FTP", "SMTP", "TCP"],
                    'answer': 2,
                    'category': 'Réseaux'
                },
                {
                    'question': "Quelle est la complexité temporelle de la recherche binaire?",
                    'choices': ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                    'answer': 2,
                    'category': 'Algorithmes'
                },
                {
                    'question': "Quel paradigme de programmation utilise des 'objets'?",
                    'choices': ["Fonctionnel", "Impératif", "Oriente objet", "Logique"],
                    'answer': 2,
                    'category': 'Programmation'
                },
                {
                    'question': "Que signifie 'SQL'?",
                    'choices': ["Structured Query Language", "Simple Question Language", "System Query Logic", "Structured Question Logic"],
                    'answer': 0,
                    'category': 'Bases de données'
                },
                {
                    'question': "Quel langage est compilé en bytecode Java?",
                    'choices': ["Python", "C++", "JavaScript", "Java"],
                    'answer': 3,
                    'category': 'Programmation'
                }
            ],
            'hard': [
                {
                    'question': "Quel algorithme de tri a une complexité moyenne de O(n log n)?",
                    'choices': ["Tri à bulles", "Tri par insertion", "Tri rapide (QuickSort)", "Tri par sélection"],
                    'answer': 2,
                    'category': 'Algorithmes'
                },
                {
                    'question': "Quelle est la différence entre TCP et UDP?",
                    'choices': [
                        "TCP est non-connecté, UDP est connecté",
                        "TCP est fiable, UDP ne l'est pas",
                        "TCP est plus rapide que UDP",
                        "UDP utilise des ports, TCP non"
                    ],
                    'answer': 1,
                    'category': 'Réseaux'
                },
                {
                    'question': "Qu'est-ce qu'une injection SQL?",
                    'choices': [
                        "Une méthode d'optimisation de base de données",
                        "Une technique d'attaque exploitant des failles d'entrée",
                        "Un type de jointure en SQL",
                        "Une fonction de sauvegarde"
                    ],
                    'answer': 1,
                    'category': 'Sécurité'
                },
                {
                    'question': "Quelle est la différence entre une liste et un tuple en Python?",
                    'choices': [
                        "Les listes sont immutables, les tuples sont mutables",
                        "Les tuples sont immutables, les listes sont mutables",
                        "Il n'y a pas de différence",
                        "Les tuples sont plus rapides pour toutes les opérations"
                    ],
                    'answer': 1,
                    'category': 'Python'
                },
                {
                    'question': "Qu'est-ce que le polymorphisme en POO?",
                    'choices': [
                        "La capacité d'une classe à hériter d'une autre",
                        "La capacité d'un objet à prendre plusieurs formes",
                        "L'encapsulation des données",
                        "La création de multiples instances"
                    ],
                    'answer': 1,
                    'category': 'POO'
                },
                {
                    'question': "Qu'est-ce qu'un arbre binaire de recherche?",
                    'choices': [
                        "Un arbre où chaque nœud a au plus deux enfants",
                        "Un arbre trié où le sous-arbre gauche < racine < sous-arbre droit",
                        "Un arbre utilisé uniquement pour la recherche",
                        "Un arbre avec exactement deux enfants par nœud"
                    ],
                    'answer': 1,
                    'category': 'Structures de données'
                }
            ]
        }
    
    def get_random_question(self, difficulty='medium'):
        """Retourne une question aléatoire d'une difficulté donnée"""
        if difficulty not in self.questions:
            difficulty = 'medium'
        
        available_questions = [
            q for q in self.questions[difficulty] 
            if q['question'] not in self.used_questions
        ]
        
        if not available_questions:
            # Réutiliser les questions si toutes ont été utilisées
            self.used_questions.clear()
            available_questions = self.questions[difficulty]
        
        question = random.choice(available_questions)
        self.used_questions.add(question['question'])
        
        return question
    
    def check_answer(self, question, user_answer):
        """Vérifie si la réponse est correcte"""
        # Convertir la lettre (a, b, c, d) en index (0, 1, 2, 3)
        if isinstance(user_answer, str) and len(user_answer) == 1:
            user_index = ord(user_answer.lower()) - ord('a')
        else:
            user_index = user_answer
        
        return user_index == question['answer']
    
    def get_category_color(self, category):
        """Retourne une couleur selon la catégorie"""
        colors = {
            'Web': (255, 150, 50),
            'Hardware': (100, 200, 255),
            'Fondamentaux': (150, 255, 150),
            'Programmation': (255, 100, 255),
            'Structures de données': (255, 255, 100),
            'Réseaux': (100, 200, 200),
            'Algorithmes': (200, 100, 255),
            'Bases de données': (255, 200, 100),
            'Sécurité': (255, 100, 100),
            'Python': (50, 150, 255),
            'POO': (255, 150, 200),
            'OS': (150, 150, 255)
        }
        return colors.get(category, (200, 200, 200))