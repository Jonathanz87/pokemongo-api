import time
import logging
import config
import itemdic
import pokemondic
from custom_exceptions import GeneralPogoException

from api import PokeAuthSession
from location import Location

# Example functions
# Get profile
def getProfile(session):
        logging.info("Printing Profile:")
        profile = session.getProfile()
        logging.info(profile)

# Basic solution to spinning all forts.
# Since traveling salesman problem, not
# true solution. But at least you get
# those step in
def sortCloseForts(session):
    # Sort nearest forts (pokestop)
    logging.debug("Sorting Closest Poke Stop in %im", config.radius)
    latitude, longitude, _ = session.getCoordinates()
    ordered_forts = []
    for cell in session.getMapCells(radius = config.radius):
        for fort in cell.forts:
            dist = Location.getDistance(
                latitude,
                longitude,
                fort.latitude,
                fort.longitude
            )
            if fort.type == 1 and fort.cooldown_complete_timestamp_ms == 0:
                ordered_forts.append({'distance': dist, 'fort': fort})

    ordered_forts = sorted(ordered_forts, key=lambda k: k['distance'])
    return [instance['fort'] for instance in ordered_forts]

# Find the closest fort
def findClosestFort(session):
    logging.debug("Finding Nearest Poke Stop in %im", config.radius)
    latitude, longitude, _ = session.getCoordinates()
    closest_fort = None
    dist = float("inf")
    for cell in session.getMapCells(radius = config.radius):
        for fort in cell.forts:
            if fort.type == 1:
                tempdist = Location.getDistance(
                    latitude,
                    longitude,
                    fort.latitude,
                    fort.longitude
                )
                if (tempdist is not 0 and 
                    fort.cooldown_complete_timestamp_ms == 0 and 
                    tempdist < dist):
                    logging.debug("Poke Stop found in %dm:", tempdist)
                    dist = tempdist
                    closest_fort = fort
    return closest_fort

def spinStatusToStr(fortResponse):
    string = "PokeStop +" + str(fortResponse.experience_awarded) + " xp"
    if fortResponse.result == 1:
        for item in fortResponse.items_awarded:
            string = string + " +" + itemdic.indexToName(item.item_id)

    elif (fortResponse.result == 2):
        string += " OUT OF RANGE"

    elif (fortResponse.result == 4):
        string += " INVENTORY FULL"

    else:
        string += " IN COOLDOWN PERIOD"
    return string

# Walk to fort and spin
def walkAndSpin(session, fort):
    # No fort, demo == over
    if fort:
        logging.debug("Spinning a Poke Stop:")
        # Walk over
        walkToAndCatch(session, fort.latitude, fort.longitude, step=config.speed)
        # Give it a spin

        res = session.getFortSearch(fort)
        responseStr = spinStatusToStr(res)

        #print dir(fortResponse)
        logging.info(responseStr)
        if res.result == 4:
            logging.info("Toss: " + tossItems(session))

# Walk and spin everywhere
def walkAndSpinMany(session, forts):
    for fort in forts:
        walkAndSpin(session, fort)

# These act as more logical functions.
# Might be better to break out seperately
# Walk over to position in meters
# step = n meters/sec
def walkTo(session, olatitude, olongitude, epsilon=10, step=4):
    logging.debug("Calculate distance to destination(%f,%f) - %im/s",
                    olatitude, olatitude, step)
    latitude, longitude, _ = session.getCoordinates()
    dist = closest = Location.getDistance(
        latitude,
        longitude,
        olatitude,
        olongitude
    )

    divisions = dist / step
    if (divisions == 0):
        session.setCoordinates(
            olatitude,
            olongitude
            )
        logging.debug("Current location(%f,%f) - %im to destination",
                        latitude, longitude, int(dist))
        return
    dLat = (latitude - olatitude) / divisions
    dLon = (longitude - olongitude) / divisions
    logging.info("(%f,%f) -> (%f,%f) : %im in %i s",
                latitude, longitude,
                olatitude, olongitude,
                int(dist), int(dist / step) + 1)

    logging.debug("Start Walk")
    while dist > epsilon:
        if dist < step:
            session.setCoordinates(
            olatitude,
            olongitude
            )
            logging.debug("Current location(%f,%f) - %im to destination",
                            latitude, longitude, int(dist))
            break
        latitude -= dLat
        longitude -= dLon
        session.setCoordinates(
            latitude,
            longitude
        )
        dist = Location.getDistance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )
        logging.debug("Current location(%f,%f) - %im to destination",
                        latitude, longitude, int(dist))
        time.sleep(1) # 1 sec

def walkToAndCatch(session,olatitude, olongitude, epsilon=10, step=4):
    logging.debug("Calculate distance to destination(%f,%f) - %im/s",
                    olatitude, olatitude, step)
    latitude, longitude, _ = session.getCoordinates()
    dist = Location.getDistance(
        latitude,
        longitude,
        olatitude,
        olongitude
    )

    divisions = dist / step
    if (divisions == 0):
        session.setCoordinates(
            olatitude,
            olongitude
            )
        logging.debug("Current location(%f,%f) - %im to destination",
                        latitude, longitude, int(dist))
        return
    dLat = (latitude - olatitude) / divisions
    dLon = (longitude - olongitude) / divisions
    logging.info("(%f,%f) -> (%f,%f) : %im in %i s",
                latitude, longitude,
                olatitude, olongitude,
                int(dist), int(dist / step) + 1)

    logging.debug("Start Walk")
    while dist > epsilon:
        if dist < step:
            session.setCoordinates(
            olatitude,
            olongitude
            )
            logging.debug("Current location(%f,%f) - %im to destination",
                            latitude, longitude, int(dist))
            break
        latitude -= dLat
        longitude -= dLon
        session.setCoordinates(
            latitude,
            longitude
        )
        dist = Location.getDistance(
            latitude,
            longitude,
            olatitude,
            olongitude
        )
        logging.debug("Current location(%f,%f) - %im to destination",
                        latitude, longitude, int(dist))
        catchAllPokemon(session)
        time.sleep(1) # 1 sec

def catchStatusToStr(status):
    string = ""
    if(status.status == 1):
        string = ("captured +" + 
            str(sum(status.capture_award.xp)) + " xp +" + 
            str(sum(status.capture_award.candy)) + " candy +" + 
            str(sum(status.capture_award.stardust)) + " stardust")
    else:
        string = "escaped +" + str(sum(status.capture_award.xp)) + " xp"
    return string

def findAllPokemon(session):
    logging.debug("Finding all pokemons...")
    pokemons = []
    logging.debug("get cells in %im", config.radius)
    for cell in session.getMapCells(radius = config.radius):
        for pokemon in cell.wild_pokemons:
            logging.debug("[%s]\tat (%f,%f) in cell(%d)",
                pokemondic.indexToName(pokemon.pokemon_data.pokemon_id),
                pokemon.latitude,
                pokemon.longitude,
                cell.s2_cell_id
            )
            pokemons.append(pokemon)
    logging.debug("%i pokemons are found", len(pokemons))
    return pokemons

def catchAllPokemon(session):
    logging.debug("catch all pokemons")
    for pokemon in findAllPokemon(session):
        catchPokemon(session, pokemon)

# Catch a pokemon at a given point
def catchPokemon(session, pokemon):
    if pokemon:
        logging.debug("Catching pokemon [%s]", 
            pokemondic.indexToName(pokemon.pokemon_data.pokemon_id))
        session.getBag()
        pokeball_ID = 0

        logging.debug("select ball...")
        while (session.checkItenQuantity(1) <= 0 and 
            session.checkItenQuantity(2) <= 0 and 
            session.checkItenQuantity(3) <=0 and
            session.checkItenQuantity(4) <= 0):
            forts = sortCloseForts(session)
            #TODO exception handler for 0 fort found
            for fort in forts:
                walkTo(session, fort.latitude, fort.longitude, step = 50)
                session.getFortSearch(fort)
                session.getBag()

        for pokeball_ID in [1,2,3,4]:
            if(session.checkItenQuantity(pokeball_ID) > 0):
                break
        logging.debug("get %s", itemdic.indexToName(pokeball_ID))

        res = session.encounterAndCatch(pokemon, pokeball = pokeball_ID)
        
        responseStr = catchStatusToStr(res)

        logging.info("[" + pokemondic.indexToName(pokemon.pokemon_data.pokemon_id)
             + "]\t" + responseStr)

        if(res.status == 1):
            pokemon = session.getPokemonByID(res.captured_pokemon_id)
            if pokemon is not None:
                releasePokemonInCondition(session, pokemon,
                    IV = config.releaseIV, CP = config.releaseCP,
                    rareList = config.rarePokemonIDList)

def getIV(pokemon):
    return (float(pokemon.individual_attack) + 
            float(pokemon.individual_defense) +
            float(pokemon.individual_stamina)
            ) / 45

def nicknamePokemonIV(session, pokemon):
    logging.debug("nickname a Pokemon")
    name = pokemondic.indexToName(pokemon.pokemon_id)
    if len(name) > 9:
        name = name[:9]
    name += str(int(getIV(pokemon) * 1000))
    session.nicknamePokemon(pokemon, name)
    logging.info("Nickname [" + 
        pokemondic.indexToName(pokemon.pokemon_id) + "] to [" + name + "]")
    time.sleep(1)

def releasePokemonInCondition(session, pokemon, IV = 0, CP = 0, rareList = {}):
    logging.debug("release a Pokemon that (IV < %f and CP < %i)", IV, CP)
    pokemonIV = getIV(pokemon)
    if ((pokemon.pokemon_id in rareList) and 
        (pokemonIV >= rareList[pokemon.pokemon_id])):
        nicknamePokemonIV(session, pokemon)
    if pokemonIV < IV and pokemon.cp < CP:
        logging.info("[" + pokemondic.indexToName(pokemon.pokemon_id) +
            "]\tIV: " + str(pokemonIV) +  
            " CP: " + str(pokemon.cp) + " released")
        session.releasePokemon(pokemon)
        time.sleep(1)
    else:
        nicknamePokemonIV(session, pokemon)

def releaseAllPokemonInCondition(session, IV = 0, CP = 0, rareList = {}):
    logging.debug("release All Pokemon that (IV < %f and CP < %i)", IV, CP)
    for pokemon in session.getPokemons():
        releasePokemonInCondition(session, pokemon, IV, CP, rareList)

# Recycle unused items refer to config.recycleItemList
def tossItems(session):
    logging.debug("toss Items")
    bag = session.getBag()
    itemList = ""
    for itemID in config.recycleItemIDList:
        stock	= session.checkItenQuantity(itemID)
        keep	= config.recycleItemIDList[itemID]
        if(stock > keep):
            session.recycleItem(itemID, stock - keep)
            itemList += (itemdic.indexToName(itemID) + " * " + str(stock - keep) + " ")
    return itemList

# Set an egg to an incubator
def setEgg(session):
    inventory = session.checkInventory()

    # If no eggs, nothing we can do
    if len(inventory["eggs"]) == 0:
        return None

    egg = inventory["eggs"][0]
    incubator = inventory["incubators"][0]
    return session.setEgg(incubator, egg)

# A very brute force approach to evolving
def evolveAllPokemon(session):
    inventory = session.checkInventory()
    for pokemon in inventory.pokemons:
        logging.info(session.evolvePokemon(pokemon))
        time.sleep(1)

# Basic bot
def simpleBot(session, poko_session):
    # Trying not to flood the servers
    cooldown = 1

    # Run the bot
    # releaseAllPokemonInCondition(session,
    #     IV = config.releaseIV, CP = config.releaseCP,
    #     rareList = config.rarePokemonIDList)
    while True:
        try:
            fort = findClosestFort(session)
            if fort is not None:
                walkAndSpin(session, fort)
                cooldown = 1
#                time.sleep(1)
            else:
                time.sleep(5)

        # Catch problems and reauthenticate
        except GeneralPogoException as e:
            logging.critical('GeneralPogoException raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2

        except Exception as e:
            logging.critical('Exception raised: %s', e)
            session = poko_session.reauthenticate(session)
            time.sleep(cooldown)
            cooldown *= 2