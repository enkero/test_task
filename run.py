import argparse
from config import Config as cfg
import math
from functions import (create_temp_directory, generate_test_file,
                       sort_by_batches, open_sorted_batches,
                       merge_and_sort_batches)


parser = argparse.ArgumentParser()
parser.add_argument("--generate", help="generate file? y/n",
                    type=str, default='y', choices=['y', 'n'])
parser.add_argument("--file", help="file for sorting",
                    type=str, default=cfg.generated_file)
parser.add_argument("--n_lines", help="number of lines in generated file",
                    type=int, default=cfg.n_lines)
parser.add_argument("--max_line_length", help="maximum line length in file",
                    type=int, default=cfg.max_line_length)
parser.add_argument("--gb", help="max batch of text (in Gb) read into RAM",
                    type=float, default=cfg.max_text_batch_size_gb)
args = parser.parse_args()


create_temp_directory(cfg.temp_directory)

if args.generate == 'y':
    n_uniform_lines_for_each_buffer = int(args.n_lines*cfg.ratio_random_lines
                                          / 2)
    n_random_lines = args.n_lines-n_uniform_lines_for_each_buffer*2
    generate_test_file(args.file, n_random_lines, args.max_line_length,
                       cfg.max_buffer_length, cfg.symbols,
                       n_uniform_lines_for_each_buffer, cfg.n_buffers_per_line)

max_symbols_in_memory = int(args.gb*cfg.symbols_per_gb)
n_buffers_per_batch = math.floor(max_symbols_in_memory/cfg.max_buffer_length)
sort_by_batches(args.file, n_buffers_per_batch, cfg.max_buffer_length,
                max_symbols_in_memory, cfg.temp_directory)

opened, mmaped, starts, ends = open_sorted_batches(cfg.temp_directory)

merge_and_sort_batches(opened, mmaped, starts, ends,
                       cfg.sorted_file, cfg.max_buffer_length,
                       max_symbols_in_memory, cfg.temp_directory)
