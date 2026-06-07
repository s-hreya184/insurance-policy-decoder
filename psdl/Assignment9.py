#Implement following operations in Python using OpenCV/ PIL :
import cv2 
from PIL import Image, ImageEnhance

def showImage():
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#1] Read an image using OpenCV

img_cv = cv2.imread("image.jpg");
print("Image read using OpenCV \nShape : ", img_cv.shape)

#using PIL
img_pil = Image.open("image.jpg")
print("\nImage Read using PIL \nSize : ", img_pil.size)
print("Mode : ", img_pil.mode)

#2] Display the image using OpenCV

cv2.imshow("Displaying Image : ", img_cv)

showImage()

print("\nImage displayed using OpenCV")

#using PIL 
img_pil.show()
print("\nImage displayed using PIL")

#3] Save the image with a new name using OpenCV

cv2.imwrite("saved_opencv.jpg", img_cv)

print("\nImage saved as 'saved_opencv.jpg' using openCV")

#using PIL

img_pil.save("saved_pil.png")

print("\nImage saved as 'saved_pil.png' using PIL")

#4] Resize an image using openCV

resized_cv = cv2.resize(img_cv, (600,400))

cv2.imwrite("resized_opencv.jpg", resized_cv)

cv2.imshow("Resized", resized_cv)

print("\nImage resized to 600x400 using OpenCV")

showImage()

#using PIL
resize_pil = img_pil.resize((600,400))

resize_pil.save("resized_pil.jpg")

print("\nImage resized to 600x400 using PIL")

resize_pil.show()

#5] Flip an image

#using OpenCV
#1 - horizontally
#0 - vertically

flip_opencv = cv2.flip(img_cv, 1)

cv2.imshow("Flipped", flip_opencv)

print("\nFlipped horizontal using OpenCV")

cv2.imwrite("flipped_opencv.jpg", flip_opencv)

showImage()

#using PIL

flip_pil = img_pil.transpose(Image.FLIP_LEFT_RIGHT)

flip_pil.show()
flip_pil.save("flipped_pil.jpg")
print("\nFlipped horizontally using PIL")

#6] Crop an image
cropped_cv = img_cv[100:300, 200:400]

cv2.imshow("\nCropped", cropped_cv)

print("Cropped using OpenCV")

cv2.imwrite("crop_opencv.jpg", cropped_cv)

showImage()

#using PIL

crop_pil = img_pil.crop((200, 100, 400, 300))

crop_pil.show()
crop_pil.save("crop_pil.jpg")
print("\nCropped using PIL")

#7] Convert into Gray colour

gray_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

cv2.imshow("Gray", gray_cv)

print("\nConverted to Grayscale using OpenCV")

cv2.imwrite("grayscae_cv.jpg", gray_cv)

showImage()

#using pil
gray_cv = img_pil.convert("L")

gray_cv.show()
gray_cv.save("Grayscale_PIL.jpg")
print("\nConverted to grayscale using PIL")

#8] Enhance the image using contrast factor

#using PIL

enhance_img = ImageEnhance.Contrast(img_pil)

high_contrast = enhance_img.enhance(2.0)

high_contrast.show()

high_contrast.save("Enhanced_constrast_PIL.jpg")
print("\nContrast enhancement via PIL done.")

#using OpenCV
clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8,8))

enhanced_cv = clahe.apply(gray_cv)

cv2.imshow("Enhance", enhanced_cv)

print("\nContrast enhancement via CV done")

cv2.imwrite("enhanced_cv.jpg", enhanced_cv)

showImage()