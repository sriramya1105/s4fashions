from PIL import Image

im = Image.open('static/assets/asset_sheet.png')
# Total size: 1024 x 576

# 1. Logo (top left)
logo = im.crop((24, 16, 286, 172))
logo.save('static/assets/asset_logo.png')

# 2. Top Wave Decoration
top_wave = im.crop((300, 16, 620, 172))
top_wave.save('static/assets/asset_top_wave.png')

# 3. Bottom Wave Decoration
bottom_wave = im.crop((630, 20, 990, 165))
bottom_wave.save('static/assets/asset_bottom_wave.png')

# 4. Women Model
women = im.crop((10, 230, 182, 600 if 600 < 576 else 348))
# Wait, let's look closer at the Y coordinates of models row
# The models row is in the middle:
# Y is roughly from 220 to 600? Let's check with vertical slices.
