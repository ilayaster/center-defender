import os
# Принудительное включение Nearest Neighbor для четкого пиксель-арта
os.environ['SDL_RENDER_SCALE_QUALITY'] = 'nearest'

from core.game import run

if __name__ == "__main__":
    run()