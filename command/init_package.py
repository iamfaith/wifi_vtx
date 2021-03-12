import sys
import subprocess


def main():
    # implement pip as a subprocess:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
    'pyroute2', 'future', 'configparser'])