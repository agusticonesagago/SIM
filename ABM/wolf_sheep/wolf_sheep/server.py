from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from wolf_sheep.agents import GrassPatch, Hen, FertilizedEgg, Egg, HatchingChicken, Rooster
from wolf_sheep.model import WolfSheep


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Rooster:
        portrayal["Shape"] = "wolf_sheep/resources/rooster.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is Hen:
        portrayal["Shape"] = "wolf_sheep/resources/gallina.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is FertilizedEgg:
        portrayal["Shape"] = "wolf_sheep/resources/huevo-amarillo.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"


    elif type(agent) is Egg:
        portrayal["Shape"] = "wolf_sheep/resources/huevo.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"


    elif type(agent) is HatchingChicken:
        portrayal["Shape"] = "wolf_sheep/resources/pollito.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.energy, 1)
        portrayal["text_color"] = "White"

    elif type(agent) is GrassPatch:
        if agent.fully_grown:
            portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
        else:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(wolf_sheep_portrayal, 20, 20, 500, 500)
chart_element = ChartModule(
    [{"Label": "Hen", "Color": "blue"}, {"Label": "Rooster", "Color": "red"},{"Label": "HatchingChicken", "Color": "yellow"}
    ,{"Label": "Egg", "Color": "orange"}, {"Label": "FertilizedEgg", "Color": "green"}]
)

model_params = {
    "grass_regrowth_time": UserSettableParameter(
        "slider", "Grass Regrowth Time", 20, 0, 50
    ),
    "initial_rooster": UserSettableParameter(
        "slider", "Initial Rooster Population", 1, 1, 100
    ),
    "initial_hen": UserSettableParameter(
        "slider", "Initial Hen Population", 1, 1, 100
    ),
    "initial_hatchingChicken": UserSettableParameter(
        "slider", "Initial Hatching Chicken Population", 1, 1, 100
    ),
    "initial_egg": UserSettableParameter(
        "slider", "Initial Egg Population", 1, 1, 100
    ),
    "initial_fertilized_egg": UserSettableParameter(
        "slider", "Initial Fertilized Egg Population", 1, 1, 100
    ),
    "rooster_gain_from_food": UserSettableParameter(
        "slider", "Rooster Gain From Food", 4, 1, 10
    ),
    "hen_gain_from_food": UserSettableParameter(
        "slider", "Hen Gain From Food", 4, 1, 10
    ),
    "hatchingChicken_gain_from_food": UserSettableParameter(
        "slider", "Hatching Chicken Gain From Food", 4, 1, 10
    ),
}

server = ModularServer(
    WolfSheep, [canvas_element, chart_element], "Hen, Rooster and Egg Ecosystem", model_params
)
server.port = 8521