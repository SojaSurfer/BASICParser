# BASICParser

![Python version](https://img.shields.io/badge/python-3.12%2B-blue)

This repository contains scripts for decoding [Commodore 64 BASIC](https://en.wikipedia.org/wiki/Commodore_BASIC) source files and converting them into lexical tokens in ASCII format. The parser includes a syntax tagger that classifies tokens according to their functional properties in the BASIC language.

## Features

- **Stateful parsing** of tokenized C64 BASIC files
- **PETSCII to ASCII conversion** with proper encoding handling
- **Syntax tagging** system for token classification
- **Context-aware disambiguation** (variables, operators, commands)
- **Token chunking** for multi-byte sequences (e.g., `<=`, variable names)
- **Assembly detection** in DATA statements
- **Excel export** for token analysis

## Getting Started

### Prerequisites

- Python 3.12+
- Required packages: `pandas`, `tqdm`, `openpyxl`

### Example Use

Run the parser with the [main.py](../blob/main/main.py) script to decode files in the `examples` directory:

```bash
python main.py
```

This will:

- Read tokenized BASIC files from `examples/encoded/`
- Save decoded ASCII files to `examples/decoded/` (with `.bas` extension)
- Generate token analysis tables in `examples/tables/` (Excel format)

## Citation

```bibtex
@software{wagner2025basicparser,
  author = {Wagner, Julian Severin},
  title = {BASICParser},
  version = {1.0},
  year = {2025},
  url = {https://github.com/SojaSurfer/BASICParser},
  note = {Software}
}
```
