itemDic = {	1 : "Poke Ball", 2 : "Great Ball", 3 : "Ultra Ball", 4 : "Master Ball",
		101 : "Potion", 102 : "Super Potion", 103 : "Hyper Potion", 104 : "Max Potion",
		201 : "Revive", 202 : "Max Revive",
		301 : "Lucky Egg",
		401 : "Incense", 402 : "Incense Spicy", 403 : "Incense Cool", 404 : "Incense Floral",
		501 : "Tory Disk",
		602 : "X Attack", 603 : "X Defense", 604 : "X Miracle",
		701 : "Razz Berry", 702 : "Bulk Berry", 703 : "Nanab Berry", 704 : "Wepar Berry", 705 : "Pinap Berry",
		801 : "Special Camera",
		901 : "Incubator Basic Unlimited", 902 : "Incubator Basic",
		1001 : "Pokemon Storage Upgrade", 1002 : "Item Storage Upgrade"}

def indexToName(index):
	if index in itemDic:
		return itemDic[index]
	return None
