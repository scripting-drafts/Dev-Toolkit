from copy import deepcopy
from fileinput import filename
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
    filenames = [file for file in filenames if file.find(".wav") != -1]
    print(filenames)
    source_files = [wave.open(file, "r") for file in filenames]

    return filenames, source_files

def get_files_data(source_files):
    signals = [src.readframes(-1) for src in source_files]
    signals = [np.frombuffer(sig, np.int16) for sig in signals]
    fss = [src.getframerate() for src in source_files]
    durations = [np.linspace(0, len(sig) / fs, num=len(sig)) for sig, fs in zip(signals, fss)]

    return signals, durations, fss

def stop_if_stereo(source_files):
    '''
    No Stereo support
    '''
    if source_files.getnchannels() == 2:
        print("Just mono files")
        sys.exit(0)

def prepare_data(filenames, durations, fss, signals):
    fig, axs = plt.subplots(len(signals), 3, figsize=(18, 36), squeeze=False)
    # axs = axs.flatten()
    axs_packs = [axs.reshape(-1)[y:z] for y, z in zip(range(0, len(axs.reshape(-1)) + 1, 3), range(3, len(axs.reshape(-1)) + 1, 3))]
    # filenames = [element for element in filenames for i in range(3)]
    args = [[x, title, time, fs, sig] for x, title, time, fs, sig in zip(axs_packs, filenames, durations, fss, signals)]
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
    fig, axs, fileName, fs, time, sig = args
    matplotlib.font_manager._get_font.cache_clear()
    axs.title.set_text(fileName)
    # axs[0].bar(time, sig)
    axs[1].specgram(sig, fs)
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
    signals, durations, fss = get_files_data(source_files)
    # [stop_if_stereo(src) for src in source_files]
    fig, args = prepare_data(filenames, durations, fss, signals)
    
    for x in args:
        axs, filename, time, fs, sig = x
        matplotlib.font_manager._get_font.cache_clear()
        if axs[0].title.get_text() == '':
            # axs[0].xaxis.set_label_position('top')
            # axs[0].set_xlabel('X-label')
            axs[0].spines.bottom.set_visible(False)
            axs[0].spines.left.set_visible(False)
            axs[0].spines.right.set_visible(False)
            axs[0].spines.top.set_visible(False)
            axs[0].axes.xaxis.set_ticklabels([])
            axs[0].axes.yaxis.set_ticklabels([])
            axs[0].set_xticks([])
            axs[0].set_yticks([])

            title = "{}\nMin: {}, Max: {}, Dominant: {}\nPESQ: {}".format(filename, None, None, None, None)
            axs[0].set_title(title, y=0.5, pad=-14, fontsize=7, loc="left")
            # axs[0].title.set_text(fileName)
        # axs[0].bar(time, sig)
        axs[1].specgram(sig, fs)
        # major_ticks_1 = np.arange(0, time[-1], 2)
        # minor_ticks_1 = np.arange(-1, 1, .25)
        # axs[1].set_xticks(major_ticks_1)
        # axs[2].set_xticks(minor_ticks_1, minor=True)
        # axs[1].set_yticks(major_ticks_1)
        # axs[2].set_yticks(minor_ticks_1, minor=True)
        axs[1].axes.xaxis.set_ticklabels([])
        axs[1].axes.yaxis.set_ticklabels([])

        axs[2].plot(time, sig)
        # major_ticks_2_x = np.arange(0, time.reshape(-1)[-1], 2)
        # minor_ticks_2_x = np.arange(0, time.reshape(-1)[-1], 2)
        # major_ticks_2_y = np.arange(-1, 1, .25)
        # minor_ticks_2_y = np.arange(-1, 1, .25)
        # axs[2].set_yticks(major_ticks_2_x)

        # axs[2].set_xticks(minor_ticks_2_x, minor=True)
        # axs[2].set_yticks(major_ticks_2_y)
        
        axs[2].set_yticks(np.arange(-1, 1, .5), minor=True)
        axs[2].axes.xaxis.set_ticklabels([])
        axs[2].axes.yaxis.set_ticklabels([])
    
    pil_img = rasterize(fig)
    fig.tight_layout()
    # fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.show()
    fig.savefig('talkbursts_audio.png', dpi=720)    #bbox_inches='tight'

if __name__ == '__main__':
    main(sys.argv)

# #############################
# plt.figure(1)
# plt.title("Signal Wave...")
# plt.plot(signal)
# plt.show()