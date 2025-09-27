import difflib
from pathlib import Path

import pandas as pd



def show_file_diffs(file1: str|Path, file2: str|Path) -> None:
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


def create_parquet(df: pd.DataFrame, table_path:Path) -> None:
    metadata_df = pd.read_excel(
        "/Users/julian/Documents/3 - Bildung/31 - Studium/314 Universität Stuttgart/314.2 Semester 2/Projektarbeit/corpus/metadata.xlsx",
    )

    # Merge file_id and game_id from metadata_df into df based on the 'name' column
    df = df.merge(
        metadata_df[["name", "file_id", "game_id"]],
        on="name",
        how="left",
    )

    df = df[["file_id", "game_id", "name", "line", "token_id", "bytes", "token", "syntax", "language"]]
    df = df.sort_values(by=["game_id", "name", "line", "token_id"])
    df.reset_index(drop=True)

    df.to_parquet(table_path / "tokenized_dataset.parquet", index=False)
    return None
