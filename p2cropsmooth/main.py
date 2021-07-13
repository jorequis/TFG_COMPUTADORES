#Imports necesarios
import time
#Herramientas de vision por computador
from cv2 import cv2
#Utlies comunes a todo el proyecto
from tfg_utils import initialize_output, initialize_video, get_input_file_content, Vector2D, Rectangle, Max

#Constantes que definen como ha terminado el programa
ERROR_VIDEO_FILE = 0
SUCCESS = 1

#Constante para aproximar la altura de la cabeza
HUMAN_HEAD_RATIO = 7

#Ejecuta el programa principal
def main():
    return

#Ejecuta el programa principal
def execute(input_file, output_file, video_file = None):
    #Leemos el archivo de texto de entrada
    text_lines = get_input_file_content(input_file)
    #Obtenemos datos sobre el video original
    video_width, video_height, video_fps = parse_video_dimensions(text_lines[0])

    #Guardamos la hora en la que empieza la deteccion para posteriormente calcular el tiempo total de ejecucion
    start_time = time.time()

    #Parseamos las lineas de texto en tuplas de rectangulos para manipularlos
    rectangles = parse_rectangles(text_lines)
    #Estimamos la posicion de la cabeza en cada uno de los rectangulos
    head_positions = get_head_centers(rectangles)
    #Suavizamos las posiciones de la cabeza
    smooth_positions = smooth_damp_head_positions(head_positions, video_fps)

    #Escribimos todas las posiciones suavizadas en el archivo de salida
    write_output(output_file, smooth_positions)

    #Obtenemos el tiempo que se ha tardado en procesar el video
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Tiempo de procesamiento Smooth: {total_time}')

    #Mostramos los resultados en pantalla (en caso de que haya un video de entrada)
    show_result_in_video(video_file, head_positions, smooth_positions, video_fps)
    
    #Se termina la ejecucion de manera satisfactoria
    return SUCCESS

#Escribe el archivo de salida
def write_output(output_file, smooth_positions):
    #Inicializamos el archivo de salida
    output = initialize_output(output_file)
    #Escribimos todas las posiciones en el archivo de salida
    for position in smooth_positions:
        output.write(f'{position.x} {position.y}\n')
    #Finalizamos el archivo de salida
    output.close()

#Devuelve los datos basicos del video guardados en el archivo (ancho, alto, fps)
def parse_video_dimensions(string):
    split = string.split(" ")
    return float(split[0]), float(split[1]), float(split[2])

#Array de rectangulos obtenidos del archivo de entrada
def parse_rectangles(text_lines):
    rectangles = []
    for i in range(1, len(text_lines)):
        rectangles.append(parse_rectangle(text_lines[i]))
    return rectangles

#Crea un rectangulo definido en un string (nombre, x, y, ancho, alto)
def parse_rectangle(string):
    split = string.split(" ")
    rect = Rectangle(float(split[1]), float(split[2]), float(split[3]), float(split[4]))
    return rect

#Devuelve una lista de posiciones aproximadas de la cabeza
def get_head_centers(rectangles):
    head_positions = []
    for rect in rectangles:
        head_center = aproximate_head_center(rect)
        head_positions.append(head_center)
    return head_positions

#Estima el centro de la cabeza de la persona
def aproximate_head_center(rect):
    return Vector2D(rect.x + rect.w * 0.5, rect.y + rect.y / HUMAN_HEAD_RATIO)

#Interpreta una lista de posiciones y devuelve una camara virtual que las sigue
def smooth_damp_head_positions(head_positions, video_fps):
    #Resultado
    smooths = []

    #Ultima posicion para cogerla como referencia para calcular la siguiente
    last_smooth = Vector2D(head_positions[0].x, head_positions[0].y)
    #Velocidad de movimiento de la camara virtual
    velocity_x = 0
    velocity_y = 0

    #Ajustes para determinar la suavidad del resultado
    smooth_time = 0.50 # 0.085
    delta_time = 1 / video_fps

    #Iteramos por cada posicion para realizar el seguimiento
    for position in head_positions:
        smooth_x, velocity_x = smooth_damp(last_smooth.x, position.x, velocity_x, smooth_time, delta_time)
        smooth_y, velocity_y = smooth_damp(last_smooth.y, position.y, velocity_y, smooth_time, delta_time)

        last_smooth = Vector2D(smooth_x, smooth_y)
        smooths.append(Vector2D(smooth_x, smooth_y))

    #Devolvemos el resultado
    return smooths

#Algoritmo de suavizado de seguimiento basado en Spring Damp
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

#Muestra una previsualizacion del resultado
def show_result_in_video(video_file, head_positions, smooth_positions, video_fps):
    if video_file is None:
        return
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