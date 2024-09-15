from copy import deepcopy
import io
import multiprocessing
from os import chdir
from subprocess import getoutput
from functools import partial
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import numpy as np
import wave
import sys


def get_files():
    chdir("Audio Files")
    # chdir("{}\\Audio Files".format(base_path))
    filenames = getoutput("ls").replace("\n", " ").split()[:-1]
    print(filenames)
    source_files = [wave.open(file, "r") for file in filenames if file.find(".wav") != -1]

    return filenames, source_files

def get_files_data(source_files):
    signals = [src.readframes(-1) for src in source_files]
    signals = [np.frombuffer(sig, np.int16) for sig in signals]
    fss = [src.getframerate() for src in source_files]
    durations = [np.linspace(0, len(sig) / fs, num=len(sig)) for sig, fs in zip(signals, fss)]

    return signals, durations

def stop_if_stereo(source_files):
    '''
    No Stereo support
    '''
    if source_files.getnchannels() == 2:
        print("Just mono files")
        sys.exit(0)

def prepare_data(filenames, durations, signals):
    fig, axs = plt.subplots(len(signals), 3, figsize=(len(signals), 3), sharex=True, sharey=True, squeeze=False)
    # axs = axs.flatten()
    axs_packs = [axs.reshape(-1)[y:z] for y, z in zip(range(0, len(signals), 3), range(3, len(signals), 3))]
    # filenames = [element for element in filenames for i in range(3)]
    args = [[x, title, time, sig] for x, title, time, sig in zip(axs_packs, filenames, durations, signals)]
    # print(args)

    return fig, args

def generate_drawing_instances(args):
    pool = multiprocessing.Pool()
    # func = partial(draw_subplot)
    pool.map(draw_subplot, args)
    # pool.close()
    # pool.join()

def draw_subplot(args):
    # fig = plt.figure()
    # axes = plt.axes()
    fig, axs, fileName, time, sig = args
    matplotlib.font_manager._get_font.cache_clear()
    axs.title.set_text(fileName)
    axs[0].bar(time, sig)
    axs[1].scatter(time, sig)
    axs[2].plot(time, sig)
    pil_img = rasterize(fig)

    return pil_img

def rasterize(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    pil_img = deepcopy(Image.open(buf))
    buf.close()
    
    return pil_img

def main(argv):
    filenames, source_files = get_files()
    signals, durations = get_files_data(source_files)
    # [stop_if_stereo(src) for src in source_files]
    fig, args = prepare_data(filenames, durations, signals)
    axs, fileName, time, sig = args[1]
    matplotlib.font_manager._get_font.cache_clear()
    # axs.title.set_text(fileName)
    # axs[0].bar(time, sig)
    axs[1].scatter(time, sig)
    axs[2].plot(time, sig)
    pil_img = rasterize(fig)

    plt.show()
    fig.savefig('talkbursts_audio.png', dpi = 300)

if __name__ == '__main__':
    main(sys.argv)

# #############################
# plt.figure(1)
# plt.title("Signal Wave...")
# plt.plot(signal)
# plt.show()