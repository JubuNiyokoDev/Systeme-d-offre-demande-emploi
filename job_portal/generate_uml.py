import os
import subprocess

def generate_diagrams():
    # Chemin vers votre plantuml.jar
    PLANTUML_JAR = "../plantuml.jar"  # Modifiez ce chemin selon l'emplacement de votre fichier
    
    # Créer le dossier diagrams s'il n'existe pas
    if not os.path.exists('diagrams'):
        os.makedirs('diagrams')
    
    # Liste des fichiers .puml à traiter
    diagrams = {
        'use_case': """
@startuml
actor "Candidat" as Candidate
actor "Recruteur" as Recruiter
actor "Admin" as Admin

rectangle "Système de Gestion d'Emploi" {
    usecase "S'inscrire" as UC1
    usecase "Se connecter" as UC2
    usecase "Consulter les offres" as UC3
    usecase "Postuler à une offre" as UC4
    usecase "Gérer son profil" as UC5
    usecase "Publier une offre" as UC6
    usecase "Gérer les candidatures" as UC7
    usecase "Bannir un utilisateur" as UC8
}

Candidate --> UC1
Candidate --> UC2
Candidate --> UC3
Candidate --> UC4
Candidate --> UC5

Recruiter --> UC1
Recruiter --> UC2
Recruiter --> UC5
Recruiter --> UC6
Recruiter --> UC7

Admin --> UC8
Admin --> UC3
@enduml
""",
        'class_diagram': """
@startuml
class CustomUser {
    - username: str
    - email: str
    - password: str
    - is_recruiter: bool
    - is_banned: bool
    + ban_user()
    + unban_user()
}

class JobOffer {
    - title: str
    - company: str
    - description: text
    - location: str
    - salary_range: int
    - status: str
    - created_at: datetime
    - expires_at: datetime
    + is_expired(): bool
    + has_user_applied(user): bool
}

class JobApplication {
    - status: str
    - applied_at: datetime
    - cover_letter: text
    + update_status(new_status)
}

CustomUser "1" -- "*" JobOffer : publishes >
CustomUser "1" -- "*" JobApplication : submits >
JobOffer "1" -- "*" JobApplication : receives >
@enduml
""",
        # Ajoutez les autres diagrammes ici...
    }
    
    # Générer chaque diagramme
    for name, content in diagrams.items():
        # Créer le fichier .puml temporaire
        puml_file = f"diagrams/{name}.puml"
        with open(puml_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Générer le PNG
        try:
            subprocess.run([
                'java',
                '-jar',
                PLANTUML_JAR,
                puml_file
            ], check=True)
            print(f"Diagramme généré : {name}.png")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la génération de {name}.png : {e}")

if __name__ == '__main__':
    generate_diagrams()