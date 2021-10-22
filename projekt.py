import random
import time
import math
import pygame
from datetime import datetime

class Box:
    def __init__(self, H, L, R):
        self.height = H * R
        self.length = L * R

class Particle:
    def __init__(self, m, R, rx, ry, vx, vy):
        self.mass = m
        self.radius = R
        self.r = [rx, ry]
        self.V = [vx, vy]

pygame.init()

scale = 5
M = 1000
N = 20
H = 10 * scale
L = 10 * scale  # convertion to pixels
m = 1
R = 2 * scale
d = 0.1 * R
Vinit =  4 # static velocity for all
t = 1 / (Vinit * 20) 

T = t * M #czas zliczania zderzeń
Vx = random.randint(1, Vinit) #składowe początkowej prędkość czerwonego atomu
Vy = random.randint(1, Vinit) 
collisions = 0

box = Box(H, L, R)

screen = pygame.display.set_mode((box.height, box.length))

if (H < 20 or L < 20):
    print("Invalid box size.")
    exit()

if (N < 1 or N > 0.25 * H * L):
    print("Invalid particle amount.")
    exit()

particle = []
r = []
counter = 0
check = 1
particle.append(Particle(m, R, R, R, Vx, Vy))
for i in range(1, N+1):
    while (counter != check):
        Rx = random.randrange(2 * R, box.length - R, 2 * R + 0.2*R)
        Ry = random.randrange(2 * R, box.length - R, 2 * R + 0.2*R)
        if (Rx, Ry) not in r:
            r.append([Rx, Ry])
            counter += 1
    check += 1
    if(random.randint(0, 1) == 0):
        V = random.randint(2, Vinit)
        particle.append(Particle(m, R, Rx, Ry, 1, V))
    else:
        V = -random.randint(2, Vinit)
        particle.append(Particle(m, R, Rx, Ry, V, -1))

ParticleImg = pygame.image.load('circle.png')
IMG_Resize = pygame.transform.scale(ParticleImg, (2 * R, 2 * R))
ParticleImgRed = pygame.image.load('circle-red.png')
IMG_Resize_Red = pygame.transform.scale(ParticleImgRed, (2 * R, 2 * R))

pygame.display.set_caption("Particle Simulation")
icon = pygame.image.load('molecule.png')
pygame.display.set_icon(icon)

hit_counter = 0
allLambdas = 0
running = True
start = datetime.now()
tmpTime = datetime.now()
while (running and (datetime.now() - start).total_seconds() <= T):
    screen.fill((46, 46, 48)) #grafika
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(IMG_Resize_Red, (int(particle[0].r[0] - R), int(particle[0].r[1] - R)))
    for i in range(1, N):
        screen.blit(IMG_Resize, (int(particle[i].r[0] - R), int(particle[i].r[1] - R)))
    
    # aktualizacja pozycji
    for i in range(0, N + 1):
        particle[i].r[0] = particle[i].r[0] + particle[i].V[0]
        particle[i].r[1] = particle[i].r[1] + particle[i].V[1]

    # obsluga kolizji
    for i in range(0, N + 1):
        for j in range(i + 1, N + 1):  # kwadraty nachodza sie
            distanceSquared = (particle[j].r[0] - particle[i].r[0])**2+(particle[j].r[1]-particle[i].r[1])**2
            if(particle[i].r[0] + 2 * R > particle[j].r[0] and particle[i].r[0] < particle[j].r[0] + 2 * R and particle[i].r[1] + 2 * R > particle[j].r[1] and particle[i].r[1] < particle[j].r[1] + 2 * R):
                if (distanceSquared <= (2 * particle[i].radius + d)**2):
                    if i == 0:
                        timeBetweenHits = datetime.now() - tmpTime
                        hit_counter += 1
                        allLambdas += timeBetweenHits.total_seconds() * math.sqrt(
                            (particle[i].V[0] ** 2) + (particle[i].V[1] ** 2))  
                        tmpTime = datetime.now()
                    angle = math.atan2(particle[j].r[1] - particle[i].r[1], particle[j].r[0] - particle[i].r[0])#korekcja pozycji
                    distanceBetweenCircles = math.sqrt(distanceSquared)
                    distanceToMove = particle[i].radius + particle[j].radius - distanceBetweenCircles
                    particle[j].r[0] += float(math.cos(angle) * distanceToMove)
                    particle[j].r[1] += float(math.cos(angle) * distanceToMove)
                    tangentVector = pygame.math.Vector2() #obliczanie nowych wektorów
                    tangentVector.x = -(particle[j].r[0] - particle[i].r[0])
                    tangentVector.y = particle[j].r[1] - particle[i].r[1]
                    if(tangentVector.x == 0): 
                        tangentVector.x = 0.00001
                    if(tangentVector.y == 0):
                        tangentVector.y = 0.00001
                    tangentVector = pygame.math.Vector2.normalize(tangentVector)
                    relativeVelocity = pygame.math.Vector2()
                    relativeVelocity.xy = particle[i].V[0]-particle[j].V[0], particle[i].V[1]-particle[j].V[1]
                    length = pygame.math.Vector2.dot(relativeVelocity, tangentVector)
                    velocityComponentOnTangent = pygame.math.Vector2()
                    velocityComponentOnTangent = tangentVector*length
                    velocityComponentPerpendicularToTangent = pygame.math.Vector2()
                    velocityComponentPerpendicularToTangent = relativeVelocity - velocityComponentOnTangent
                    particle[i].V[0] -= velocityComponentPerpendicularToTangent.x
                    particle[i].V[1] -= velocityComponentPerpendicularToTangent.y
                    particle[j].V[0] += velocityComponentPerpendicularToTangent.x
                    particle[j].V[1] += velocityComponentPerpendicularToTangent.y

        if (particle[i].r[0] < 0 + d + R): #uderzenia o krawędzie
            particle[i].V[0] = -particle[i].V[0]
            particle[i].r[0] = 0 + d + R
        if (particle[i].r[0] >= box.length - d - R):
            particle[i].V[0] = -particle[i].V[0]
            particle[i].r[0] = box.length - d - R
        if (particle[i].r[1] < 0 + d + R):
            particle[i].V[1] = -particle[i].V[1]
            particle[i].r[1] = 0 + d + R
        if (particle[i].r[1] >= box.height - d - R):
            particle[i].V[1] = -particle[i].V[1]
            particle[i].r[1] = box.height - d - R

    pygame.display.update()
    time.sleep(t)

if hit_counter == 0:
    print("Ilosc zderzen: 0.")
else:
    print("Ilosc zderzen: {}.".format(hit_counter))
    result = (1 / hit_counter) * allLambdas
    print("Srednia droga swobodna: {} m.".format(result))

frequency = hit_counter / T
print("Czestosc zderzen: {} Hz.".format(frequency))

print("Czas: {} s.".format(T))
