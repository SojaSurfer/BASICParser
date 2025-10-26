import difflib
from pathlib import Path



def show_file_diffs(file1: str | Path, file2: str | Path) -> None:
    """Show the file differences between the BASIC decodings from petcat
    and from the Parser.
    """
    
    if isinstance(file1, str):
        file1 = Path(file1)
    if isinstance(file2, str):
        file2 = Path(file2)

    with file1.open("r") as f:
        tokenized = [line.lower() for line in f.readlines()]

    with file2.open("r") as f:
        ground_truth = [line.lower() for line in f.readlines()]

    for file in (tokenized, ground_truth):
        for i, line in enumerate(file):
            while " " in line:
                line = line.replace(" ", "")

            file[i] = line

    diff = difflib.unified_diff(ground_truth, tokenized)
    for line in diff:
        print(line)

    return None
