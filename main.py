from pathlib import Path

import pandas as pd
from tqdm import tqdm

from scripts.parser import Parser
from scripts.utils import show_file_diffs



def main(source_path : Path, destination_path : Path, table_path : Path | None = None) -> None:
    """Process a directory of C64 BASIC source files, decode each into a ASCII file, and optionally
    generate per-file token tables and a merged table.

    This function iterates over all entries in ``source_path``, decodes each regular file, and writes 
    the decoded BASIC file to ``destination_path`` with an added ".bas" extension. 
    If ``table_path`` is provided, it creates additionally token-tables per file.
    a per-file Excel token table is created and accumulated into a single 
    pandas DataFrame.

    Parameters
    ----------
        source_path : Path
            Directory containing source files to be decoded.
        destination_path : Path
            Directory where the decoded files will be written. Files are named "<source_name>.bas".
        table_path : Path | None, optional
            If provided, an Excel token table "<source_name>.xlsx" is created for each decoded file,
            and the token tables are accumulated for possible merging. If None, no tables are created.
    """

    df = pd.DataFrame()
    parser = Parser()
    files = sorted(source_path.iterdir())

    # Iterate over all files in the source directory
    for source_file in tqdm(files, desc="Parsing Files", ncols=80):
        if source_file.name in (".DS_Store", ".gitkeep") or source_file.is_dir():
            continue

        # create destination path
        dest_file = destination_path / f"{source_file.name}.bas"
        
        # decode the source file with the Parser
        bfile = parser.decode_basic_file(source_file)
        bfile.save_file(dest_file)


        if table_path is not None:
            # create an excel file for each source file with one row per token
            table_file = table_path / f"{source_file.name}.xlsx"
            table = bfile.save_table(table_file)

            table.insert(0, "name", source_file.name)
            df = table if df.empty else pd.concat((df, table), axis=0)
        
    return None



if __name__ == "__main__":

    # Path settings, run it with the default settings for decoding the files in the examples directory
    examples_path = Path(__file__).parent / "examples"
    source_path = examples_path / "encoded"
    destination_path = examples_path / "decoded"
    table_path = examples_path / "tables"  # set to None to omit the Excel file creation

    main(source_path, destination_path, table_path)
