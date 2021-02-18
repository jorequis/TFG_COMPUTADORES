import ffmpeg
import sys
import io

# Print iterations progress
def print_progress_bar (actual_frame, total_frames, decimals = 1, length = 100):
    fill = '█'
    unfill = '-'

    percent = get_process_percent(actual_frame, total_frames, decimals)
    filled_length = int(length * actual_frame // total_frames)
    progress_bar = fill * filled_length + unfill * (length - filled_length)
    print(f'\r |{progress_bar}| {percent}%', end = '\r')

#Obtiene el porcentaje completado del procesamiento
def get_process_percent(actual_frame, total_frames, decimals = 1):
    return ("{0:." + str(decimals) + "f}").format(100 * (actual_frame / float(total_frames)))

def encode_h264(clip_video_file, original_video_file, output_file):
    video_input = ffmpeg.input(clip_video_file).video
    audio_input = ffmpeg.input(original_video_file).audio

    #hacemos doble cast para quitarnos los ceros del final
    total_duration = str(float(ffmpeg.probe(original_video_file)['format']['duration']))
    duration_split = total_duration.split('.')
    total_milliseconds = (int(duration_split[0]) * 1000) + (int(duration_split[1]) if len(duration_split) > 0 else 0)

    stream = ffmpeg.output(audio_input, video_input, output_file, vcodec='h264').overwrite_output()
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)

    time_length = 16
    initial_line_start = 'vbv_delay'
    initial_line_finish = '\\'
    line_start = 'frame='
    line_finish = '\\'
    time_start = 'time='

    finish_transcoding = False
    print("Transcodificando a H264:")
    print_progress_bar(0, total_milliseconds)
    get_output_line(initial_line_start, initial_line_finish, process.stderr)
    while not finish_transcoding:
        line = get_output_line(line_start, line_finish, process.stderr)
        
        time_index = line.rfind('time=')
        time_line = line[time_index:time_index + time_length]
        split_time_line = time_line.split('.')
        current_millisecond = int(split_time_line[1])

        split_time_line = split_time_line[0].split(':')
        current_minute = int(split_time_line[1])
        current_second = int(split_time_line[2])

        current_total_milliseconds = (((current_minute * 60) + current_second) * 1000) + current_millisecond
        finish_transcoding = total_milliseconds == current_total_milliseconds
        print_progress_bar(current_total_milliseconds, total_milliseconds)

    print()

    #print(process.stderr.read(4596))
    #out, err = process.communicate()
    #while True:
        #print(process.stderr.read(99+3-6+3-1))
    #while True:
    #output_line = str(err)
    #time_index = output_line.rfind('time=')
    ##time_line = output_line[time_index:time_index + time_length]
    #split_time_line = time_line.split('.')
    #millis = split_time_line[1]
    #split_time_line = split_time_line[0].split(':')
    #print(split_time_line[1] + " " + split_time_line[2] + " " + millis)

def get_output_line(starting, ending, stderr):
    get_line_until(starting, stderr)
    second_part_line = get_line_until(ending, stderr)

    return starting + second_part_line

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
