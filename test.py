import numpy as np
import mmap
from config import Config as cfg
from functions import *



create_temp_directory(cfg.temp_directory)

generate_test_file(cfg.generated_file,cfg.n_random_lines,cfg.max_line_length,cfg.max_buffer_length,cfg.symbols,cfg.n_uniform_lines_for_each_buffer,cfg.n_buffers_per_line)   

sort_by_batches(cfg.generated_file,cfg.n_buffers_per_batch,cfg.max_buffer_length,cfg.max_symbols_in_memory,cfg.temp_directory)

opened,mmaped,starts,ends=open_sorted_batches(cfg.temp_directory)

merge_and_sort_batches(opened,mmaped,starts,ends,cfg.sorted_file,cfg.max_buffer_length,cfg.max_symbols_in_memory,cfg.temp_directory)



file = open(cfg.generated_file,'r')
mmaped = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

file_sorted = open(cfg.sorted_file,'r')
mmaped_sorted = mmap.mmap(file_sorted.fileno(), 0, access=mmap.ACCESS_READ)



def test_equal_sizes():
    assert len(mmaped)==len(mmaped_sorted)
    
def test_equal_hashes():
    assert hashed(mmaped,cfg.max_symbols_in_memory)==hashed(mmaped_sorted,cfg.max_symbols_in_memory)
    
def test_lines_sorted():
    assert np.sum(is_adjacent_lines_are_sorted(mmaped_sorted,cfg.max_buffer_length))==count_lines(mmaped_sorted)-1    
    