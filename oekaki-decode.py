#!/usr/bin/env python3
"""
Decoder for おーちゃんのおえかきロジック (O-Chan no Oekaki Logic)
WonderSwan ROM, SunSoft 2000

Decodes all 372 nonogram puzzles from the ROM file.

Usage: python3 oekaki-decode.py /path/to/oekaki.ws [output.json]
"""

import json
import sys

# ROM layout constants
LUT_BASE = 0x20690      # File offset of lookup table (372 × 4 bytes)
TOTAL_PUZZLES = 372

# Data pool base offsets in DS=0xA000 address space (SI values)
# Physical = 0xA0000 + SI; file offset = physical - 0x80000
DATA_BASES = {0: 0x2D58, 1: 0x3190, 2: 0x4108, 3: 0x9568, 4: 0xB4D0}
PUZZLE_SIZE = 0x78  # 120 bytes per puzzle in ROM

# Grid dimensions per size_cat
# [0x104]+1 = n_rows, [0x102]+1 = n_cols (from decode routine at 0x4CF1)
GRID_ROWS = {0: 5,  1: 10, 2: 15, 3: 15, 4: 15}
GRID_COLS = {0: 5,  1: 10, 2: 15, 3: 20, 4: 25}

# Difficulty level start indices in lookup table
# Derived from SI bases: 0x690, 0x7F4, 0x95C, 0xA74, 0xB40
# Offsets from LUT_BASE/4: 0, 89, 179, 249, 300
DIFF_START = [0, 89, 179, 249, 300, 372]


def decode_grid(rom, size_cat, sub_idx):
    """
    Decode puzzle ROM data to a 15×32 cell array.

    V30MZ decode loop at ROM offset 0x4D6B:
      - Outer loop: 60 iterations (= 15 rows × 4 words/row)
      - Inner loop: 4 iterations per word (= 8 cells per word)
      - Per iteration: MOV AX,[SI]; XCHG AL,AH (→ big-endian word);
        extract 2-bit pairs MSB-first; write pairs to ES:DI sequentially
      - Cell value > 1 means filled; 0 or 1 means empty

    Returns: list of 15 rows, each a list of 32 cell values (0-3)
    """
    si = DATA_BASES[size_cat] + PUZZLE_SIZE * sub_idx
    file_off = 0xA0000 + si - 0x80000
    data = rom[file_off:file_off + 120]

    grid = []
    for row in range(15):
        cells = []
        for wi in range(4):
            b0 = data[row * 8 + wi * 2]
            b1 = data[row * 8 + wi * 2 + 1]
            ax = (b0 << 8) | b1   # XCHG AL,AH = big-endian of LE word
            for sh in [14, 12, 10, 8, 6, 4, 2, 0]:
                cells.append((ax >> sh) & 3)
        grid.append(cells)
    return grid


def compute_clues(grid, n_rows, n_cols):
    """Extract row and column nonogram clues from decoded grid."""
    def runs(seq):
        clues, run = [], 0
        for v in seq:
            if v > 1:
                run += 1
            elif run:
                clues.append(run)
                run = 0
        if run:
            clues.append(run)
        return clues or [0]

    row_clues = [runs(grid[r][:n_cols]) for r in range(n_rows)]
    col_clues = [runs([grid[r][c] for r in range(n_rows)]) for c in range(n_cols)]
    return row_clues, col_clues


def decode_all(rom_path):
    rom = open(rom_path, 'rb').read()
    if len(rom) != 0x80000:
        raise ValueError(f"Expected 512KB ROM, got {len(rom)} bytes")

    puzzles = []
    for i in range(TOTAL_PUZZLES):
        off = LUT_BASE + i * 4
        sc  = int.from_bytes(rom[off:off+2],   'little')
        si  = int.from_bytes(rom[off+2:off+4], 'little')
        diff = next(d for d in range(5) if DIFF_START[d] <= i < DIFF_START[d+1])
        local_idx = i - DIFF_START[diff]

        grid = decode_grid(rom, sc, si)
        n_rows, n_cols = GRID_ROWS[sc], GRID_COLS[sc]
        row_clues, col_clues = compute_clues(grid, n_rows, n_cols)

        puzzles.append({
            'global_num':  i + 1,
            'difficulty':  diff,
            'local_num':   local_idx + 1,
            'size_cat':    sc,
            'sub_idx':     si,
            'rows':        n_rows,
            'cols':        n_cols,
            'row_clues':   row_clues,
            'col_clues':   col_clues,
            'solution':    [''.join('X' if grid[r][c] > 1 else '.'
                                    for c in range(n_cols))
                            for r in range(n_rows)],
        })
    return puzzles


if __name__ == '__main__':
    rom_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/oekaki.ws'
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    puzzles = decode_all(rom_path)
    print(f"Decoded {len(puzzles)} puzzles")

    counts = {}
    for p in puzzles:
        k = (p['rows'], p['cols'])
        counts[k] = counts.get(k, 0) + 1
    for k in sorted(counts):
        print(f"  {k[0]}x{k[1]}: {counts[k]} puzzles")

    if out_path:
        with open(out_path, 'w') as f:
            json.dump(puzzles, f, indent=2)
        print(f"Wrote {out_path}")
    else:
        # Print a sample: difficulty 2, puzzle 18
        p = next(p for p in puzzles if p['difficulty'] == 2 and p['local_num'] == 18)
        print(f"\nSample -- difficulty 2, puzzle 18 ({p['rows']}x{p['cols']}):")
        print(f"  Row clues: {p['row_clues']}")
        print(f"  Col clues: {p['col_clues']}")
        for line in p['solution']:
            print(f"  {line}")
