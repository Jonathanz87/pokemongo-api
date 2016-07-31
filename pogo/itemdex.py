class Items(dict):

    # Static Lookups
    UNKNOWN = 0
    POKE_BALL = 1
    GREAT_BALL = 2
    ULTRA_BALL = 3
    MASTER_BALL = 4
    POTION = 101
    SUPER_POTION = 102
    HYPER_POTION = 103
    MAX_POTION = 104
    REVIVE = 201
    MAX_REVIVE = 202
    LUCKY_EGG = 301
    INCENSE_ORDINARY = 401
    INCENSE_SPICY = 402
    INCENSE_COOL = 403
    INCENSE_FLORAL = 404
    TROY_DISK = 501
    X_ATTACK = 602
    X_DEFENSE = 603
    X_MIRACLE = 604
    RAZZ_BERRY = 701
    BLUK_BERRY = 702
    NANAB_BERRY = 703
    WEPAR_BERRY = 704
    PINAP_BERRY = 705
    SPECIAL_CAMERA = 801
    INCUBATOR_BASIC_UNLIMITED = 901
    INCUBATOR_BASIC = 902
    POKEMON_STORAGE_UPGRADE = 1001
    ITEM_STORAGE_UPGRADE = 1002

    def __init__(self):
        super(dict, self).__init__(self)
        attributes = inspect.getmembers(Items, lambda attr :not(inspect.isroutine(attr)))
        for attr in attributes:
            if attr[0].isupper():
                self[attr[1]] = attr[0]
