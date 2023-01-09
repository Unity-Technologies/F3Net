from PIL import Image
import os
# Set the size of the resized images
width = 128
height = 128

# Set the input and output directories
input_dir = 'input'
output_dir = 'output'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Loop through the input directory
for file in os.listdir(input_dir):
    # Open the image file
    with Image.open(os.path.join(input_dir, file)) as im:
        # Resize the image
        im_resized = im.resize((width, height), Image.BICUBIC)
        # Save the resized image
        im_resized.save(os.path.join(output_dir, file))
