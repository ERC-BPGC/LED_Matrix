from PIL import Image

def lower_resolution(input_path, output_path, new_width, new_height):
    # Open the image
    original_image = Image.open(input_path)

    # Resize the image to the desired resolution
    resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Save the resized image
    resized_image.save(output_path)

# Example usage
input_image_path = "/home/parth/Downloads/tesla.png"
output_image_path = "disp_image.png"
new_width = 20  # Set your desired width
new_height = 40  # Set your desired height

lower_resolution(input_image_path, output_image_path, new_width, new_height)
