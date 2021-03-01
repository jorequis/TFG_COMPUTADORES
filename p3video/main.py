#Imports necesarios
import time
#Herramientas de vision por computador
from cv2 import cv2
#Utlies comunes a todo el proyecto
from tfg_utils import print_progress_bar, encode_h264, initialize_video, get_input_file_content, Vector2D, Rectangle

#Constantes que definen como ha terminado el programa
ERROR_VIDEO_FILE = 0
SUCCESS = 1

#Ejecuta el programa principal
def main():
    return

#Ejecuta el programa principal
def execute(video_file, input_file, output_width, output_height, output_file, debug = False):
    #Capturador de video
    video_capure = initialize_video(video_file)
    if video_capure is None:
        return ERROR_VIDEO_FILE

    #Leemos el archivo de texto de entrada
    input_content = get_input_file_content(input_file)
    #Obtenemos las posiciones de la parte anterior
    head_positions = parse_positions(input_content)
    #Obtenemos los fps del video original para escribir el resultado con la misma tasa
    video_fps = video_capure.get(cv2.CAP_PROP_FPS)
    #Nombre del archivo temporal
    temp_file = output_file + ".tmp.mp4"

    #Codificamos un video recortado con las posiciones de entrada
    # este video no tiene audio
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_file, fourcc, video_fps, (output_width, output_height))

    #Dimensiones del video original para limitar el recorte
    video_width = video_capure.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_height = video_capure.get(cv2.CAP_PROP_FRAME_HEIGHT)

    #Guardamos el numero de fotogramas totales para llevar un seguimiento
    total_head_positions = len(head_positions)
    actual_frame = 0

    print("Recortando video original:")

    while video_capure.isOpened():
        #Leemos el siguiente fotograma del video
        success, frame = video_capure.read()
        #Escribimos por pantalla la barra de progreso
        print_progress_bar(actual_frame, total_head_positions)

        #En caso de que algo falle o no queden fotogramas paramos
        if frame is None or not success or actual_frame >= total_head_positions:
            break
        
        #Limitamos la posicion actual para que no recorte fuera del video
        head_position_bounded = get_head_position_bounded(head_positions[actual_frame], output_width, output_height, video_width, video_height)
        #Escribimos el fotograma recortado
        out.write(frame[head_position_bounded.y:head_position_bounded.y+output_height, head_position_bounded.x:head_position_bounded.x+output_width])
        
        #Llevamos un seguimiento del fotograma para la barra de progreso
        actual_frame += 1

        #Mostramos el resultado en una ventana
        if debug:
            cv2.rectangle(frame, (head_position_bounded.x,head_position_bounded.y), (head_position_bounded.x+output_width,head_position_bounded.y+output_height), (0,255,0), 2)

            time.sleep(1 / (video_fps * 3))
            
            # Show the image with the rectangles
            frame = cv2.resize(frame, (960, 540))
            cv2.imshow('Previsualizacion', frame)
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
    
    #Codificamos el video final con el video recortado sumado al audio del video original
    encode_h264(temp_file, video_file, output_file)

#Array de posiciones obtenidas del archivo de entrada
def parse_positions(input_content):
    head_positions = []
    for line in input_content:
        split = line.split(" ")
        position = Vector2D(float(split[0]), float(split[1]))
        head_positions.append(position)
    return head_positions

#Reposiciona una posicion para que el rectangulo de recorte no se salga de las dimensiones del video
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