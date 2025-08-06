import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Constantes du jeu
LARGEUR = 900
HAUTEUR = 700
TAILLE_CASE = 25
FPS_INITIAL = 8

# Couleurs améliorées
NOIR = (15, 15, 25)
VERT_TETE = (50, 255, 50)
VERT_CORPS = (30, 200, 30)
VERT_FONCE = (20, 150, 20)
ROUGE = (255, 50, 50)
ROUGE_SPECIAL = (255, 100, 255)
BLANC = (255, 255, 255)
JAUNE = (255, 255, 100)
BLEU = (100, 150, 255)
GRIS = (100, 100, 100)
OR = (255, 215, 0)

class Particule:
    def __init__(self, x, y, couleur):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.couleur = couleur
        self.vie = 30
        self.taille = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 1
        self.taille = max(1, self.taille - 0.1)
    
    def dessiner(self, ecran):
        if self.vie > 0:
            alpha = max(0, min(255, self.vie * 8))
            couleur_avec_alpha = (*self.couleur, alpha)
            pygame.draw.circle(ecran, self.couleur, (int(self.x), int(self.y)), int(self.taille))

class NourritureSpeciale:
    def __init__(self):
        self.position = self.nouvelle_position()
        self.temps_vie = 300  # 30 secondes à 10 FPS
        self.points = 50
        self.effet = random.choice(['vitesse', 'score_double', 'invincible'])
        self.pulse = 0
    
    def nouvelle_position(self):
        x = random.randint(0, (LARGEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        y = random.randint(0, (HAUTEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        return (x, y)
    
    def update(self):
        self.temps_vie -= 1
        self.pulse += 0.2
        return self.temps_vie > 0
    
    def dessiner(self, ecran):
        # Effet de pulsation
        taille_pulse = int(TAILLE_CASE + math.sin(self.pulse) * 3)
        couleur = ROUGE_SPECIAL if self.effet == 'invincible' else JAUNE if self.effet == 'score_double' else BLEU
        
        pygame.draw.rect(ecran, couleur, 
                        (self.position[0] - (taille_pulse - TAILLE_CASE)//2, 
                         self.position[1] - (taille_pulse - TAILLE_CASE)//2, 
                         taille_pulse, taille_pulse))
        
        # Bordure brillante
        pygame.draw.rect(ecran, BLANC, 
                        (self.position[0] - (taille_pulse - TAILLE_CASE)//2, 
                         self.position[1] - (taille_pulse - TAILLE_CASE)//2, 
                         taille_pulse, taille_pulse), 2)

class Snake:
    def __init__(self):
        self.corps = [(LARGEUR//2, HAUTEUR//2)]
        self.direction = (TAILLE_CASE, 0)
        self.croissance = False
        self.invincible = 0
        self.score_double = 0
        self.vitesse_boost = 0
        self.trail = []  # Traînée du serpent
        
    def bouger(self):
        tete = self.corps[0]
        nouvelle_tete = (tete[0] + self.direction[0], tete[1] + self.direction[1])
        
        # Ajouter à la traînée
        self.trail.append(tete)
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Gestion des bordures
        nouvelle_tete = (nouvelle_tete[0] % LARGEUR, nouvelle_tete[1] % HAUTEUR)
        
        self.corps.insert(0, nouvelle_tete)
        
        if not self.croissance:
            self.corps.pop()
        else:
            self.croissance = False
        
        # Décrémenter les effets spéciaux
        if self.invincible > 0:
            self.invincible -= 1
        if self.score_double > 0:
            self.score_double -= 1
        if self.vitesse_boost > 0:
            self.vitesse_boost -= 1
    
    def changer_direction(self, nouvelle_direction):
        if (nouvelle_direction[0] * -1, nouvelle_direction[1] * -1) != self.direction:
            self.direction = nouvelle_direction
    
    def grandir(self):
        self.croissance = True
    
    def collision_avec_soi(self):
        if self.invincible > 0:
            return False
        return self.corps[0] in self.corps[3:]  # Évite collision immédiate
    
    def appliquer_effet(self, effet):
        if effet == 'vitesse':
            self.vitesse_boost = 150
        elif effet == 'score_double':
            self.score_double = 200
        elif effet == 'invincible':
            self.invincible = 100
    
    def dessiner(self, ecran):
        # Dessiner la traînée
        for i, pos in enumerate(self.trail):
            alpha = (i / len(self.trail)) * 50
            couleur_trail = (30, 150, 30, int(alpha))
            pygame.draw.circle(ecran, (30, 150, 30), 
                             (pos[0] + TAILLE_CASE//2, pos[1] + TAILLE_CASE//2), 
                             TAILLE_CASE//4)
        
        # Dessiner le corps
        for i, segment in enumerate(self.corps):
            if i == 0:  # Tête
                couleur = VERT_TETE
                if self.invincible > 0:
                    couleur = (255, 255, 255) if (self.invincible // 5) % 2 else VERT_TETE
                
                # Tête avec des yeux
                pygame.draw.rect(ecran, couleur, 
                               (segment[0], segment[1], TAILLE_CASE, TAILLE_CASE))
                
                # Yeux
                oeil_size = 4
                pygame.draw.circle(ecran, BLANC, 
                                 (segment[0] + 6, segment[1] + 6), oeil_size)
                pygame.draw.circle(ecran, BLANC, 
                                 (segment[0] + TAILLE_CASE - 6, segment[1] + 6), oeil_size)
                pygame.draw.circle(ecran, NOIR, 
                                 (segment[0] + 6, segment[1] + 6), 2)
                pygame.draw.circle(ecran, NOIR, 
                                 (segment[0] + TAILLE_CASE - 6, segment[1] + 6), 2)
            else:  # Corps
                # Gradient de couleur pour le corps
                intensite = max(0.3, 1 - (i / len(self.corps)) * 0.7)
                couleur = (int(VERT_CORPS[0] * intensite), 
                          int(VERT_CORPS[1] * intensite), 
                          int(VERT_CORPS[2] * intensite))
                
                pygame.draw.rect(ecran, couleur, 
                               (segment[0], segment[1], TAILLE_CASE, TAILLE_CASE))
                
                # Bordure
                pygame.draw.rect(ecran, VERT_FONCE, 
                               (segment[0], segment[1], TAILLE_CASE, TAILLE_CASE), 1)

class Nourriture:
    def __init__(self):
        self.position = self.nouvelle_position()
        self.animation = 0
    
    def nouvelle_position(self):
        x = random.randint(0, (LARGEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        y = random.randint(0, (HAUTEUR - TAILLE_CASE) // TAILLE_CASE) * TAILLE_CASE
        return (x, y)
    
    def update(self):
        self.animation += 0.1
    
    def dessiner(self, ecran):
        # Animation de pulsation
        taille = TAILLE_CASE + int(math.sin(self.animation) * 2)
        offset = (TAILLE_CASE - taille) // 2
        
        pygame.draw.rect(ecran, ROUGE, 
                        (self.position[0] + offset, self.position[1] + offset, taille, taille))
        
        # Reflet
        pygame.draw.rect(ecran, (255, 150, 150), 
                        (self.position[0] + offset + 2, self.position[1] + offset + 2, 
                         taille//3, taille//3))

class Jeu:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("🐍 Snake Edition")
        self.horloge = pygame.time.Clock()
        self.snake = Snake()
        self.nourriture = Nourriture()
        self.nourriture_speciale = None
        self.score = 0
        self.meilleur_score = self.charger_meilleur_score()
        self.niveau = 1
        self.fps = FPS_INITIAL
        self.particules = []
        
        # Polices
        self.police_titre = pygame.font.Font(None, 48)
        self.police_score = pygame.font.Font(None, 32)
        self.police_info = pygame.font.Font(None, 24)
        
        self.jeu_termine = False
        self.pause = False
        self.temps_jeu = 0
        
        # État du menu
        self.etat = "menu"  # "menu", "jeu", "fin"
    
    def charger_meilleur_score(self):
        try:
            with open("meilleur_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def sauvegarder_meilleur_score(self):
        if self.score > self.meilleur_score:
            self.meilleur_score = self.score
            try:
                with open("meilleur_score.txt", "w") as f:
                    f.write(str(self.meilleur_score))
            except:
                pass
    
    def creer_particules(self, x, y, couleur, nombre=8):
        for _ in range(nombre):
            self.particules.append(Particule(x, y, couleur))
    
    def gerer_evenements(self):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.sauvegarder_meilleur_score()
                return False
            elif evenement.type == pygame.KEYDOWN:
                if self.etat == "menu":
                    if evenement.key == pygame.K_SPACE:
                        self.etat = "jeu"
                        self.recommencer()
                elif self.etat == "jeu":
                    if evenement.key == pygame.K_UP:
                        self.snake.changer_direction((0, -TAILLE_CASE))
                    elif evenement.key == pygame.K_DOWN:
                        self.snake.changer_direction((0, TAILLE_CASE))
                    elif evenement.key == pygame.K_LEFT:
                        self.snake.changer_direction((-TAILLE_CASE, 0))
                    elif evenement.key == pygame.K_RIGHT:
                        self.snake.changer_direction((TAILLE_CASE, 0))
                    elif evenement.key == pygame.K_p:
                        self.pause = not self.pause
                elif self.etat == "fin":
                    if evenement.key == pygame.K_r:
                        self.etat = "jeu"
                        self.recommencer()
                    elif evenement.key == pygame.K_m:
                        self.etat = "menu"
        return True
    
    def mettre_a_jour(self):
        if self.etat != "jeu" or self.pause or self.jeu_termine:
            return
        
        self.temps_jeu += 1
        
        # Mise à jour des particules
        self.particules = [p for p in self.particules if p.vie > 0]
        for particule in self.particules:
            particule.update()
        
        # Mise à jour des animations
        self.nourriture.update()
        
        # Gérer la vitesse selon les effets
        fps_actuel = self.fps + (5 if self.snake.vitesse_boost > 0 else 0)
        
        if self.temps_jeu % max(1, FPS_INITIAL - (fps_actuel - FPS_INITIAL)) == 0:
            self.snake.bouger()
            
            # Vérifier collision avec la nourriture normale
            if self.snake.corps[0] == self.nourriture.position:
                self.snake.grandir()
                points = 10 * (2 if self.snake.score_double > 0 else 1)
                self.score += points
                
                # Créer particules
                self.creer_particules(self.nourriture.position[0] + TAILLE_CASE//2, 
                                    self.nourriture.position[1] + TAILLE_CASE//2, ROUGE)
                
                # Nouvelle nourriture
                while True:
                    self.nourriture.position = self.nourriture.nouvelle_position()
                    if (self.nourriture.position not in self.snake.corps and 
                        (not self.nourriture_speciale or self.nourriture.position != self.nourriture_speciale.position)):
                        break
                
                # Augmenter le niveau et la vitesse
                if self.score > 0 and self.score % 100 == 0:
                    self.niveau += 1
                    self.fps = min(20, FPS_INITIAL + self.niveau)
                
                # Chance de créer nourriture spéciale
                if random.random() < 0.15 and not self.nourriture_speciale:
                    self.nourriture_speciale = NourritureSpeciale()
            
            # Vérifier collision avec nourriture spéciale
            if (self.nourriture_speciale and 
                self.snake.corps[0] == self.nourriture_speciale.position):
                
                points = self.nourriture_speciale.points * (2 if self.snake.score_double > 0 else 1)
                self.score += points
                self.snake.appliquer_effet(self.nourriture_speciale.effet)
                
                # Particules spéciales
                couleur = JAUNE if self.nourriture_speciale.effet == 'score_double' else BLEU
                self.creer_particules(self.nourriture_speciale.position[0] + TAILLE_CASE//2,
                                    self.nourriture_speciale.position[1] + TAILLE_CASE//2, 
                                    couleur, 15)
                
                self.nourriture_speciale = None
            
            # Mise à jour nourriture spéciale
            if self.nourriture_speciale and not self.nourriture_speciale.update():
                self.nourriture_speciale = None
            
            # Vérifier collision avec soi-même
            if self.snake.collision_avec_soi():
                self.jeu_termine = True
                self.etat = "fin"
                self.sauvegarder_meilleur_score()
    
    def dessiner_menu(self):
        self.ecran.fill(NOIR)
        
        # Titre avec effet
        titre = self.police_titre.render("SNAKE GAME", True, VERT_TETE)
        rect_titre = titre.get_rect(center=(LARGEUR//2, HAUTEUR//3))
        self.ecran.blit(titre, rect_titre)
        
        # Instructions
        textes = [
            "Utilisez les flèches pour diriger le serpent",
            "Mangez la nourriture rouge pour grandir",
            "Collectez les bonus spéciaux pour des effets !",
            "",
            f"Meilleur score: {self.meilleur_score}",
            "",
            "Appuyez sur ESPACE pour commencer"
        ]
        
        y = HAUTEUR//2
        for texte in textes:
            if texte:
                surface = self.police_info.render(texte, True, BLANC)
                rect = surface.get_rect(center=(LARGEUR//2, y))
                self.ecran.blit(surface, rect)
            y += 30
    
    def dessiner_jeu(self):
        self.ecran.fill(NOIR)
        
        # Dessiner les particules
        for particule in self.particules:
            particule.dessiner(self.ecran)
        
        if not self.jeu_termine:
            self.snake.dessiner(self.ecran)
            self.nourriture.dessiner(self.ecran)
            if self.nourriture_speciale:
                self.nourriture_speciale.dessiner(self.ecran)
        
        # Interface utilisateur améliorée
        # Score
        texte_score = self.police_score.render(f"Score: {self.score}", True, BLANC)
        self.ecran.blit(texte_score, (10, 10))
        
        # Niveau
        texte_niveau = self.police_info.render(f"Niveau: {self.niveau}", True, BLANC)
        self.ecran.blit(texte_niveau, (10, 45))
        
        # Meilleur score
        texte_meilleur = self.police_info.render(f"Record: {self.meilleur_score}", True, OR)
        self.ecran.blit(texte_meilleur, (10, 70))
        
        # Effets actifs
        y_effet = 100
        if self.snake.invincible > 0:
            texte = self.police_info.render(f"Invincible: {self.snake.invincible//10}s", True, ROUGE_SPECIAL)
            self.ecran.blit(texte, (10, y_effet))
            y_effet += 25
        
        if self.snake.score_double > 0:
            texte = self.police_info.render(f"Score x2: {self.snake.score_double//10}s", True, JAUNE)
            self.ecran.blit(texte, (10, y_effet))
            y_effet += 25
        
        if self.snake.vitesse_boost > 0:
            texte = self.police_info.render(f"Vitesse+: {self.snake.vitesse_boost//10}s", True, BLEU)
            self.ecran.blit(texte, (10, y_effet))
        
        # Pause
        if self.pause:
            texte_pause = self.police_titre.render("PAUSE", True, BLANC)
            rect_pause = texte_pause.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            self.ecran.blit(texte_pause, rect_pause)
    
    def dessiner_fin(self):
        self.ecran.fill(NOIR)
        
        # Message de fin
        texte_fin = self.police_titre.render("GAME OVER!", True, ROUGE)
        rect_fin = texte_fin.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 80))
        self.ecran.blit(texte_fin, rect_fin)
        
        # Score final
        texte_score = self.police_score.render(f"Score final: {self.score}", True, BLANC)
        rect_score = texte_score.get_rect(center=(LARGEUR//2, HAUTEUR//2 - 30))
        self.ecran.blit(texte_score, rect_score)
        
        # Nouveau record ?
        if self.score == self.meilleur_score and self.score > 0:
            texte_record = self.police_score.render("NOUVEAU RECORD !", True, OR)
            rect_record = texte_record.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 10))
            self.ecran.blit(texte_record, rect_record)
        
        # Instructions
        texte_recommencer = self.police_info.render("R - Recommencer  |  M - Menu", True, BLANC)
        rect_recommencer = texte_recommencer.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 60))
        self.ecran.blit(texte_recommencer, rect_recommencer)
    
    def dessiner(self):
        if self.etat == "menu":
            self.dessiner_menu()
        elif self.etat == "jeu":
            self.dessiner_jeu()
        elif self.etat == "fin":
            self.dessiner_fin()
        
        pygame.display.flip()
    
    def recommencer(self):
        self.snake = Snake()
        self.nourriture = Nourriture()
        self.nourriture_speciale = None
        self.score = 0
        self.niveau = 1
        self.fps = FPS_INITIAL
        self.jeu_termine = False
        self.pause = False
        self.temps_jeu = 0
        self.particules = []
    
    def executer(self):
        en_cours = True
        while en_cours:
            en_cours = self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(60)  # 60 FPS pour l'affichage
        
        pygame.quit()
        sys.exit()

# Lancer le jeu
if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()