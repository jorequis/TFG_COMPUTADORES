#Importa la libreria para obtener los argumentos necesarios
import argparse
#Acceso a variables usadas por el interpretador
import sys, os

#Imports para cada uno de los modulos
import p1yolo
import p2cropsmooth
import p3video

import cv2
import ffmpeg

#Mensaje con el modo de empleo
USAGE = 'Modo de empleo: -v VÍDEO [OPCIÓN]... [FICHERO]...'

#Extension de los archivos
P1EXT = '.txt'
P2EXT = '.txt'
P3EXT = '.mp4'

#Ruta del programa
path = os.path.dirname(os.path.realpath(__file__)) + '/'

#Array que contiene tuplas con los argumentos
arguments = [
    ('-v', '--video',    False,  'Ruta del video de entrada', path + '../VIDEOS/video4k.mp4'),
    ('-c', '--config',   False, 'path to yolo config file', path + '/p1yolo/cfg/yolov3-tiny.cfg'),
    ('-w', '--weights',  False, 'path to yolo pre-trained weights', path + '/p1yolo/weights/yolov3-tiny.weights'),
    ('-cl', '--classes', False, 'path to text file containing class names', path + '/p1yolo/cfg/coco.data'),
    ('-o1', '--output1', False, 'path to text file containing class names', path + '/p1_output_from_main'),
    ('-o2', '--output2', False, 'path to text file containing class names', path + '/p2_output_from_main'),
    ('-o3', '--output3', False, 'path to text file containing class names', path + '/p3_output_from_main')
]

#Ejecuta el programa principal
def main():
    #Obtenemos los argumentos del programa
    args = get_arguments()
    #Cambiamos las rutas relativas a absolutas
    args.video = os.path.realpath(args.video)
    args.config = os.path.realpath(args.config)
    args.weights = os.path.realpath(args.weights)
    args.classes = os.path.realpath(args.classes)
    args.output1 = os.path.realpath(args.output1) + P1EXT
    args.output2 = os.path.realpath(args.output2) + P2EXT
    args.output3 = os.path.realpath(args.output3) + P3EXT

    #Cambiamos el directorio de trabajo a la ruta del programa para que funcionen las rutas relativas
    os.chdir(path)

    #p1_code = p1yolo.execute(args.video, args.config, args.weights, args.classes, args.output1, True)

    #p2_code = p2cropsmooth.execute(args.output1, args.output2, args.video)
    
    p3video.execute(args.video, args.output2, 720, 480, args.output3)

#Obtiene los argumentos definidos
def get_arguments():    
    #Inicializamos
    argument_parser = argparse.ArgumentParser()
    #Sobreescribimos la funcion que escribe un error por pantalla para que escriba lo que nosotros queremos
    argument_parser.error = lambda message: arguments_error(argument_parser, message)
    argument_parser.print_help = lambda file=None: print_help()

    #Definimos los argumentos
    for argument in arguments:
        argument_parser.add_argument(argument[0], argument[1], required=argument[2], help=argument[3], default=argument[4])

    return argument_parser.parse_args()

#Escribe por pantalla el error que ha producido los argumentos
def arguments_error(argument_parser, message):
    try_message = 'Pruebe el argumento "--help" para más información.'
    argument_parser.exit(2, '{message}\n{try_message}\n'.format(message=message, try_message=try_message))

#Escribe por pantalla el uso del programa
def print_help():
    print(USAGE)

    print('\nArgumentos obligatorios')
    for argument in arguments:
        if argument[2]:
            print_argument(argument)

    print('\nArgumentos opcionales')
    for argument in arguments:
        if not argument[2]:
            print_argument(argument)

#Escribe por pantalla el uso de un argumento
def print_argument(argument):
    prefix = '  {a}, {b}'.format(a=argument[0], b=argument[1])
    print('{prefix}{indent}{message}'.format(prefix=prefix, indent=" " * (25 - len(prefix)), message=argument[3]))

#Si ejecutamos este script como principal invocamos el metodo Main
if __name__ == '__main__': main()