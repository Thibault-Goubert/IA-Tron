import random
import time
import copy 
import numpy as np
import random
from numba import jit
import keyboard

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
    global Grille, PosJ1, NbPartie, Joueurs, Portals
    
    NbPartie += 1
    Joueurs = []
    Portals = []
    
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
       
    #positionne les portails
    p1 = (2,2)
    p2 = (2,HAUTEUR-3)
    p3 = (LARGEUR-3,HAUTEUR-3)
    p4 = (LARGEUR-3,2)
    
    Portals.append(p1)
    Portals.append(p2)
    Portals.append(p3)
    Portals.append(p4)
    
    p12 = (4,4)
    p22 = (4,HAUTEUR-5)
    p32 = (LARGEUR-5,HAUTEUR-5)
    p42 = (LARGEUR-5,4)
    
    Portals.append(p12)
    Portals.append(p22)
    Portals.append(p32)
    Portals.append(p42)
    
    for portal in Portals:
        Grille[portal[0]][portal[1]] = 11
    
    # position du joueur 1
    J1 = Joueur("joueur1",(1,0.5,0.5),(LARGEUR//2,1),0,(0,1))
    Joueurs.append(J1)
    
    #Position des Ia
    Ia1 = Joueur("ia1",(1,0,0),(LARGEUR//2,HAUTEUR-2),1,(0,1))
    Ia2 = Joueur("ia2",(0,0,1),(LARGEUR-2,HAUTEUR//2),1,(0,1))
    Ia3 = Joueur("ia3",(0,1,0),(1,HAUTEUR//2),1,(0,1))
    
    Joueurs.append(Ia1)
    Joueurs.append(Ia2)
    Joueurs.append(Ia3)
    
    #Obstacles
        #Cross
    #for k in range(LARGEUR-6):
    #    Grille[k+3][HAUTEUR//2] = 10
    #for k in range(HAUTEUR-6):
    #    Grille[LARGEUR//2][k+3] = 10 
        #Square
    for k in range(LARGEUR-6):
        Grille[k+3][HAUTEUR-4] = 10
        Grille[k+3][3] = 10
    for k in range(HAUTEUR-8):
        Grille[3][k+4] = 10
        Grille[LARGEUR-4][k+4] = 10

#################################################################################
#
# gestion du joueur humain et de l'IA
# VOTRE CODE ICI 
def Play():
    time.sleep(1)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    while (True):
        time.sleep(0.2)
        global  Joueurs

        nbAlive = 0
        for joueur in Joueurs:
            if(joueur.isAlive):
                nbAlive += 1
                
        if(nbAlive==0):
            print("Nul")
            return
            
        for joueur in Joueurs:
            if(joueur.isAlive):
                if(nbAlive == 1):
                    print(joueur.name, ": Win")
                    return
                elif(joueur.status == 1):
                    IaAction(joueur)
                else:
                    PlayerAction(joueur)
        
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
    
    if(mapTemp1[xTemp1+1][yTemp1] == 11):  
        if(GetTeleportValidation((xTemp1+1,yTemp1), mapTemp1)):
            resListMovements.append(GetTeleport((xTemp1+1,yTemp1)))
   
    if(mapTemp1[xTemp1-1][yTemp1] == 11):  
        if(GetTeleportValidation((xTemp1-1,yTemp1), mapTemp1)):
            resListMovements.append(GetTeleport((xTemp1-1,yTemp1)))
    
    if(mapTemp1[xTemp1][yTemp1+1] == 11):  
        if(GetTeleportValidation((xTemp1,yTemp1+1), mapTemp1)):
            resListMovements.append(GetTeleport((xTemp1,yTemp1+1)))
    
    if(mapTemp1[xTemp1][yTemp1-1] == 11):  
        if(GetTeleportValidation((xTemp1,yTemp1-1), mapTemp1)):
            resListMovements.append(GetTeleport((xTemp1,yTemp1-1)))
    
    #Retourne la liste des coordonnées auxquelles le joueur peut se déplacer
    #Resultat du 1er mouvement : [(7, 1), (5, 1), (6, 2)]
    #Droite,Gauche,Haut
    return resListMovements

def GetTeleport(portalPos):
    if portalPos == (2,2):                 
        return (4,5)
    if portalPos == (2,HAUTEUR-3):         
        return (5,HAUTEUR-3)
    if portalPos == (LARGEUR-3,HAUTEUR-3): 
        return (LARGEUR-5,HAUTEUR-6)
    if portalPos == (LARGEUR-3,2):         
        return (LARGEUR-6,4)

    if portalPos == (4,4):                 
        return (3,2)
    if portalPos == (4,HAUTEUR-5):         
        return (2,HAUTEUR-4)
    if portalPos == (LARGEUR-5,HAUTEUR-5): 
        return (LARGEUR-4,HAUTEUR-3)
    if portalPos == (LARGEUR-5,4):         
        return (LARGEUR-3,3)

def GetTeleportValidation(portalPos, mapTempPort):
    if portalPos == (2,2):                 
        if(mapTempPort[4][5]==0):                 
            return True
    if portalPos == (2,HAUTEUR-3):         
        if(mapTempPort[5][HAUTEUR-3]==0):         
            return True
    if portalPos == (LARGEUR-3,HAUTEUR-3): 
        if(mapTempPort[LARGEUR-5][HAUTEUR-6]==0): 
            return True
    if portalPos == (LARGEUR-3,2):         
        if(mapTempPort[LARGEUR-6][4]==0):         
            return True

    if portalPos == (4,4):                 
        if(mapTempPort[3][2]==0):                 
            return True
    if portalPos == (4,HAUTEUR-5):         
        if(mapTempPort[2][HAUTEUR-4]==0):         
            return True
    if portalPos == (LARGEUR-5,HAUTEUR-5): 
        if(mapTempPort[LARGEUR-4][HAUTEUR-3]==0): 
            return True
    if portalPos == (LARGEUR-5,4):         
        if(mapTempPort[LARGEUR-3][3]==0):         
            return True
    
    return False

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
            #Déplacement fictivement le joueur
            sim_xTemp3 = simRandomMov[0]
            sim_yTemp3 = simRandomMov[1]
            #Actualise le score de la simulation
            simScore += 1

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
    if(Grille[joueur.pos[0]][joueur.pos[1]] != 0): 
        joueur.Dead()
        for path in joueur.paths:
            Grille[path[0]][path[1]] = 0
        joueur.paths = []
    
def IaAction(joueur):
    nbSimulation1 = 100
    #Laisse la trace de la moto
    Grille[joueur.pos[0]][joueur.pos[1]] = 1
    joueur.paths.append(joueur.pos)
    #Obtient la liste des déplacement possibles
    ListMov = GetListMovements(Grille, joueur.pos[0], joueur.pos[1])
    #Prévision de collision
    #Si aucun déplacement n'est possible, la partie se termine
    if(len(ListMov)==0):
        joueur.Dead()
        for path in joueur.paths:
            Grille[path[0]][path[1]] = 0
        joueur.paths = []
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
            scoreTemp = MonteCarlo(Grille, mov[0], mov[1], nbSimulation1)
            #Vérification
            #Si le score de la simulatione est meilleur que le précédent
            if(scoreTemp > bestScore):
                #Actualisa le meilleur score
                bestScore = scoreTemp
                #Actualise le meilleur déplacement
                bestMov = mov
        #print(time.time() - simulationTimeStart)
        #Déplacement du joueur selon le meilleur déplacement
        joueur.pos = (bestMov[0], bestMov[1])
    
    if(Grille[joueur.pos[0]][joueur.pos[1]] != 0): 
        joueur.Dead()
        for path in joueur.paths:
            Grille[path[0]][path[1]] = 0
        joueur.paths = []
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
            if (Grille[x][y] == 11 ) : Ports.append(plt.Rectangle((x,y), width = 1, height = 1))
    #Dessine les motos et les trainées
    for joueur in Joueurs:
        if(joueur.isAlive):
            axes.add_patch(plt.Circle((joueur.pos[0]+0.5,joueur.pos[1]+0.5), radius=0.5, facecolor = joueur.color ))
        Murs = []
        for path in joueur.paths: 
            Murs.append(plt.Rectangle((path[0],path[1]), width = 1, height = 1))
        axes.add_collection(matplotlib.collections.PatchCollection(Murs, facecolors = joueur.color))      
        
    axes.add_collection(matplotlib.collections.PatchCollection(Bords, facecolors = (0.6, 0.6, 0.6)))
    axes.add_collection(matplotlib.collections.PatchCollection(Ports, facecolors = (0.6, 0.6, 0)))
        
    # demande reaffichage
    fig.canvas.draw()
    fig.canvas.flush_events()  

################################################################################
#    
# Lancement des parties      
          
def GestionnaireDeParties():
    for i in range(3):
        time.sleep(1) # pause dune seconde entre chaque partie
        InitPartie()
        Play()
        Affiche()
        print("Partie Fini")
        
     
GestionnaireDeParties()