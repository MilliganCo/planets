"""Параметры конфигурации falling sand симулятора."""

# Размеры сетки (увеличено в 1.5 раза)
W = 330
H = 210

# Скорость симуляции (уменьшено для лучшей производительности)
TICKS_PER_FRAME = 1  # Количество тиков на кадр
MIN_TICKS_PER_FRAME = 1
MAX_TICKS_PER_FRAME = 5  # Уменьшено для стабильности FPS

# Вероятности и параметры
P_IGNITE = 0.25  # Вероятность зажигания дерева от огня

# Параметры жизни материалов
FIRE_LIFE_MIN = 8
FIRE_LIFE_MAX = 18
SMOKE_LIFE_MIN = 25
SMOKE_LIFE_MAX = 60

# Новые материалы - параметры жизни
STEAM_LIFE_MIN = 30
STEAM_LIFE_MAX = 80
EMBER_LIFE_MIN = 40
EMBER_LIFE_MAX = 100
LAVA_LIFE_MIN = 100
LAVA_LIFE_MAX = 300
GAS_LIFE_MIN = 50
GAS_LIFE_MAX = 150
ASH_LIFE_MIN = 20
ASH_LIFE_MAX = 50
MOLTEN_METAL_LIFE_MIN = 80
MOLTEN_METAL_LIFE_MAX = 200

# Вероятности взаимодействий
P_OIL_IGNITE = 0.4  # Вероятность зажигания масла от огня
P_EMBER_IGNITE = 0.3  # Вероятность зажигания дерева угольками
P_LAVA_IGNITE = 0.6  # Вероятность зажигания дерева лавой
P_ICE_MELT = 0.5  # Вероятность таяния льда от огня/лавы
P_ACID_DISSOLVE = 0.2  # Вероятность разъедания материала кислотой
P_GAS_EXPLODE = 0.8  # Вероятность взрыва газа от огня
P_STEAM_CONDENSE = 0.05  # Вероятность конденсации пара в воду
P_SNOW_MELT = 0.3  # Вероятность таяния снега от огня/лавы
P_ASH_TO_SOIL = 0.4  # Вероятность превращения пепла в почву при контакте с водой
P_PLANT_GROW = 0.01  # Вероятность роста растения на почве/воде
P_SALT_DISSOLVE = 0.5  # Вероятность растворения соли в воде
P_CEMENT_HARDEN = 0.6  # Вероятность затвердевания цемента при контакте с водой
P_METAL_MELT = 0.7  # Вероятность плавления металла от лавы

# Параметры течения воды
WATER_FLOW_DISTANCE = 3  # Максимальная дальность бокового течения воды

# Размер пикселя (масштаб отрисовки)
PIXEL_SIZE = 4  # Каждая клетка = 4x4 пикселя на экране

# Размеры окна
WINDOW_WIDTH = W * PIXEL_SIZE
WINDOW_HEIGHT = H * PIXEL_SIZE

# Параметры кисти
BRUSH_MIN_RADIUS = 1
BRUSH_MAX_RADIUS = 12
BRUSH_DEFAULT_RADIUS = 3

# Направления гравитации
GRAVITY_DOWN = (0, 1)
GRAVITY_LEFT = (-1, 0)
GRAVITY_RIGHT = (1, 0)
GRAVITY_UP = (0, -1)

GRAVITY_MODES = [
    ("Down", GRAVITY_DOWN),
    ("Left", GRAVITY_LEFT),
    ("Right", GRAVITY_RIGHT),
    ("Up", GRAVITY_UP),
]

# Ветер (смещение для дыма)
WIND_NONE = (0, 0)
WIND_LEFT = (-1, 0)
WIND_RIGHT = (1, 0)

WIND_MODES = [
    ("None", WIND_NONE),
    ("Left", WIND_LEFT),
    ("Right", WIND_RIGHT),
]

