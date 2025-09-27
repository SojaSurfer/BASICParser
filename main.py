from pathlib import Path

import pandas as pd

from scripts.lexer import Lexer
from scripts.tagset import TAGSET
from scripts.utils import create_parquet, show_file_diffs



if __name__ == "__main__":
    corpus_path = Path(
        "/Users/julian/Documents/3 - Bildung/31 - Studium/314 Universität Stuttgart/314.2 Semester 2/Projektarbeit/corpus",
    )
    source_path = corpus_path / "encoded"
    petcat_path = corpus_path / "decoded" / "petcat"
    dest_path = corpus_path / "decoded" / "tokenizer"
    table_path = corpus_path / "dataset"

    examples_path = Path(__file__).parent / "examples"
    source_path = examples_path / "encoded"
    destination_path = examples_path / "decoded"

    df = pd.DataFrame()
    detokenizer = Lexer(TAGSET)


    for source_file in source_path.iterdir():
        if source_file.name in (".DS_Store", ):
            continue

        print(source_file.name)

        dest_file = destination_path / f"{source_file.name}.bas"
        # table_file = table_path / f"{source_file.name}.xlsx"


        bfile = detokenizer.detokenize_basic_file(source_file)

        bfile.save_file(dest_file)
        # table = bfile.save_table(table_file)

        # table.insert(0, "name", source_file.name)
        # df = table if df.empty else pd.concat((df, table), axis=0)
        
        # break

    # print(df)
    # create_parquet(df)