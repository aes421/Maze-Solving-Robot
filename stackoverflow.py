import cv2
import numpy as np


def centroid(contour):
    x,y,w,h = cv2.boundingRect(contour)
    return (y+h/2.0, x+w/2.0)

def contains_red(red_mask, tile):
    tile_area = np.zeros_like(red_mask)
    cv2.drawContours(tile_area, [tile[1]], 0, 255, -1)
    red_tile_area = cv2.bitwise_and(tile_area, red_mask)
    return (cv2.countNonZero(red_tile_area) > 0)

def get_transform(grid_size, grid_contour):
    x,y,w,h = cv2.boundingRect(grid_contour)
    tile_w = float(w) / (grid_size[0])
    tile_h = float(h)/ (grid_size[1])
    return ((-y - tile_h/2, -x - tile_w/2), (1/tile_h, 1/tile_w))


img = cv2.imread("PaintMaze.png")

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)

cv2.imwrite("out_1.png", np.hstack([h, s, v]))

# Saturation mask to get rid of black
s_mask = cv2.threshold(s, 10, 255, cv2.THRESH_BINARY)[1]

# Pick out blue area
blue_range = [110, 130]
blue_mask = cv2.inRange(h, blue_range[0], blue_range[1])
blue_mask = cv2.bitwise_and(blue_mask, s_mask)


# Pick out blue area
red_range = [[170, 180], [0,10]]
red_mask = cv2.bitwise_or(
    cv2.inRange(h, red_range[0][0], red_range[0][1])
    , cv2.inRange(h, red_range[1][0], red_range[1][1]))
red_mask = cv2.bitwise_and(red_mask, s_mask)

cv2.imwrite("out_2.png", np.hstack([s_mask, blue_mask, red_mask]))


kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# Remove noise
blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
# Fill any small holes
blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)


# Find outer contour, and fill area outside
cnt_grid = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
#assert(len(cnt_grid) == 1)
grid_area = np.zeros_like(blue_mask)
cv2.drawContours(grid_area, cnt_grid, 0, 255, -1)
grid_tiles = cv2.bitwise_and(cv2.bitwise_not(blue_mask), grid_area)

cv2.imwrite("out_3.png", np.hstack([blue_mask, grid_area, grid_tiles]))

# Find contours of our tiles
cnt_tiles = cv2.findContours(grid_tiles.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

# Find scaling parameters
offset, scale = get_transform((11, 11), cnt_grid[0])

tiles = [[centroid(contour), contour, False] for contour in cnt_tiles]
for tile in tiles:
    # Rescale centroid
    tile[0] = (
        int(round((tile[0][0] + offset[0]) * scale[0]))
        , int(round((tile[0][1] + offset[1]) * scale[1]))
    )
    tile[2] = contains_red(red_mask, tile)

# Sort the tiles
tiles = sorted(tiles, key=lambda x: x[0], reverse=False)

# Extract the results
result = np.array([int(t[2]) for t in tiles])

print result.reshape(11,11)