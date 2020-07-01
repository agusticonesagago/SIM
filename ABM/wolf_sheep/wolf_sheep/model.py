from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from wolf_sheep.agents import GrassPatch, Hen, Egg, HatchingChicken, Rooster, FertilizedEgg
from wolf_sheep.schedule import RandomActivationByBreed


class WolfSheep(Model):
  
    height = 20
    width = 20

    initial_egg = 50
    initial_rooster = 50
    initial_hatchingChicken = 50
    initial_hen = 50
    initial_fertilized_egg = 50

    hen_gain_from_food = 20
    rooster_gain_from_food = 20
    hatchingChicken_gain_from_food = 20

    grass = True
    grass_regrowth_time = 30

    donde_ha_puesto_huevos = []
    donde_ha_visto_huevos = []

    current_step = 0

    fecundat = False

    verbose = False  # Print-monitoring

    description = (
        "A model for simulating hen, rooster and egg ecosystem."
    )

    def __init__(
        self,
        height=20,
        width=20,

        initial_hatchingChicken=100,
        initial_hen=100,
        initial_egg=100,
        initial_rooster=50,
        initial_fertilized_egg=50,

        grass=True,
        grass_regrowth_time=30,

        hen_gain_from_food = 20,
        rooster_gain_from_food = 20,
        hatchingChicken_gain_from_food = 20,

        donde_ha_puesto_huevos = [],
        donde_ha_visto_huevos = [],

        current_step = 0,

        fecundat = False,
    ):
       

        super().__init__()
        self.height = height
        self.width = width

        self.initial_hatchingChicken = initial_hatchingChicken
        self.initial_egg = initial_egg
        self.initial_hen = initial_hen
        self.initial_rooster = initial_rooster
        self.initial_fertilized_egg = initial_fertilized_egg

        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time

        self.rooster_gain_from_food = rooster_gain_from_food
        self.hen_gain_from_food = hen_gain_from_food
        self.hatchingChicken_gain_from_food = hatchingChicken_gain_from_food

        self.donde_ha_puesto_huevos = donde_ha_puesto_huevos
        self.donde_ha_visto_huevos = donde_ha_visto_huevos

        self.current_step = current_step

        self.fecundat = fecundat

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {   
                "Rooster": lambda m: m.schedule.get_breed_count(Rooster),
                "Hen": lambda m: m.schedule.get_breed_count(Hen),
                "HatchingChicken": lambda m: m.schedule.get_breed_count(HatchingChicken),
                "Egg": lambda m: m.schedule.get_breed_count(Egg),
                "FertilizedEgg": lambda m: m.schedule.get_breed_count(FertilizedEgg),
            }
        )

        # Create Hatching chicken:
        for i in range(self.initial_hatchingChicken):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.hatchingChicken_gain_from_food)
            hatchingChicken = HatchingChicken(self.next_id(), (x, y), self, True, energy, current_step, 0)
            self.grid.place_agent(hatchingChicken, (x, y))
            self.schedule.add(hatchingChicken)

        # Create Egg:
        for i in range(self.initial_egg):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.hen_gain_from_food)
            egg = Egg(self.next_id(), (x, y), self, True, energy, fecundat, current_step)
            self.grid.place_agent(egg, (x, y))
            self.schedule.add(egg)


        # Create Fertilized egg:
        for i in range(self.initial_fertilized_egg):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.hen_gain_from_food)
            fertilizedEgg = FertilizedEgg(self.next_id(), (x, y), self, True, energy, True, current_step)
            self.grid.place_agent(fertilizedEgg, (x, y))
            self.schedule.add(fertilizedEgg)

        # Create Hen:
        for i in range(self.initial_hen):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.hen_gain_from_food)
            current_step = 0
            hen = Hen(self.next_id(), (x, y), self, True, energy, donde_ha_puesto_huevos, current_step)
            self.grid.place_agent(hen, (x, y))
            self.schedule.add(hen)


        # Create Rooster:
        for i in range(self.initial_rooster):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.rooster_gain_from_food)
            rooster = Rooster(self.next_id(), (x, y), self, True, energy, donde_ha_visto_huevos, current_step, [])
            self.grid.place_agent(rooster, (x, y))
            self.schedule.add(rooster)


        # Create Grass patches
        if self.grass:
            for agent, x, y in self.grid.coord_iter():

                fully_grown = self.random.choice([True, False])

                if fully_grown:
                    countdown = self.grass_regrowth_time
                else:
                    countdown = self.random.randrange(self.grass_regrowth_time)

                patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_breed_count(Hen),
                ]
            )

    def run_model(self, step_count=200):

        if self.verbose:
            print("Initial number hen: ", self.schedule.get_breed_count(Hen))
            print("Initial number rooster: ", self.schedule.get_breed_count(Rooster))
            print("Initial number hatching Chicken: ", self.schedule.get_breed_count(HatchingChicken))
            print("Initial number egg: ", self.schedule.get_breed_count(Egg))
            print("Initial number egg fertilized: ", self.schedule.get_breed_count(FertilizedEgg))

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            
