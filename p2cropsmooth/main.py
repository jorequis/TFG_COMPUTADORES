#Imports necesarios
from collections import namedtuple
import time
#Herramientas de vision por computador
import cv2

import tfg_utils as utils

#Constantes que definen como ha terminado el programa
ERROR_VIDEO_FILE = 0
SUCCESS = 1

#Constante para aproximar la altura de la cabeza
HUMAN_HEAD_RATIO = 7

#Tuplas
Vector2D = namedtuple("Vector2D", "x y")
Rectangle = namedtuple("Rectangle", "x y w h")

#Ejecuta el programa principal
def main():
    return

def execute(input_file, output_file, video_file = None):
    input_file = open(input_file, "r")
    text_lines = input_file.read().splitlines()

    video_width, video_height, video_fps = parse_video_dimensions(text_lines[0])

    rectangles = parse_rectangles(text_lines)

    head_positions = get_head_centers(rectangles)
    smooth_positions = smooth_damp_head_positions(head_positions, video_fps)

    output = open(output_file, "w")

    for position in smooth_positions:
        output.write(f'{position.x} {position.y}\n')

    output.close()

    if not video_file is None:
        show_result_in_video(video_file, head_positions, smooth_positions, video_fps)
    
    return SUCCESS

def parse_video_dimensions(string):
    split = string.split(" ")
    return float(split[0]), float(split[1]), float(split[2])

def parse_rectangles(text_lines):
    rectangles = []
    for i in range(1, len(text_lines)):
        rectangles.append(parse_rectangle(text_lines[i]))
    return rectangles

def parse_rectangle(string):
    split = string.split(" ")
    rect = Rectangle(float(split[1]), float(split[2]), float(split[3]), float(split[4]))
    return rect

#Estima el centro de la cabeza de la persona
def aproximate_head_center(rect):
    return Vector2D(rect.x + rect.w * 0.5, rect.y + rect.y / HUMAN_HEAD_RATIO)

#Devuelve una lista de posiciones aproximadas de la cabeza
def get_head_centers(rectangles):
    head_positions = []
    for rect in rectangles:
        head_center = aproximate_head_center(rect)
        head_positions.append(head_center)
    return head_positions

def smooth_damp_head_positions(head_positions, video_fps):

    smooths = []
    smooth_vector = Vector2D(head_positions[0].x, head_positions[0].y)

    velocity_x = 0
    velocity_y = 0

    smooth_time = 0.50 # 0.085
    delta_time = 1 / video_fps

    for position in head_positions:
        smooth_x, velocity_x = smooth_damp(smooth_vector.x, position.x, velocity_x, smooth_time, delta_time)
        smooth_y, velocity_y = smooth_damp(smooth_vector.y, position.y, velocity_y, smooth_time, delta_time)

        smooth_vector = Vector2D(smooth_x, smooth_y)
        smooths.append(Vector2D(smooth_x, smooth_y))
    return smooths

def smooth_damp(current, target, currentVelocity, smoothTime, deltaTime):
    smoothTime = Max(0.0001, smoothTime)
    num1 = 2 / smoothTime
    num2 = num1 * deltaTime
    num3 = (1.0 / (1.0 + num2 + 0.479999989271164 * num2 * num2 + 0.234999999403954 * num2 * num2 * num2))
    num4 = current - target
    num5 = target
    
    target = current - num4
    num7 = (currentVelocity + num1 * num4) * deltaTime
    currentVelocity = (currentVelocity - num1 * num7) * num3
    num8 = target + (num4 + num7) * num3

    if (num5 - current > 0.0 == num8 > num5):
        num8 = num5
        currentVelocity = (num8 - num5) / deltaTime

    return num8, currentVelocity

def Max(a, b):
    if (a > b):
        return a
    return b

#Devuelve un caputurador de video para sacar los fotogramas del video
def initialize_video(video_file):
    capture = cv2.VideoCapture(video_file)
    #En caso de que el capturador no haya podido abrir el video devolvemos None
    if(not capture.isOpened()): return None
    return capture

def show_result_in_video(video_file, head_positions, smooth_positions, video_fps):
    video_capure = initialize_video(video_file)
    if not video_capure is None:
        frame_index = 0
        while video_capure.isOpened():
            #Leemos el siguiente fotograma del video
            success, frame = video_capure.read()
            #En caso de que algo falle o no queden fotogramas paramos
            if frame is None or not success:
                break

            original_color = (0, 0, 255)
            smooth_color = (0, 255, 0)

            ox, oy = int(head_positions[frame_index].x), int(head_positions[frame_index].y)
            sx, sy = int(smooth_positions[frame_index].x), int(smooth_positions[frame_index].y)

            frame = cv2.rectangle(frame, (ox, oy),(ox + 2, oy + 2), original_color, 20)
            frame = cv2.rectangle(frame, (sx, sy),(sx + 2, sy + 2), smooth_color, 20)
            
            frame = cv2.resize(frame, (960, 540))
            cv2.imshow("Previsualizacion", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_index += 1
            time.sleep(1 / (video_fps * 3))

            if frame_index >= len(head_positions):
                break
            
    # Release the video file
    video_capure.release()
    # Close the window where the image is shown
    cv2.destroyAllWindows()

#Si ejecutamos este script como principal invocamos el metodo Main
if __name__ == '__main__': main()