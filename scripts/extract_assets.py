from PIL import Image

im = Image.open('static/assets/s4_fashions_clean.jpg')
width, height = im.size

# Extract the models (women, men, kids)
# The models span roughly:
# X: from 140 to 860
# Y: from 120 to 450
women = im.crop((140, 120, 390, 440))
women.save('static/assets/model_women.png')

men = im.crop((370, 120, 590, 440))
men.save('static/assets/model_men.png')

kids = im.crop((570, 160, 860, 440))
kids.save('static/assets/model_kids.png')

all_models = im.crop((130, 120, 870, 435))
all_models.save('static/assets/all_models.png')

print("Assets extracted successfully!")
