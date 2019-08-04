import math
import string


class Config():
    temp_directory = 'temp/'
    generated_file = 'test.txt'
    sorted_file = 'sorted.txt'

    n_lines = 20
    ratio_random_lines = 0.5
    n_uniform_lines_for_each_buffer = int(n_lines*ratio_random_lines/2)
    n_random_lines = n_lines-n_uniform_lines_for_each_buffer*2

    max_line_length = 97

    max_buffer_length = 10  # This can be changed depends on strings type
    max_symbols_in_memory = 50
    max_text_batch_size_gb = 1.0
    symbols_per_gb = 1073741824

    symbols = string.ascii_letters + string.digits + ' '
    n_buffers_per_line = math.ceil(max_line_length/max_buffer_length)
    n_buffers_per_batch = math.floor(max_symbols_in_memory/max_buffer_length)
