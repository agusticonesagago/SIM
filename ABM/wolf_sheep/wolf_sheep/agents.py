from mesa import Agent
from wolf_sheep.random_walk import RandomWalker

import random, math

def distance(p0, p1):
    # Calculate distance between 2 points 
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

class Rooster(RandomWalker):

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, donde_ha_visto_huevos=[], current_step=None, info_gallina=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.donde_ha_visto_huevos = []
        self.current_step = current_step
        self.info_gallina = info_gallina

    def step(self):
               
        lista_posiciones_cercanas = []

        self.current_step += 1

        """
        12 iterations == 1 day
        1-8 iterations (move)
        9-12 iterations (sleep)
        """

        decimal = abs(self.current_step/12) - abs(int(self.current_step/12))
        comparar = abs((9-1)/12) - abs(int((9-1)/12))

        if (self.current_step%12==0 or round(decimal,2)>round(comparar,2)):
            # Rooster sleeps
            self.energy -= 0.25
        else:
            # Rooster is awake
            if(len(self.info_gallina)>0):
                # Rooster meets a Hen, and the Hen explains where she has laid the eggs
                self.donde_ha_visto_huevos.append(self.info_gallina[0])

            if self.model.grass:
                # Rooster loses energy(move) and gains(eat) if model.grass(activated)
                        self.energy -= 1

                        this_cell = self.model.grid.get_cell_list_contents([self.pos])
                        grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
                        if grass_patch.fully_grown:
                            self.energy += self.model.rooster_gain_from_food
                            grass_patch.fully_grown = False

            if self.energy > 0:
                # Rooster is alive
                for i in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        # Save all the the possible movements
                        if((self.pos[0]+i)>=0 and (self.pos[1]+y)>=0 and (self.pos[0]+i)<=19 and (self.pos[1]+y)<=19
                            and ((self.pos[0]+i)!=self.pos[0] and (self.pos[1]+y!=self.pos[1]))): 
                            lista_posiciones_cercanas.append((self.pos[0]+i, self.pos[1]+y)) 

                huevos = []
                min_vida_huevo = 999999
                pos_vida_huevo = [-1,-1]
                for i in range(len(lista_posiciones_cercanas)):
                   # Rooster remembers all the the eggs near him
                   this_cell = self.model.grid.get_cell_list_contents([lista_posiciones_cercanas[i]])
                   egg = [obj for obj in this_cell if isinstance(obj, Egg)]
                   if(len(egg)>0): 
                    huevos.append(egg[0].pos)
                    self.donde_ha_visto_huevos.append(egg[0].pos)
                    if(egg[0].energy < min_vida_huevo and egg[0].energy>0):
                        # Rooster looks which egg has less energy (preventing death)
                        min_vida_huevo = egg[0].energy
                        pos_vida_huevo = egg[0].pos

                if self.energy > 5:
                    # Rooster needs more than 5 of energy to "fertilize" an egg               
                    if(min_vida_huevo < 999999): 
                        # Rooster "fertilize" an egg near him
                        self.move_position(pos_vida_huevo)
                        this_cell = self.model.grid.get_cell_list_contents(pos_vida_huevo)
                        egg = [obj for obj in this_cell]
                        egg[0].fecundat = True
                        self.energy -= 5

                    else:
                        # Rooster doesn't have an egg near him
                        if(len(self.donde_ha_visto_huevos)==0):
                            # Rooster haven't seen any egg during his life 
                            self.random_move()
                        else:
                            # Rooster have seen some eggs during his life 
                            posicion_cercana = []
                            distancia_minima_huevos = 99999

                            for i in range(len(self.donde_ha_visto_huevos)):
                                # Rooster wants to know the nearest place
                                distancia_actual_pos_visto_huevos = distance(self.pos, self.donde_ha_visto_huevos[i])
                                if(distancia_actual_pos_visto_huevos<distancia_minima_huevos and distancia_actual_pos_visto_huevos>2):
                                    distancia_minima_huevos = distancia_actual_pos_visto_huevos
                                    posicion_cercana = self.donde_ha_visto_huevos[i]

                            if(distancia_minima_huevos == 99999):
                                # Rooster only knows one egg and he is on the same position
                                self.random_move()
                            
                            else:
                                # Rooster knows he needs to go
                                distancia_minima_moverse = 99999
                                movimiento_hacer = []

                                # Calculation of which is the best direction to take
                                for i in range(len(lista_posiciones_cercanas)):
                                    distancia_actual_pos_movimiento = distance(posicion_cercana, lista_posiciones_cercanas[i])
                                    if(distancia_actual_pos_movimiento<distancia_minima_moverse and lista_posiciones_cercanas[i]!=self.pos):
                                        distancia_minima_moverse = distancia_actual_pos_movimiento
                                        movimiento_hacer = lista_posiciones_cercanas[i]

                                # Move to the best direction
                                self.move_position(movimiento_hacer)

                else:
                    # Rooster has less than 5 of energy and he can't "fertilize" an egg
                    gespa_posicions = []

                    # Rooster looks grass cells to eat
                    for i in range(len(lista_posiciones_cercanas)):
                       this_cell = self.model.grid.get_cell_list_contents([lista_posiciones_cercanas[i]])
                       grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
                      
                       if grass_patch.fully_grown:
                            gespa_posicions.append(lista_posiciones_cercanas[i])

                    if(len(gespa_posicions)>0):
                        # Rooster choses randomly one grass cell to go 
                        self.move_position(random.choice(gespa_posicions))
                    else :
                        # Rooster choses randomly where to go (no grass cell around him)
                        self.random_move()

            else:
                # Rooster dies (0 energy)
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)


class Egg(RandomWalker):

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, fecundat=False, current_step=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.pos = pos
        self.fecundat = fecundat
        self.current_step = current_step

    def step(self):

        """
        Egg has "energy" and decreases if it is not fertilized
        """

        self.current_step += 1
        self.energy -= 1

        if self.energy <= 0:
            # Egg dies (0 energy)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

        else:
            # Egg is alive
            decimal = abs(self.current_step/12) - abs(int(self.current_step/12))
            comparar = abs((9-1)/12) - abs(int((9-1)/12))

            if not(self.current_step%12==0 or round(decimal,2)>round(comparar,2)):
                this_cell = self.model.grid.get_cell_list_contents([self.pos])
                cuantos_gallos_encima = [obj for obj in this_cell if isinstance(obj, Rooster)]
                if(len(cuantos_gallos_encima)>0):
                    # Egg changes to Fertilized Egg (Rooster at the same cell)
                    fertilizedEgg = FertilizedEgg(
                           self.model.next_id(), self.pos, self.model, self.moore, 0, self.fecundat, self.current_step
                    )
                    self.model.grid.place_agent(fertilizedEgg, self.pos)
                    self.model.schedule.add(fertilizedEgg)
                    self.model.grid._remove_agent(self.pos, self)
                    self.model.schedule.remove(self)



class FertilizedEgg(RandomWalker):

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, fecundat=True, current_step=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.pos = pos
        self.fecundat = fecundat
        self.current_step = current_step

    def step(self):

        """
        Egg Ferilized has "energy" and increases until Hatching Chicken can come out
        """

        self.current_step += 1
        self.energy += 1

        if(self.energy >= 252):
            # Enough energy to come out the Hatching Chicken
            hatchingChicken = HatchingChicken(
                       self.model.next_id(), self.pos, self.model, self.moore, 10, self.current_step, 0
            )
            self.model.grid.place_agent(hatchingChicken, self.pos)
            self.model.schedule.add(hatchingChicken)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)


class Hen(RandomWalker):

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, donde_ha_puesto_huevos=[], current_step=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.donde_ha_puesto_huevos = []
        self.current_step = current_step

    def step(self):
        
        """
        12 iterations == 1 day
        1-4 iterations (lay eggs and move(eat)) --> Lay eggs always near the last ones  
        5-8 iterations (move(eat))
        9-12 iterations (sleep)
        """

        self.current_step += 1

        lista_posiciones_cercanas = []

        decimal = abs(self.current_step/12) - abs(int(self.current_step/12))
        comparar = abs((9-1)/12) - abs(int((9-1)/12))

        if self.energy <= 0:
            # Hen dies (0 energy)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
         
        else:
            # Hen is alive
            for i in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        # Save all the the possible movements
                        if((self.pos[0]+i)>=0 and (self.pos[1]+y)>=0 and (self.pos[0]+i)<=19 and (self.pos[1]+y)<=19
                            and ((self.pos[0]+i)!=self.pos[0] and (self.pos[1]+y!=self.pos[1]))):  
                            lista_posiciones_cercanas.append((self.pos[0]+i, self.pos[1]+y)) 

            if (self.current_step%12==0 or round(decimal,2)>round(comparar,2)):
                # Hen sleeps
                self.energy -= 0.25
            else:
                # Hen is awake
                for i in range(len(lista_posiciones_cercanas)):
                       this_cell = self.model.grid.get_cell_list_contents([lista_posiciones_cercanas[i]])
                       rooster_encontrado = [obj for obj in this_cell if isinstance(obj, Rooster)]
                       if(len(rooster_encontrado)>0):
                            # Hen meets a Rooster, and she explains to the Rooster where she has laid the eggs
                            rooster_encontrado[0].info_gallina = self.donde_ha_puesto_huevos

                if self.model.grass:
                    # Hen loses energy(move) and gains(eat) if model.grass(activated)
                    self.energy -= 1
                    this_cell = self.model.grid.get_cell_list_contents([self.pos])
                    grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
                    if grass_patch.fully_grown:
                        self.energy += self.model.hen_gain_from_food
                        grass_patch.fully_grown = False

                comparar = abs((5-1)/12) - abs(int((5-1)/12))
                if(round(decimal,2)>round(comparar,2)):
                    # Iterations 5-8 (move(eat))
                    gespa_posicions = []
                    # Hen looks grass cells to eat
                    for i in range(len(lista_posiciones_cercanas)):
                       this_cell = self.model.grid.get_cell_list_contents([lista_posiciones_cercanas[i]])
                       grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
                      
                       if grass_patch.fully_grown:
                            gespa_posicions.append(lista_posiciones_cercanas[i])

                    if(len(gespa_posicions)>0):
                        # Hen choses randomly one grass cell to go 
                        self.move_position(random.choice(gespa_posicions))
                    else:
                        # Hen choses randomly where to go (no grass cell around him)
                        self.random_move()

                else:
                    # Iterations 1-4 (lay eggs and move(eat))
                    if self.random.random() < 0.25 and self.energy>5:
                        # Hen needs more than 5 of energy to lay an egg    
                        if self.model.grass:
                            self.energy -= 5
                        huevo = Egg(
                            self.model.next_id(), self.pos, self.model, self.moore, 36, False, self.current_step
                        )
                        self.donde_ha_puesto_huevos.append(self.pos)
                        self.model.grid.place_agent(huevo, self.pos)
                        self.model.schedule.add(huevo)

                    
                    else:
                        # Hen moves to where she has layed previously 
                        if(len(self.donde_ha_puesto_huevos)==0):
                            # Hen hasn't layed before
                            self.random_move()
                        else:
                            # Hen moves to where she has layed previously 
                            posicion_cercana = []
                            distancia_minima_huevos = 99999
                            for i in range(len(self.donde_ha_puesto_huevos)):
                                # Hen wants to know the nearest place
                                distancia_actual_pos_puesto_huevos = distance(self.pos, self.donde_ha_puesto_huevos[i])
                                if(distancia_actual_pos_puesto_huevos<distancia_minima_huevos):
                                    distancia_minima_huevos = distancia_actual_pos_puesto_huevos
                                    posicion_cercana = self.donde_ha_puesto_huevos[i]

                            distancia_minima_moverse = 99999
                            movimiento_hacer = []

                            for i in range(len(lista_posiciones_cercanas)):
                                # Calculation of which is the best direction to take
                                distancia_actual_pos_movimiento = distance(posicion_cercana, lista_posiciones_cercanas[i])
                                if(distancia_actual_pos_movimiento<distancia_minima_moverse and lista_posiciones_cercanas[i]!=self.pos):
                                    distancia_minima_moverse = distancia_actual_pos_movimiento
                                    movimiento_hacer = lista_posiciones_cercanas[i]

                            # Move to the best direction
                            self.move_position(movimiento_hacer)

                        
class HatchingChicken(RandomWalker):

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None, current_step=None, saber_que_eres=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.energy = energy
        self.current_step = current_step
        self.saber_que_eres = saber_que_eres

    def step(self):

        self.current_step += 1

        # Increases energy (less time to change to Hen or Rooster)
        self.saber_que_eres += 1

        lista_posiciones_cercanas = []

        if self.energy <= 0:
            # Hatching Chicken dies (0 energy)
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

        else:
    
            decimal = abs(self.current_step/12) - abs(int(self.current_step/12))
            comparar = abs((9-1)/12) - abs(int((9-1)/12))

            if (self.current_step%12==0 or round(decimal,2)>round(comparar,2)): 
                # HatchingChicken sleeps
                self.energy -= 0.25

            else:
                if self.model.grass:
                    # HatchingChicken loses energy(move) and gains(eat) if model.grass(activated)
                    this_cell = self.model.grid.get_cell_list_contents([self.pos])
                    grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]
                    if grass_patch.fully_grown:
                        self.energy += self.model.hatchingChicken_gain_from_food
                        grass_patch.fully_grown = False

                for i in [-1, 0, 1]:
                    for y in [-1, 0, 1]:
                        # Save all the the possible movements
                        if((self.pos[0]+i)>=0 and (self.pos[1]+y)>=0 and (self.pos[0]+i)<=19 and (self.pos[1]+y)<=19
                            and ((self.pos[0]+i)!=self.pos[0] and (self.pos[1]+y!=self.pos[1]))):  
                            lista_posiciones_cercanas.append((self.pos[0]+i, self.pos[1]+y)) 

                gespa_posicions = []
                for i in range(len(lista_posiciones_cercanas)):
                   this_cell = self.model.grid.get_cell_list_contents([lista_posiciones_cercanas[i]])
                   grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)][0]                
                   if grass_patch.fully_grown:
                        gespa_posicions.append(lista_posiciones_cercanas[i])

                if(len(gespa_posicions)>0): 
                    # HatchingChicken choses randomly one grass cell to go
                    self.move_position(random.choice(gespa_posicions))
                else:
                    # HatchingChicken choses randomly where to go (no grass cell around him)
                    self.random_move()

                if self.saber_que_eres >= 180:
                    # HatchingChicken grows to Hen or to Rooster
                    numero_random = self.random.random()
                    if numero_random < 0.5:
                        # Hen
                        if self.model.grass:
                            self.energy /= 2
                        hen = Hen(
                            self.model.next_id(), self.pos, self.model, self.moore, self.energy, [], self.current_step
                        )
                        self.model.grid.place_agent(hen, self.pos)
                        self.model.schedule.add(hen)
                        self.model.grid._remove_agent(self.pos, self)
                        self.model.schedule.remove(self)

                    elif numero_random >= 0.5:
                        # Rooster
                        if self.model.grass:
                            self.energy /= 2
                        rooster = Rooster(
                            self.model.next_id(), self.pos, self.model, self.moore, self.energy, [], self.current_step, []
                        )
                        self.model.grid.place_agent(rooster, self.pos)
                        self.model.schedule.add(rooster)
                        self.model.grid._remove_agent(self.pos, self)
                        self.model.schedule.remove(self)

class GrassPatch(Agent):

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
      
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos

    def step(self):
        if not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1
