#Controlar el tiempo que tarda en ejecutarse
import time
#Herramientas de vision por computador
import cv2
from pydarknet import Detector as YoloDetector, Image as YoloImage
#Utiles
from collections import namedtuple
#Utiles creados para el TFG
from tfg_utils import print_progress_bar, get_process_percent

#Constantes que definen como ha terminado el programa
ERROR_VIDEO_FILE = 0
SUCCESS = 1

#Constantes para la escritura del archivo de salida
PERSON = 'person'
LOST = 'lost'

#Rectangulo obtenido de una prediccion
Rectangle = namedtuple("Rectangle", "x y w h")

#Ejecuta el programa principal
def main():
    return

#Ejecuta el programa principal
def execute(video_file, config, weights, coco, output_file, debug = False):
    #Capturador de video
    video_capure = initialize_video(video_file)
    if video_capure is None:
        return ERROR_VIDEO_FILE

    #Objeto para escribir el resultado de analizar cada fotograma
    output_stream = initialize_output(output_file)
    
    #Escribimos las dimensiones del video
    write_video_dimensions(video_capure, output_stream)

    #Inicializamos el detector con los parametros recibidos
    detector = YoloDetector(bytes(config, encoding="utf-8"), bytes(weights, encoding="utf-8"), 0, bytes(coco, encoding="utf-8"))

    #Numero de fotogramas iniciales hasta que se encuentra la primera persona
    initial_lost_frames = 0
    initial_person_found = False

    #Guardamos la hora en la que empieza la deteccion para posteriormente calcular el tiempo total de ejecucion
    start_time = time.time()

    #Guardamos el numero de fotogramas totales para llevar un seguimiento
    total_frames = int(video_capure.get(cv2.CAP_PROP_FRAME_COUNT))
    actual_frame = 0

    while video_capure.isOpened():
        #Leemos el siguiente fotograma del video
        success, frame = video_capure.read()
        #En caso de que algo falle o no queden fotogramas paramos
        if frame is None or not success:
            break

        #Aumentamos el numero de fotograma en el que nos encontramos
        actual_frame += 1
            
        #Indica si hemos encontrado una persona en el fotograma actual
        found_person = False

        #Pasamos el detector de Yolo por el fotograma actual
        yolo_frame = YoloImage(frame)
        results = detector.detect(yolo_frame)
        del yolo_frame

        #Interamos por todos los objetos que encuentra para buscar personas
        for category, score, bounds in results:
            decoded_name = str(category.decode("utf-8"))
            #De todos los objetos encontrados solo nos interesan las personas
            if decoded_name == "person":
                #Establecemos el flag a verdadero para que se escriba el nombre correcto en el archivo de salida
                found_person = True
                
                #Obtenemos los parametros del rectangulo y los ajustamos para que el origen sea Arriba Izquierda
                x, y, w, h = bounds
                x = x - w/2
                y = y - h/2

                #Actualizamos el rectangulo con los nuevos valores
                person_rectangle = Rectangle(int(x), int(y), int(w), int(h))

                #Hemos encontrado una persona entonces ya no tenemos que aumentar mas los frames
                initial_person_found = True

                #Salimos del bucle ya que solo nos interesa una persona
                break
        
        #Si aun no se ha encontrado una persona desde el inicio aumentamos el numero de fotogramas incial sin personas
        if not initial_person_found:
            initial_lost_frames += 1
            continue
        #En el momento que se encuentre una persona se escribiran tantas lineas como fotogramas perdidos
        #  con el primer rectangulo encontrado para suplir la falta de informacion inicial
        else:
            if initial_lost_frames > 0:
                for i in range(initial_lost_frames):
                    write_prediction(LOST, person_rectangle, output_stream)
                initial_lost_frames = 0

        #Escribimos en el archivo de salida los datos necesarios
        prediction_name = PERSON if found_person else LOST
        write_prediction(prediction_name, person_rectangle, output_stream)

        #Escribimos por pantalla una barra de progreso
        print_progress_bar(actual_frame, total_frames, decimals=2)

        #En caso de que sea una prueba mostramos una ventana con la informacion que ve el detector
        if debug:
            color = (255, 0, 0) if found_person else (0, 0, 255)
            x, y, w, h = person_rectangle.x, person_rectangle.y, person_rectangle.w, person_rectangle.h
            frame = cv2.rectangle(frame, (x, y),(x + w, y + h), color, 2)
            frame = cv2.putText(frame, prediction_name, (x - 10, y - 10), cv2.FONT_HERSHEY_COMPLEX, 1, color)
            
            frame = cv2.resize(frame, (960, 540))
            cv2.imshow("Previsualizacion", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    #Se hace un print para que la consola se escriba correctamente debido a la manera de escribir por pantalla
    #  la barra de progreso
    print()

    #Obtenemos el tiempo que se ha tardado en procesar el video
    end_time = time.time()
    total_time = end_time - start_time
    percent = get_process_percent(actual_frame, total_frames, 2)
    print(f'Tiempo de procesamiento: {total_time} en completar el {percent}%')

    #En caso de que sea una prueba cerramos todas las ventanas que se hayan abierto
    if debug:
        cv2.destroyAllWindows()

    #Finalizamos el archivo de salida
    output_stream.close()

    #Se termina la ejecucion de manera satisfactoria
    return SUCCESS

#Dibuja en una imagen un rectangulo y la etiqueta de la prediccion
def draw_prediction(img, label, rect, color):
    cv2.rectangle(img, (rect.x, rect.y), (rect.x + rect.w, rect.y + rect.h), color, 2)
    cv2.putText(img, label, (rect.x - 10,rect.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#Devuelve un stream en el que se puede escribir
def initialize_output(output_file):
    output = open(output_file, "w")
    return output

#Devuelve un caputurador de video para sacar los fotogramas del video
def initialize_video(video_file):
    capture = cv2.VideoCapture(video_file)
    #En caso de que el capturador no haya podido abrir el video devolvemos None
    if(not capture.isOpened()): return None
    return capture

#Escribe por la salida las dimensiones del video
def write_video_dimensions(video_capure, output):
    width = video_capure.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video_capure.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = video_capure.get(cv2.CAP_PROP_FPS)
    output.write(f'{width} {height} {fps}\n')

#Escribe por la salida la prediccion con el formato correcto
def write_prediction(label, rect, output):
    output.write(f'{label} {rect.x} {rect.y} {rect.w} {rect.h}\n')

#Si ejecutamos este script como principal invocamos el metodo Main
if __name__ == '__main__': main()