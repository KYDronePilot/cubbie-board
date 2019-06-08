import os

from PIL import Image

names = os.popen('ls -1a ./logos/converted').read().split('\n')

for name in names:
    if name[0] == '.':
        continue
    image = Image.open('./logos/converted/'+name)
    width, height = image.size
    max_dim = max(width, height)
    background = Image.new('RGB', (max_dim, max_dim), (255,255,255))
    x0 = (max_dim - width)//2
    y0 = (max_dim - height)//2
    background.paste(image, (x0, y0))
    background.save(('./logos/converted/'+name), quality=100)
