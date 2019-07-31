import math
import string

      
class Config():
    temp_directory='temp/'
    generated_file='test.txt'
    sorted_file='sorted.txt'
    
    n_lines=10
    ratio_random_lines=0.5
    n_random_lines=int(n_lines/2)
    n_uniform_lines_for_each_buffer=n_lines-n_random_lines
    
    max_line_length=97
    
    max_buffer_length=10 ######### These two parameters can be changed ###########
    max_symbols_in_memory=50 ##### depends on available RAM and strings type #####


    symbols=string.ascii_letters + string.digits + ' '
    n_buffers_per_line=math.ceil(max_line_length/max_buffer_length)
    n_buffers_per_batch=math.floor(max_symbols_in_memory/max_buffer_length)








