import cv2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from skimage import measure
import os

# Locations
INPUT_LOCATION = "./input"
OUTPUT_LOCATION = "./output"
FRAMES_LOCATION = "./frames"
# Settings
CAMERA = False
SHOW_LIVE = False
VIDEO_SAVE_FRAMES = True
INTERVAL = 100 # only if animating images

def get_image_contours(image):
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use a non-edge altering denoising filter
    nudge = 0.6
    # Values from https://github.com/kevinjycui/DesmosBezierRenderer/blob/master/backend.py
    median = max(10, min(245, np.median(grey_image)))
    lower = int(max(0, (1 - nudge) * median))
    upper = int(min(255, (1 + nudge) * median))
    filtered = cv2.bilateralFilter(grey_image, 5, 50, 50)
    edged = cv2.Canny(filtered, lower, upper)

    # Find the contours of the objects in the image
    return measure.find_contours(edged, 0.1)


if CAMERA:
    # First camera
    cam = cv2.VideoCapture(0)

    plt.show()
    while True:
        ret, frame = cam.read()

        plt.clf()
        contours = get_image_contours(frame)
        for contour in contours:
            # Flip horizontally so that the top and bottom would be fixed
            flipped_y = -contour[:, 0] + frame.shape[0]
            flipped_x = -contour[:, 1] + frame.shape[1]
            plt.plot(flipped_x, flipped_y, color='red')

        plt.pause(0.0000001)

        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

else:
    # Input files
    input_files = os.listdir(INPUT_LOCATION)
    frames = []
    max_height = 0
    max_width = 0

    # If input is only 1 (and it's a video)
    if len(input_files) == 1 and input_files[0].endswith(".mp4"):
        # Video
        cam = cv2.VideoCapture(os.path.join(INPUT_LOCATION, input_files[0]))
        fps = cam.get(cv2.CAP_PROP_FPS)
        INTERVAL = (fps ** -1) * 1000 # milliseconds/frame

        # If you are going to save frames, delete everything in frames folder first to retain size
        if VIDEO_SAVE_FRAMES:
            for f in os.listdir(FRAMES_LOCATION):
                os.remove(os.path.join(FRAMES_LOCATION, f))

        # If you want to save frames
        currentframe = 0
        while True:
            ret, frame = cam.read()

            # There are still frames left
            if ret:
                # Save images
                if VIDEO_SAVE_FRAMES:
                    print("Creating " + os.path.join(FRAMES_LOCATION, str(currentframe) + ".jpg"))
                    cv2.imwrite(os.path.join(FRAMES_LOCATION, str(currentframe) + ".jpg"), frame)
                    currentframe += 1
                frames.append(frame)
            else:
                break
        cam.release()
        cv2.destroyAllWindows()

    # If multiple images
    else:
        for image in input_files:
            if image.endswith(".png") or image.endswith(".jpg"):
                frames.append(cv2.imread(os.path.join(INPUT_LOCATION, image)))


    frame_contours = []
    # Process frames beforehand
    for frame in frames:
        max_height = max(max_height, frame.shape[0])
        max_width = max(max_width, frame.shape[1])
        print("Processing frame " + str(len(frame_contours)))
        contours = get_image_contours(frame)
        frame_contours.append(contours)


    ### Animate
    fig, ax = plt.subplots()

    def animate(i):
        artists = []
        contours = frame_contours[i]

        plt.cla()
        if not SHOW_LIVE:
            print("Creating frame " + str(i))
        for contour in contours:
            # Flip horizontally so that the top and bottom would be fixed
            flipped_y = -contour[:, 0] + max_height
            ax.set_xlim(0, max_width)
            ax.set_ylim(0, max_height)
            artists.append(ax.plot(contour[:, 1], flipped_y, color='red')[0])
        return artists


    anim = FuncAnimation(fig, animate, frames=len(frame_contours), interval=INTERVAL, blit=True)
    # anim.save(os.path.join(OUTPUT_LOCATION, 'animation.gif'), writer='ffmpeg')
    anim.save(os.path.join(OUTPUT_LOCATION, 'animation.mp4'), writer='ffmpeg')


    def on_key(event):
        if event.key == 'q':
            print("Quit")
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key)
    if SHOW_LIVE:
        plt.show()



# MIGHT BE USEFUL IN THE FUTURE
# image = cv2.imread("./input/3.png")
# contours = get_image_contours(image)

# # Draw the contours on the image
# fig, ax = plt.subplots()
# # ax.imshow(image, cmap='gray')

# for contour in contours:
#     # Flip horizontally so that the top and bottom would be fixed
#     contour = -contour + image.shape[0]
#     ax.plot(contour[:, 1], contour[:, 0], linewidth=2, color='black')

#----

# while True:
#     for filename in os.listdir("./output"):
#         plt.clf()
#         print(filename)

#         image = cv2.imread(f"./output/{filename}")
#         contours = get_image_contours(image)

#         for contour in contours:
#             # Flip horizontally so that the top and bottom would be fixed
#             contour = -contour + image.shape[0]
#             plt.plot(contour[:, 1], contour[:, 0], linewidth=2, color='black')
#         plt.pause(0.0000001)
