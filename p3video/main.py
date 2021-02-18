#Imports necesarios
from collections import namedtuple
import time
#Herramientas de vision por computador
import cv2
#Utiles creados para el TFG
from tfg_utils import print_progress_bar, encode_h264

#Constantes que definen como ha terminado el programa
ERROR_VIDEO_FILE = 0
SUCCESS = 1

#Tuplas
Vector2D = namedtuple("Vector2D", "x y")
Rectangle = namedtuple("Rectangle", "x y w h")

#Ejecuta el programa principal
def main():
    return

def execute(video_file, input_file, output_width, output_height, output_file, debug = False):
    #Capturador de video
    video_capure = initialize_video(video_file)
    if video_capure is None:
        return ERROR_VIDEO_FILE

    input_content = get_input_file_content(input_file)

    head_positions = parse_positions(input_content)

    video_fps = video_capure.get(cv2.CAP_PROP_FPS)

    temp_file = output_file + ".tmp.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_file, fourcc, video_fps, (output_width, output_height))

    video_width = video_capure.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_height = video_capure.get(cv2.CAP_PROP_FRAME_HEIGHT)

    #Guardamos el numero de fotogramas totales para llevar un seguimiento
    total_frames = int(video_capure.get(cv2.CAP_PROP_FRAME_COUNT))
    total_head_positions = len(head_positions)
    actual_frame = 0

    print("Recortando video original:")

    while video_capure.isOpened():
        #Leemos el siguiente fotograma del video
        success, frame = video_capure.read()

        print_progress_bar(actual_frame, total_head_positions)

        #En caso de que algo falle o no queden fotogramas paramos
        if frame is None or not success or actual_frame >= total_head_positions:
            break
        
        head_position_bounded = get_head_position_bounded(head_positions[actual_frame], output_width, output_height, video_width, video_height)
        
        out.write(frame[head_position_bounded.y:head_position_bounded.y+output_height, head_position_bounded.x:head_position_bounded.x+output_width])
        
        actual_frame += 1

        if debug:
            cv2.rectangle(frame, (head_position_bounded.x,head_position_bounded.y), (head_position_bounded.x+output_width,head_position_bounded.y+output_height), (0,255,0), 2)

            time.sleep(1 / (video_fps * 3))
            
            # Show the image with the rectangles
            frame = cv2.resize(frame, (960, 540))
            cv2.imshow('Preview', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    #Se hace un print para que la consola se escriba correctamente debido a la manera de escribir por pantalla
    #  la barra de progreso
    print()

    # Release the video file
    video_capure.release()
    out.release()
    # Close the window where the image is shown
    cv2.destroyAllWindows()
    
    encode_h264(temp_file, video_file, output_file)

#Devuelve un caputurador de video para sacar los fotogramas del video
def initialize_video(video_file):
    capture = cv2.VideoCapture(video_file)
    #En caso de que el capturador no haya podido abrir el video devolvemos None
    if(not capture.isOpened()): return None
    return capture

def get_input_file_content(input_file):
    input_file = open(input_file, "r")
    return input_file.read().splitlines()

def parse_positions(input_content):
    head_positions = []
    for line in input_content:
        split = line.split(" ")
        position = Vector2D(float(split[0]), float(split[1]))
        head_positions.append(position)
    return head_positions

def get_head_position_bounded(head_position, output_width, output_height, video_width, video_height):    

    head_x = round(head_position.x) - output_width * 0.5
    head_y = round(head_position.y) - output_height * 0.5

    if head_x + output_width > video_width:
        diff = head_x + output_width - video_width
        head_x -= diff

    if head_y + output_height > video_height:
        diff = head_y + output_height - video_height
        head_y -= diff

    if head_x < 0:
        head_x = 0

    if head_y < 0:
        head_y = 0

    return Vector2D(int(head_x), int(head_y))

#Si ejecutamos este script como principal invocamos el metodo Main
if __name__ == '__main__': main()