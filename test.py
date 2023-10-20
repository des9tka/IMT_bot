from PIL import Image, ImageFilter


work_image = Image.open('work_image.jpg')

blured_image = work_image.filter(ImageFilter.GaussianBlur(5))
blured_image.save('blurred_image.jpg')