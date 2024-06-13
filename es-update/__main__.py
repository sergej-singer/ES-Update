import argparse
from pathlib import Path
import sys
import configparser
import csv

def main(prog_name: str, *argv: str) -> None:
    argp = argparse.ArgumentParser(
        prog=Path(prog_name).name,
        usage="%(prog)s [options] es_path",
    )
    argp.add_argument(
        "-c", "--config",
        type=Path,
        default=Path(),
        help="Config path (default: is current directory)")
    argp.add_argument(
        "es_path",
        type=Path,
        help="Euroscope path")
    
    args = argp.parse_args(argv)

    if not Path.is_file(args.config / 'config.ini'):
        argp.error("Config not found")

    config = configparser.ConfigParser()
    config.read(args.config / 'config.ini')

    es_path = args.es_path

    if not 'LOGIN' in config:
        argp.error("Config is corrupt")

    session_data = {
            'realname':	    config['LOGIN']['Name'],
            'certificate':	config['LOGIN']['CID'],
            'password':	    config['LOGIN']['Password'],
            'rating':	    config['LOGIN']['Rating'],
            'server':	    'AUTOMATIC',
            'tovatsim':	    '1'
        }
    vccs_data = {
            'Ts3NickName':	    config['LOGIN']['CID'],
            'Ts3G2APtt':	    config['VCCS']['PTT'],
            'PlaybackMode':	    config['VCCS']['Mode'],
            'PlaybackDevice':	config['VCCS']['Playback'],
            'CaptureMode':	    config['VCCS']['Mode'],
            'CaptureDevice':	config['VCCS']['Capture']
        }
    hoppie = config['LOGIN']['Hoppie']
    initials = config['LOGIN']['Initials']
    size = config['SETTINGS']['TextSize']       

    for prff in args.es_path.rglob('*.prf'):
        print(f"Processing {prff}")
        prf = []
        i = 0
        
        topsky_path: Path = None
        symbology_path: Path = None
        
        attributes_session = {
            'realname':	    False,
            'certificate':	False,
            'password':	    False,
            'rating':	    False,
            'server':	    False,
            'tovatsim':	    False
        }
        attributes_vccs = {
                'Ts3NickName':	    False,
                'Ts3G2APtt':	    False,
                'PlaybackMode':	    False,
                'PlaybackDevice':	False,
                'CaptureMode':	    False,
                'CaptureDevice':	False

            }

        with prff.open(encoding="iso-8859-1") as f:
            for line in csv.reader(f, delimiter="\t"):
                if not line:
                    prf.append(line)
                    i = i + 1
                    continue

                find_attribute(attributes_session, line, i)
                find_attribute(attributes_vccs, line, i)
                if find_topsky(line):    
                    topsky_path = es_path / find_topsky(line)
                if find_symbology(line):    
                    symbology_path = es_path / find_symbology(line)
                if line[0] == "Settings":
                    update_settings(line, es_path, size)
                update_profiles(line, es_path, initials)

                prf.append(line)
                i = i + 1

        update_symbology(symbology_path, size)
        print(f"    Updated {symbology_path.parts[-1]} with {size}")

        for attribute in attributes_session:        
            prf = add_attribute(
                prf,
                prff,
                'LastSession',
                attribute,
                session_data[attribute],
                attributes_session[attribute]
                )
            
        for attribute in attributes_vccs:        
            prf = add_attribute(
                prf,
                prff,
                'TeamSpeakVccs',
                attribute,
                vccs_data[attribute],
                attributes_vccs[attribute]
                )
        
        if hoppie and topsky_path:
            with (topsky_path / 'TopSkyCPDLChoppieCode.txt').open('w', newline='') as f:
                f.write(hoppie)
                print(f"    Updated TopSkyCPDLChoppieCode.txt with {hoppie}")
    

        with prff.open('w', newline='') as f:
            writer = csv.writer(f, delimiter="\t")
            j = 0

            for line in prf:
                writer.writerow(prf[j])
                j = j + 1



def add_attribute(
        data: list, 
        path: Path, 
        attribute_type1: str, 
        attribute_type2: str, 
        attribute = '', 
        attribute_line = False
        ) -> list:
    """Returns list with added attributes and data."""

    if not attribute_line:
        data.append([attribute_type1, attribute_type2, attribute])
        print(f"    Added {attribute_type2} with {data[-1][2]}")
        return data

    try:
        data[attribute_line][2] = attribute
    except:
        data[attribute_line].append(attribute)

    print(f"    Updated {attribute_type2} with {data[attribute_line][2]}")
    return data

def find_attribute(attribute_type2: dict, line: list, i: int) -> bool:
    """Checks line of the file for attribute. Returns lines, where the given attributes were found."""
    for attribute in attribute_type2:      
        if line[1] == attribute:
            attribute_type2[attribute] = i
            return True

    return False

def find_topsky(line: list) -> Path:
    """Returns TopSky Path if finds it in given line"""
         
    if not line[0] == 'Plugins':
        return None
    
    path = Path(line[2])
    path = Path(*path.parts[1:])

    if path == Path('.'):
        return None
    
    if path.parts[-1] == 'TopSky.dll':
        return Path(*path.parts[:-1])
    
def find_symbology(line: list) -> Path:
    """Returns Settings Path if finds it in given line"""
         
    if not line[0] == 'Settings':
        return None
    
    if not line[1] == 'SettingsfileSYMBOLOGY':
        return None
    
    path = Path(line[2])
    path = Path(*path.parts[1:])
    
    return path

def update_settings(line: list, es_path: Path, size: str) -> None:
    """Updates Settings file with given Text Sizes."""

    settings = []
    i = 0
    setting_except = [
        'alias',
        'AtisFolder',
        'airlines',
        'airports',
        'aircraft',
        'airways',
        'airportcoords',
        'AselKey',
        'FreqKey',
        'sector',
        'AtisFolder',
        'SettingsfileSYMBOLOGY',
        'SettingsfileVOICE',
        'Settingsfile',
        'SettingsfilePROFILE',
        'SettingsfileTAGS',
        'SettingsfileSCREEN',
        'SettingsfileVCCS'
        ]
    
    if size == '':
        return None

    for setting in setting_except:
        if line[1] == setting:
            return None
    
    path = Path(line[2])
    path = Path(*path.parts[1:])

    if path == Path('.'):
        return None
        
    path = es_path / path

    with path.open(encoding="iso-8859-1") as f:
        for line in csv.reader(f, delimiter=':'):
            settings.append(line)

    for line in settings:
        if not line:
            i = i + 1
            continue

        if not settings[i][0] == 'm_Column':
            i = i + 1
            continue

        if settings[i][-1] == '0.0':
            i = i + 1
            continue
            
        settings[i][-1] = size
        i = i + 1
        
    with path.open('w', newline='') as f:
        writer = csv.writer(f, delimiter=":")
        j = 0

        for line in settings:
            writer.writerow(settings[j])
            j = j + 1

    print(f"    Updated {path.parts[-1]} with {size}")
    return None

def update_profiles(line: list, es_path: Path, initials: str) -> None:
    """Updates OBS Profile in Profiles file with given Initials."""

    settings = []
    i = 0
        
    if initials == '':
        return None

    if not line[1] == 'SettingsfilePROFILE':
        return None
    
    path = Path(line[2])
    path = Path(*path.parts[1:])

    if path == Path('.'):
        return None
        
    path = es_path / path

    with path.open(encoding="iso-8859-1") as f:
        for line in csv.reader(f, delimiter=':'):
            settings.append(line)

    for line in settings:
        if not line:
            i = i + 1
            continue

        if not settings[i][0] == 'PROFILE':
            i = i + 1
            continue

        try:
            if not settings[i][1].endswith('_OBS'):
                i = i + 1
                continue

            settings[i][1] = initials + '_OBS'
        except:
            i = i + 1
            continue
        
        i = i + 1
        
    with path.open('w', newline='') as f:
        writer = csv.writer(f, delimiter=":")
        j = 0

        for line in settings:
            writer.writerow(settings[j])
            j = j + 1

    print(f"    Updated {path.parts[-1]} with {initials}_OBS")
    return None
    
def update_symbology(symbology_path: Path, size: str) -> None:
    """Updates Symbology Settings file with given Text Sizes."""

    settings = []
    rows1 = range(25, 63)
    rows2 = [86, 87, 88, 90, 92, 93]
    
    if size == '':
        return None

    with symbology_path.open(encoding="iso-8859-1") as f:
        for line in csv.reader(f, delimiter=':'):
            settings.append(line)
    
    if not 'SYMBOLOGY' in settings[0][0]:
        raise Exception("Symbology Settings file is corrupt")
    if not 'SYMBOLSIZE' in settings[1][0]:
        raise Exception("Symbology Settings file is corrupt")
    
    for row in rows1:
        settings[row][3] = size
    for row in rows2:
        settings[row][3] = size

    with symbology_path.open('w', newline='') as f:
        writer = csv.writer(f, delimiter=":")
        j = 0

        for line in settings:
            writer.writerow(settings[j])
            j = j + 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv))