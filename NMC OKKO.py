import random
import time
import copy 
import numpy as np
import random
from numba import jit
import keyboard
import sys

class Joueur:
    def __init__(self, name, color, pos, status, direction):
        self.name = name
        self.color = color
        self.isAlive = True
        self.pos = pos
        self.status = status
        self.direction = direction
        self.paths = []
        
    def Dead(self):
        print(self.name, "Dead")
        self.isAlive = False
        self.pos = (0,0)
        
    def ResetPath(self, grille):
        for path in self.paths:
            grille[path[0]][path[1]] = 0

        self.paths = []
        

## fenetre d'affichage

import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
plt.ion()
plt.show()
fig,axes = plt.subplots(1,1)
fig.canvas.set_window_title('TRON')


#################################################################################
#
#  Parametres du jeu

LARGEUR = 13
HAUTEUR = 17
L = 20  # largeur d'une case du jeu en pixel
canvas = None   # zone de dessin
Grille = None   # grille du jeu
posJ1  = None   # position du joueur 1 (x,y)
NbPartie = 0   # Nombre de parties effectuées
Scores = [0 , 0]  # score de la partie / total des scores des differentes parties

def InitPartie():  
    global Grille, PosJ1, NbPartie, Joueurs
    
    NbPartie += 1
    Joueurs = []
    
    Grille = np.zeros((LARGEUR,HAUTEUR))
    for i in range(LARGEUR):
        Grille[i] = ([0] * HAUTEUR )
    
    # #positionne les murs de l'arene
    for x in range(LARGEUR):
       Grille[x][0] = 10
       Grille[x][HAUTEUR-1] = 10
       
    for y in range(HAUTEUR):
       Grille[LARGEUR-1][y] = 10
       Grille[0][y] = 10
    
    #Position des Ia
    Ia1 = Joueur("ia1",(1,0,0),(LARGEUR//2,HAUTEUR-2),1,(0,1))
    Joueurs.append(Ia1)
    
    # J1 = Joueur("joueur1",(1,0.5,0.5),(LARGEUR//2,1),0,(0,1))
    # Ia2 = Joueur("ia2",(0,0,1),(LARGEUR-2,HAUTEUR//2),1,(0,1))
    # Ia3 = Joueur("ia3",(0,1,0),(1,HAUTEUR//2),1,(0,1))
    # Joueurs.append(J1)
    # Joueurs.append(Ia2)
    # Joueurs.append(Ia3)

#################################################################################
# gestion du joueur humain et de l'IA
# VOTRE CODE ICI 
def CompteARebours():
    time.sleep(1)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)

def Play():
    Affiche()
    CompteARebours()
    
    while (True):
        time.sleep(0.2)

        AlivePlayers = []
        for joueur in Joueurs:
            if(joueur.isAlive):
                AlivePlayers.append(joueur)
                
        if(len(AlivePlayers)==0):
            print("Nul")
            return
            
        for joueur in AlivePlayers:
            # if(len(AlivePlayers) == 1):
            #     print(joueur.name, "Win")
            #     return
            if(joueur.status == 1): #Status => Joueur/IA
                IaAction(joueur)
            else:
                PlayerAction(joueur)
        
        CheckDeath()
        
        # fin de traitement
        Affiche()

@jit
def GetListMovements(mapTemp1, xTemp1, yTemp1):
    #Initialisation d'une liste de coordonnées possible
    resListMovements = []
    #Si le mouvement est possible, ajout de la coordonnée dans la liste
    if(mapTemp1[xTemp1+1][yTemp1] == 0): resListMovements.append((xTemp1+1,yTemp1))
    if(mapTemp1[xTemp1-1][yTemp1] == 0): resListMovements.append((xTemp1-1,yTemp1))
    if(mapTemp1[xTemp1][yTemp1+1] == 0): resListMovements.append((xTemp1,yTemp1+1))
    if(mapTemp1[xTemp1][yTemp1-1] == 0): resListMovements.append((xTemp1,yTemp1-1))
    
    #Retourne la liste des coordonnées auxquelles le joueur peut se déplacer
    return resListMovements

@jit
def MonteCarlo(mapTemp2, xTemp2, yTemp2, nbSimulation2):
    #Initialisation du résultat total des simulations
    total = 0
    #Création de n simulation
    for i in range(0, nbSimulation2):
        #Création d'une copie de la map pour effectuer la simulation
        mapCopy = np.copy(mapTemp2)
        #Ajout du résultat de la simulation au total des simulations
        total += Simulation(mapCopy, xTemp2, yTemp2)
    #Retour de la moyenne lorsque toute les simulations sont faites
    return total/nbSimulation2

@jit
def Simulation(simMapTemp3, sim_xTemp3, sim_yTemp3):
    #Initialisation du resultat de la simulation
    simScore = 0
    while(True):
        #Test
        simMapTemp3[sim_xTemp3][sim_yTemp3] = 1
        #Obtient la liste des mouvements possibles
        simListMov = GetListMovements(simMapTemp3, sim_xTemp3, sim_yTemp3)
        #Prévision de collision
        #Si aucun mouvement n'est possible, la partie se termine
        if(len(simListMov)==0):
            return simScore
        else:
            #Obtient un mouvement possible aléatoire
            simRandomMov = simListMov[random.randrange(len(simListMov))]
            #Crée le mur
            simMapTemp3[sim_xTemp3][sim_yTemp3] == 1
            #Déplace fictivement le joueur
            sim_xTemp3 = simRandomMov[0]
            sim_yTemp3 = simRandomMov[1]
            #Actualise le score de la simulation
            simScore += 1
@jit
def NMC(level, node, grille):
    if level == 0: # approche MC
        seq = []
        while len(GetListMovements(grille, node[0], node[1])) > 0:
            children = GetListMovements(grille, node[0], node[1])
            
            grille[node[0]][node[1]] = 1
            node = children[random.randrange(len(children))]
            seq.append(node)
        return len(seq), seq

    else: ## for levels >= 1
        # conserve le meilleur score/sequence connu de la boucle WHILE
        # si on trouve une séquence avec très bon score dès le début => conserve durant le while
        seq     = []
        numcoup = 0
        best_score = -1
        
        # boucle de deroulement de la partie
        while len(GetListMovements(grille, node[0], node[1])) > 0 :
            # monte carlo sur chaque coup possible
            # si aucun coup n'est meileur on conserve le meilleur connu précédent
            children = GetListMovements(grille, node[0], node[1])
            for newnode in children:
                (score,simseq) = NMC(level-1,newnode,grille) 
                if score > best_score :
                    best_score = score
                    seq = seq[0:numcoup-1] + simseq               
                    # meilleur score => remplace à partir de numcoup 
            # la quantité de coups peut etre différent
            # on valide le coup de la meilleure sequence connue
            if len(seq)==0:
                return best_score, seq
                
            node = seq[numcoup]
            numcoup  += 1
        return best_score, seq
            

def PlayerAction(joueur):
    Grille[joueur.pos[0]][joueur.pos[1]] = 1
    joueur.paths.append(joueur.pos)
    
    if(keyboard.is_pressed('up')): 
        joueur.direction = (0,1) 
    elif(keyboard.is_pressed('down')): 
        joueur.direction = (0,-1) 
    elif(keyboard.is_pressed('right')): 
        joueur.direction = (1,0) 
    elif(keyboard.is_pressed('left')): 
        joueur.direction = (-1,0) 
    
    joueur.pos= (joueur.pos[0]+joueur.direction[0],joueur.pos[1]+joueur.direction[1])

  
def IaAction(joueur):
    nbSimulation1 = 5
    #Laisse la trace de la moto
    Grille[joueur.pos[0]][joueur.pos[1]] = 1
    joueur.paths.append(joueur.pos)
    #Obtient la liste des déplacement possibles
    ListMov = GetListMovements(Grille, joueur.pos[0], joueur.pos[1])
    #Prévision de collision
    #Si aucun déplacement n'est possible, la partie se termine
    if(len(ListMov)==0):
        joueur.ResetPath(Grille)
        joueur.Dead()
        return
    #Sinon, on effectue un déplacement possible
    else:
        #On effectue une simulation pour déterminer le meilleur déplacement
        #Initialisation du meilleur score des simulations
        bestScore = 0
        #Initialisation du déplacement obtenant le meilleur score
        bestMov = ListMov[0]
        #simulationTimeStart = time.time()
        #Pour chaque déplacement dans la liste des déplacements possibles
        for mov in ListMov:
            #Appel de la méthode monte carlo
            scoreTemp, temp = NMC(nbSimulation1, mov, np.copy(Grille))
            print("temp",temp)
            #scoreTemp = MonteCarlo(Grille, mov[0], mov[1], nbSimulation1)
            print(scoreTemp)
            #Vérification
            #Si le score de la simulatione est meilleur que le précédent
            if(scoreTemp > bestScore):
                #Actualise le meilleur score
                bestScore = scoreTemp
                #Actualise le meilleur déplacement
                bestMov = mov
        #print(time.time() - simulationTimeStart)
        #Déplacement du joueur selon le meilleur déplacement
        joueur.pos = (bestMov[0], bestMov[1])
        
def CheckDeath():
    isDead = []
    
    for joueurA in Joueurs:
        for joueurB in Joueurs:
            if joueurA.name != joueurB.name and joueurA.isAlive and joueurB.isAlive:
                if joueurA.pos == joueurB.pos:
                    isDead.append(joueurA)
    
    for joueur in Joueurs:
        if joueur.isAlive:
            if Grille[joueur.pos[0]][joueur.pos[1]] != 0:
                isDead.append(joueur)
                    
    for joueur in isDead:
        joueur.Dead()
        
################################################################################
#    
# Dessine la grille de jeu
def Affiche():
    axes.clear()
    
    plt.xlim(0,20)
    plt.ylim(0,20)
    plt.axis('off')
    fig.patch.set_facecolor((0,0,0))
    
    axes.set_aspect(1)
    
    #Dessine les bords et les bords
    Murs = []
    Bords = []
    Ports = []
    for x in range (LARGEUR):
        for y in range (HAUTEUR):
            if (Grille[x][y] == 10 ) : Bords.append(plt.Rectangle((x,y), width = 1, height = 1))
    #Dessine les motos et les trainées
    for joueur in Joueurs:
        if(joueur.isAlive):
            axes.add_patch(plt.Circle((joueur.pos[0]+0.5,joueur.pos[1]+0.5), radius=0.5, facecolor = joueur.color ))
        Murs = []
        for path in joueur.paths: 
            Murs.append(plt.Rectangle((path[0],path[1]), width = 1, height = 1))
        axes.add_collection(matplotlib.collections.PatchCollection(Murs, facecolors = joueur.color))      
        
    axes.add_collection(matplotlib.collections.PatchCollection(Bords, facecolors = (0.6, 0.6, 0.6)))
        
    # demande reaffichage
    fig.canvas.draw()
    fig.canvas.flush_events()  

################################################################################  
# Lancement des parties      
          
def GestionnaireDeParties():
    while True:
        time.sleep(1) # pause d'une seconde entre chaque partie
        InitPartie()
        Play()
        Affiche()
        print("Partie Fini")
        
     
GestionnaireDeParties()


#########################
# def NMC(level,x,y,GrilleTemp):
#     Grille2 = np.copy(GrilleTemp)
#     if level == 0:
#         test[0] +=1
#         seq = []
#         # seq.append([x,y])
#         # GrilleTemp=np.copy(GrilleTemp)
#         Mouvement = 0
#         while(True):
#             L=DeplacementPossible(Grille2,x,y)
#             if len(L) ==0:
#                 return len(seq),seq
#             Deplacement = L[random.randrange(len(L))]
#             Grille2[x][y] = 1
#             x = Deplacement[0]
#             y = Deplacement[1]
#             seq.append([x,y])
#             Mouvement +=1
#     else :
#         seq = []
#         # seq.append([x,y])
#         numcoup = 0
#         best_score = -1
# 
#         while(True):
#             L=DeplacementPossible(Grille2,x,y)
#             if len(L) ==0:
#                 return best_score,seq
#             Grille2[x][y] = 1
#             # best_score = -1
#             for newnode in L:
#                 score,simseq = NMC(level-1,newnode[0],newnode[1],Grille2)
#                 if score > best_score:
#                     best_score = score
#                     list = []
#                     list.append([newnode[0],newnode[1]])
#                     seq = seq[0:numcoup] +list +simseq
#             if(numcoup == len(seq) ):
#                 return -1,seq
#             x = seq[numcoup][0]
#             y = seq[numcoup][1]
#             numcoup +=1
#################