import os
import shutil
import subprocess
import argparse

def get_video_codec(input_file):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении кодека для {input_file}: {e}")
        print(f"Подробности ошибки: {e.stderr.decode()}")
        return None

def convert_video(input_file, output_file):
    try:
        subprocess.run(
            ['ffmpeg', '-i', input_file, '-vcodec', 'libx264', '-preset', 'veryslow', '-crf', '18', output_file],
            check=True
        )
        print(f"Преобразование {input_file} завершено успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при преобразовании {input_file}: {e}")
        print(f"Подробности ошибки: {e.stderr.decode()}")

def process_videos(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"Ошибка: входная папка '{input_folder}' не существует.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Выходная папка '{output_folder}' была создана.")

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            
            codec_name = get_video_codec(input_file)
            
            if codec_name == 'vp9':
                # Если видео закодировано в VP9, преобразуем в H.264
                convert_video(input_file, output_file)
            elif codec_name == 'h264':
                # Если видео уже закодировано в H.264, просто копируем файл
                shutil.copy(input_file, output_file)
                print(f"{input_file} уже закодировано в H.264, копирование в {output_file}.")
            elif codec_name:
                print(f"Кодек для {input_file} не поддерживается для преобразования.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Преобразование видео из кодека VP9 в кодек H.264.')
    parser.add_argument('input_folder', type=str, help='Путь к папке с исходными видеофайлами.')
    parser.add_argument('output_folder', type=str, help='Путь к папке для сохранения преобразованных видеофайлов.')

    args = parser.parse_args()

    input_folder = os.path.abspath(args.input_folder)
    output_folder = os.path.abspath(args.output_folder)

    print(f"Входная папка: {input_folder}")
    print(f"Выходная папка: {output_folder}")

    process_videos(input_folder, output_folder)
