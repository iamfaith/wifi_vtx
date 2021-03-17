import sys
import subprocess
from typing import List
from wfb import register, cmd
apt_cmd = "apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio"

@register(name='{}.init'.format(cmd), description='please init before use')
class InitCommand:

    def execute(self, argv: List) -> bool:
        # implement pip as a subprocess:
        print('pip install')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
        'pyroute2', 'configparser', 'twisted'])
        print('apt install')
        subprocess.check_output(apt_cmd, shell=True, text=True)