import subprocess

def get_volume():
    """
    returns volume as a percentage
    """
    info = subprocess.check_output(['pactl', 'list', 'sinks']).decode('utf-8')
    lines = info.split('\n')
    volumes = []
    for i in range(len(lines)):
        if lines[i].strip().startswith('Volume: '):
            split = lines[i].split(' ')
            for part in split:
                if '%' in part:
                    volumes.append(part.replace('%', ''))
    # I guess we return the first volume we find?
    return volumes[0]


def set_volume(amt):
    subprocess.call(['pactl', 'set-sink-volume', '0', str(amt) + '%'])

set_volume(50)
