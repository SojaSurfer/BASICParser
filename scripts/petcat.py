"""The script extracts & converts d64 files into readable txt files using petcat."""

import os
import shutil
import subprocess
from pathlib import Path



def extractD64Files(vice_bin_path:Path, d64_path:Path, extraction_dir:Path) -> None:
    """Extract all d64 files with c1541 from a source dir to a dest dir.
    
    Parameters
    ----------
        vice_bin_path: Path
            The path to the bin directory of VICE (https://vice-emu.sourceforge.io/).
        d64_path: Path
            The directory of the .d64 files.
        extraction_dir: Path
            The path where the c64 source code files should be stored. A subdirectory for each file is created.
    """

    c1541_path = vice_bin_path / "c1541"
    cwd_files = [file for file in Path().iterdir() if file.is_file()]
    
    for file in d64_path.iterdir():
        
        if file.suffix == ".d64":

            extraction_path = extraction_dir / file.stem
            extraction_path.mkdir(exist_ok=True)

            terminal_cmd = f"{c1541_path} {file} -extract"
            output = subprocess.run(terminal_cmd, capture_output=True, shell=True)

            # ugly: since c1541 will extract all to cwd, the files must be moved to the correct dir afterwards
            for extracted_file in Path().iterdir():
                if extracted_file.is_file() and extracted_file not in cwd_files:
                    shutil.move(extracted_file, extraction_path / extracted_file.name)
            
            if output.stderr:
                print("Error:", output.stderr)
                print(terminal_cmd)
                return None

    return None


def convert_d64_files(vice_bin_path:Path, extraction_dir:Path) -> None:
    """Convert all files without a suffix (c64 source code) to plain txt files using petcat.
    
    Parameters
    ----------
        vice_bin_path : Path
            The path to the bin directory of VICE (https://vice-emu.sourceforge.io/).
        extraction_dir : Path
            The path where the c64 source code files are stored.
    """
    
    petcat_path = vice_bin_path / "petcat"

    for path, dirs, files in extraction_dir.walk():
        for file in files:
            file = Path(file)
            if not (file.suffix or file == ".DS_Store"):
                filepath = (path / file).resolve()

                # conversion
                terminal_cmd = f'{petcat_path} -o "{filepath.with_suffix('.bas')}" -- "{filepath}"'

                output = subprocess.run(terminal_cmd, capture_output=True, shell=True)
                if not output.stderr:
                    filepath.unlink()
                else:
                    print("Error:", output.stderr)
                    print(terminal_cmd)
                    return None


    return None



if __name__ == "__main__":

    vice_bin_path = Path("/Applications/vice-arm64-gtk3-3.9/bin")
    d64_path = Path("d64")
    extraction_dir = Path("corpus")
    extraction_dir.mkdir(exist_ok=True)


    extractD64Files(vice_bin_path, d64_path, extraction_dir)

    convert_d64_files(vice_bin_path, extraction_dir)

