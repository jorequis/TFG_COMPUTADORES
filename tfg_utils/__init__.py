import ffmpeg
import sys
import io
from collections import namedtuple
#Herramientas de vision por computador
from cv2 import cv2

#Tuplas
Vector2D = namedtuple("Vector2D", "x y")
Rectangle = namedtuple("Rectangle", "x y w h")

#Devuelve un caputurador de video para sacar los fotogramas del video
def initialize_video(video_file):
    capture = cv2.VideoCapture(video_file)
    #En caso de que el capturador no haya podido abrir el video devolvemos None
    if(not capture.isOpened()): return None
    return capture

#Devuelve un stream en el que se puede escribir
def initialize_output(output_file):
    output = open(output_file, "w")
    return output

#Leemos todo el contenido de un archivo de texto
def get_input_file_content(input_file):
    input_file = open(input_file, "r")
    return input_file.read().splitlines()

# Print iterations progress
def print_progress_bar(actual_frame, total_frames, decimals = 1, length = 100):
    #Caracteres para que quede bonita la barra de progreso
    fill = '█'
    unfill = '-'

    #Porcentaje del progreso segun los valores
    percent = get_process_percent(actual_frame, total_frames, decimals)
    #Numero de caracteres que se van a escribir rellenos
    filled_length = int(length * actual_frame // total_frames)
    #Creamos los caracteres de la barra de progreso
    progress_bar = fill * filled_length + unfill * (length - filled_length)
    #Sacamos la barra de progreso por pantalla
    print(f'\r |{progress_bar}| {percent}%', end = '\r')

#Obtiene el porcentaje completado del procesamiento
def get_process_percent(actual_frame, total_frames, decimals = 1):
    return ("{0:." + str(decimals) + "f}").format(100 * (actual_frame / float(total_frames)))

#Codifica un video en H264 con un archivo de video que da la imagen y otro que de el audio
def encode_h264(clip_video_file, original_video_file, output_file):
    #Cogemos el video del clip de entrada
    video_input = ffmpeg.input(clip_video_file).video
    #Cogemos el audio del video original
    audio_input = ffmpeg.input(original_video_file).audio

    #Cogemos la duracion total del video. Como lo entrega como texto lo pasamos a numero para quitar cifras
    # que no nos valen y lo volvemos a pasar a texto para poder manipularlo
    total_duration = str(float(ffmpeg.probe(original_video_file)['format']['duration']))
    duration_split = total_duration.split('.')
    total_milliseconds = (int(duration_split[0]) * 1000) + (int(duration_split[1]) if len(duration_split) > 0 else 0)

    #Creamos un proceso de codificado y lo ejecutamos asincronamente para seguir el progreso
    stream = ffmpeg.output(audio_input, video_input, output_file, vcodec='h264').overwrite_output()
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)

    #Iniciamos unas variables utiles para seguir el progreso
    finish_transcoding = False
    print("Transcodificando a H264:")
    print_progress_bar(0, total_milliseconds)

    wait_start_transcode(process)
    while not finish_transcoding:
        current_total_milliseconds = get_progress_line(process)
        percent = float(get_process_percent(current_total_milliseconds, total_milliseconds))
        finish_transcoding = percent >= 100
        print_progress_bar(current_total_milliseconds, total_milliseconds)

    print()

#Esperamos a que ffmpeg empiece a transcodificar
def wait_start_transcode(process):
    initial_line_start = 'vbv_delay'
    initial_line_finish = '\\'
    get_output_line(initial_line_start, initial_line_finish, process.stderr)

#Esperamos hasta que ffmpeg escriba en la salida el progreso actual y lo devolvemos
def get_progress_line(process):
    time_length = 16
    time_start = 'time='
    line_start = 'frame='
    line_finish = '\\'
    line = get_output_line(line_start, line_finish, process.stderr)
    
    time_index = line.rfind(time_start)
    time_line = line[time_index:time_index + time_length]
    split_time_line = time_line.split('.')
    current_millisecond = int(split_time_line[1])

    split_time_line = split_time_line[0].split(':')
    current_minute = int(split_time_line[1])
    current_second = int(split_time_line[2])

    current_total_milliseconds = (((current_minute * 60) + current_second) * 1000) + current_millisecond
    return current_total_milliseconds

#Esperamos hasta que ffmpeg escriba en la salida una linea que cumpla los parametros
def get_output_line(starting, ending, stderr):
    get_line_until(starting, stderr)
    second_part_line = get_line_until(ending, stderr)

    return starting + second_part_line

#Analizamos cada caracter que ffmpeg escriba en la salida hasta cumplir el parametro de parada
def get_line_until(ending, stderr):
    line_result = ''
    sequence_acumulated = ''
    character_index = 0
    while sequence_acumulated != ending:
        character = str(stderr.read(1))[2]
        line_result += character
        if character == ending[character_index]:
            sequence_acumulated += character
            character_index += 1
        else:
            sequence_acumulated = ""
            character_index = 0
    return line_result

#pip install ffmpeg-python
#sudo apt  install ffmpeg

#Devuelve el numero mas alto de los dos
def Max(a, b):
    if (a > b):
        return a
    return b