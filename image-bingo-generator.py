# #########
#  Imports
# #########
import os
import sys
import random
import math
from PIL import Image, ImageOps

# ###########
#  Constants
# ###########
IMAGE_EXTENSIONS = [".jpeg", ".jpg", ".png"]
TARGET_SIZE = (360, 360)
FREE_SPACE_PATH = "FreeSpace.png"
GRID_OVERLAY_PATH = "GridOverlay.png"

# ###########
#  Variables
# ###########
rows = 5
cols = 5
use_free_space = True
crop_images = True
images_path = ""
num_cards = 1


# ###########
#  Functions
# ###########
def to_int(pString):
    if pString == "":
        print("Missing input.")
        return False
    if pString.isdigit():
        return int(pString)
    else:
        print("'" + pString + "' is not a whole number.")
        return False


def to_bool(pString):
    if pString == "":
        print("Missing input.")
        return -1
    first_char = pString[0].lower()
    if first_char == "y":
        return True
    elif first_char == "n":
        return False
    else:
        print("'" + pString + "' is not a yes or no.")
        return -1


def load_images(pPath):
    image_paths = []
    dir_contents = os.listdir(pPath)
    for item in dir_contents:
        if os.path.isfile(pPath + item):
            extension = (os.path.splitext(item)[1]).lower()
            if extension in IMAGE_EXTENSIONS:
                image_paths.append(pPath + item)
    return image_paths


def generate_cards(pNum, pImages, pCardSize):
    cards_generated = []
    while len(cards_generated) < pNum:
        potential_card = random.sample(pImages, pCardSize)
        if potential_card not in cards_generated:
            cards_generated.append(potential_card)
    return cards_generated


def merge_h(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im


def merge_v(im1, im2):
    h = im1.size[1] + im2.size[1]
    w = max(im1.size[0], im2.size[0])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (0, im1.size[1]))

    return im


def overlay(im1, im2):
    im2_scaled = ImageOps.contain(im2, im1.size)
    im1.paste(im2_scaled, (0, 0), im2_scaled)
    return im1


def make_card(pData, pUseFit, pRows, pCols, pFreeSpace):
    scaled_images = []
    for entry in pData:
        with Image.open(entry) as im:
            if pUseFit:
                im_scaled = ImageOps.fit(im, TARGET_SIZE)
            else:
                im_scaled = ImageOps.pad(im, TARGET_SIZE, color="white")
            scaled_images.append(im_scaled)

    if pFreeSpace:
        free_space_idx = (pRows * pCols) // 2
        if os.path.exists(FREE_SPACE_PATH):
            scaled_images.insert(free_space_idx, Image.open(FREE_SPACE_PATH))
        else:
            scaled_images.insert(
                free_space_idx, Image.new("RGBA", TARGET_SIZE, color="white")
            )

    index = 0
    card_image = Image.new("RGBA", (0, 0))
    for y in range(pRows):
        row = scaled_images[index]
        if os.path.exists(GRID_OVERLAY_PATH):
            row = overlay(row, Image.open(GRID_OVERLAY_PATH).convert("RGBA"))
        index += 1
        for x in range(pCols - 1):
            image_to_add = scaled_images[index]
            if os.path.exists(GRID_OVERLAY_PATH):
                image_to_add = overlay(
                    image_to_add, Image.open(GRID_OVERLAY_PATH).convert("RGBA")
                )
            row = merge_h(row, image_to_add)
            index += 1

        card_image = merge_v(card_image, row)

    return card_image


# ##############
#  Main Program
# ##############

# Get inputs
images_path = input("Enter folder path: ")
print()
rows_str = input("Enter number of rows:    ")
cols_str = input("Enter number of columns: ")
print()
use_free_space_str = input("Add free space? [y/n] ")
crop_images_str = input("Crop images? [y/n] ")
print()
num_cards_str = input("Number of cards to generate: ")

print()
print()

# Check for free space and grid overlay images
if not os.path.exists(FREE_SPACE_PATH):
    print("No free space image was found. Using blank square instead.")
    print()


if not os.path.exists(GRID_OVERLAY_PATH):
    print("No grid overlay image was found. Ignoring.")
    print()


# Validate inputs
rows = to_int(rows_str)
cols = to_int(cols_str)
num_cards = to_int(num_cards_str)
use_free_space = to_bool(use_free_space_str)
crop_images = to_bool(crop_images_str)

if (False in [rows, cols, num_cards]) or (-1 in [use_free_space, crop_images]):
    sys.exit(1)

# Search for images
paths_to_images = load_images(images_path)
image_found_count = len(paths_to_images)
print("Found " + str(image_found_count) + " images.")

# Check there are enough images
images_needed = rows * cols
if use_free_space:
    images_needed -= 1

if images_needed > image_found_count:
    print(
        "Not enough images to fill a card. Requires at least "
        + str(images_needed)
        + "."
    )
    sys.exit(1)

# Check if there will be duplicate cards
max_possible_cards = math.perm(image_found_count)
if num_cards > max_possible_cards:
    print(
        "Not enough images to generate "
        + str(num_cards)
        + " cards. Generating "
        + str(max_possible_cards)
        + " instead."
    )
    num_cards = max_possible_cards

# Generate card data
print("Creating card layout(s)...")
cards_data = generate_cards(num_cards, paths_to_images, images_needed)

# Make each card
print("Creating card image(s)...")
cards_images = []
for card in cards_data:
    cards_images.append(make_card(card, crop_images, rows, cols, use_free_space))


# Save the cards as files
print("Saving card file(s)...")
id = 1
for card_image in cards_images:
    card_image.save(str(id) + ".png")
    id += 1

print("Done.")
