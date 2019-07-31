import numpy as np
from sklearn import preprocessing
from collections import Counter
import random
import string
import math
import mmap
import os
import shutil



def create_temp_directory(temp_directory):
    try:
        shutil.rmtree(temp_directory) 
    except FileNotFoundError:
        None

    os.makedirs(temp_directory)    

    
def generate_test_file(generated_file,n_random_lines,max_line_length,max_buffer_length,symbols,n_uniform_lines_for_each_buffer,n_buffers_per_line):
    file = open(generated_file,'w')

    write_random_lines(n_random_lines,max_line_length,max_buffer_length,symbols,file)
    write_uniform_lines_with_different_ending_for_several_buffers(n_uniform_lines_for_each_buffer,n_buffers_per_line,max_buffer_length,symbols,file)

    file.seek(file.tell()-1)
    file.truncate()

    file.close()
    

def write_random_line(max_line_length,max_buffer_length,symbols,file):
    line_length=random.randrange(0,max_line_length+1)
    n_buffers=math.ceil(line_length/max_buffer_length)
    for i in range(n_buffers-1):
        file.write(''.join([random.choice(symbols) for _ in range(max_buffer_length)]))
    length_end_buffer=line_length-(n_buffers-1)*max_buffer_length 
    file.write(''.join([random.choice(symbols) for _ in range(max_buffer_length)])+'\n')


def write_random_lines(n_random_lines,max_line_length,max_buffer_length,symbols,file):
    for _ in range(n_random_lines):
        write_random_line(max_line_length,max_buffer_length,symbols,file)  
                
        
def write_uniform_line(n_buffer,max_buffer_length,symbol,file):
    for _ in range(n_buffer-2):
        file.write(symbol*max_buffer_length)
    file.write('\n')  

    
def write_uniform_line_with_different_ending(n_buffer,max_buffer_length,symbol,file):
    for _ in range(n_buffer-1):
        file.write(symbol*max_buffer_length)
    file.write(random.choice(string.digits)+'\n')  

    
def write_uniform_lines_with_different_ending_for_buffer(n_uniform_lines_for_each_buffer,n_buffer,max_buffer_length,symbols,file):
    symbol=random.choice(string.ascii_letters)
    write_uniform_line(n_buffer,max_buffer_length,symbol,file)
    for _ in range(n_uniform_lines_for_each_buffer-1):        
        write_uniform_line_with_different_ending(n_buffer,max_buffer_length,symbol,file)

        
def write_uniform_lines_with_different_ending_for_several_buffers(n_uniform_lines_for_each_buffer,n_buffers_per_line,max_buffer_length,symbols,file):
    test_buffers=[n_buffers_per_line]
    if n_buffers_per_line>2:
        test_buffers+=random.sample(range(2,n_buffers_per_line),1)        
    for n_buffer in test_buffers:
        write_uniform_lines_with_different_ending_for_buffer(n_uniform_lines_for_each_buffer,n_buffer,max_buffer_length,symbols,file)
                    
            
def read_next_buffer(same_lines_starts,n_buffer,max_buffer_length,mmaped,lines_bounds):
    global buffers
    
    for line_start in same_lines_starts:
        end=lines_bounds[lines_bounds.index(line_start)+1]-1
        start=line_start+n_buffer*max_buffer_length
        end=np.min([start+max_buffer_length,end])
        buffers[np.where(buffers[:,0]==line_start),2]=mmaped[start:end]
        
        
def sort_next_buffer(id_same_lines):
    global buffers
    
    buffers[np.where(buffers[:,3]==id_same_lines)]=buffers[np.where(buffers[:,3]==id_same_lines)][np.argsort(buffers[np.where(buffers[:,3]==id_same_lines)][:,2])]

    
def split_id_for_next_buffer(id_same_lines):
    global buffers
    
    le = preprocessing.LabelEncoder()
    le.fit(buffers[np.where(buffers[:,3]==id_same_lines)][:,2])
    buffers[np.where(buffers[:,3]==id_same_lines),3]=np.max(buffers[:,3])+1+le.transform(buffers[np.where(buffers[:,3]==id_same_lines)][:,2]) 

    
def sort_same_lines(id_same_lines,max_buffer_length,mmaped,lines_bounds):
    global buffers
    global same_lines
    
    buffers[buffers[:,3]==id_same_lines,1]+=1
    
    n_buffer=buffers[buffers[:,3]==id_same_lines][0,1]
    same_lines_starts=buffers[buffers[:,3]==id_same_lines][:,0]
    
    read_next_buffer(same_lines_starts,n_buffer,max_buffer_length,mmaped,lines_bounds)
    
    if len(np.unique(buffers[np.where(buffers[:,3]==id_same_lines)][:,2]))>1:
        sort_next_buffer(id_same_lines)
        split_id_for_next_buffer(id_same_lines)
        same_lines.remove(id_same_lines)
        same_lines+=[k for k, v in Counter(buffers[np.in1d(buffers[:,0], same_lines_starts)][:,3]).items() if v>1]    
    elif np.unique(buffers[np.where(buffers[:,3]==id_same_lines)][:,2])==b'':
        same_lines.remove(id_same_lines)
    else:
        sort_same_lines(id_same_lines,max_buffer_length,mmaped,lines_bounds)            
        
        
def write_sorted_line(start,end,max_symbols_in_memory,file_temp,mmaped):
    n_buffers=math.ceil((end-start)/max_symbols_in_memory)
    for n_buffer in range(n_buffers-1):
        file_temp.write(mmaped[start+n_buffer*max_symbols_in_memory:start+(n_buffer+1)*max_symbols_in_memory].decode("utf-8"))
    file_temp.write(mmaped[start+(n_buffers-1)*max_symbols_in_memory:end-1].decode("utf-8") +'\n')     
    
    
def lines_bounds_for_batch(batch_start_position,mmaped,n_buffers_per_batch,file_end_reached):
    lines_bounds=[batch_start_position]

    while len(lines_bounds)<n_buffers_per_batch+1:
        bounds=mmaped.find(b'\n',lines_bounds[-1])
        if bounds==-1:
            bounds=lines_bounds[-1]+len(mmaped[lines_bounds[-1]:])
            lines_bounds+=[bounds+1]
            file_end_reached=True
            break
        lines_bounds+=[bounds+1]
    return(file_end_reached,lines_bounds)


def get_first_buffer_for_each_line_in_batch(lines_bounds,mmaped,max_buffer_length):
    buffers=[]
    for i,start in enumerate(lines_bounds[:-1]):
        end=np.min([start+max_buffer_length,lines_bounds[i+1]-1])
        buffers+=[mmaped[start:end]]
        
    order=np.argsort(buffers)

    buffers=np.array([lines_bounds[:-1],[0]*len(buffers),buffers,[0]*len(buffers)],dtype='object').T
    buffers=buffers[order]    
    return(buffers)  


def mark_unique_buffers(buffers):
    le = preprocessing.LabelEncoder()
    le.fit(buffers[:,2])
    buffers[:,3]=le.transform(buffers[:,2])
    return(buffers)
    
    
def sort_batch(batch_start_position,mmaped,n_buffers_per_batch,max_buffer_length,file_end_reached):
    global buffers
    global same_lines
    
    file_end_reached,lines_bounds=lines_bounds_for_batch(batch_start_position,mmaped,n_buffers_per_batch,file_end_reached)
    buffers=get_first_buffer_for_each_line_in_batch(lines_bounds,mmaped,max_buffer_length)
    buffers=mark_unique_buffers(buffers)
    
    same_lines=[k for k, v in Counter(buffers[:,3]).items() if v>1]        
    while len(same_lines)!=0:
        sort_same_lines(same_lines[0],max_buffer_length,mmaped,lines_bounds)
        
    buffers=buffers[:,0]
        
    return(buffers,lines_bounds,file_end_reached) 


def write_sorted_batch(lines_bounds,max_symbols_in_memory,batch_start_position,buffers,mmaped,temp_directory):
    file_temp = open(temp_directory+'sorted_'+str(len(batch_start_position)-1)+'.txt','w')
    
    for start in buffers:
        end=lines_bounds[lines_bounds.index(start)+1]
        write_sorted_line(start,end,max_symbols_in_memory,file_temp,mmaped,buffers)
        
    file_temp.seek(file_temp.tell()-1)
    file_temp.truncate()             
    file_temp.close()


def write_sorted_line(start,end,max_symbols_in_memory,file_temp,mmaped,buffers):
    n_buffers=math.ceil((end-start)/max_symbols_in_memory)
    for n_buffer in range(n_buffers-1):
        file_temp.write(mmaped[start+n_buffer*max_symbols_in_memory:start+(n_buffer+1)*max_symbols_in_memory].decode("utf-8"))
    file_temp.write(mmaped[start+(n_buffers-1)*max_symbols_in_memory:end-1].decode("utf-8") +'\n')
    
    
def write_sorted_line_and_read_another(n_file,max_symbols_in_memory,file_result,mmaped,buffers,starts,ends,max_buffer_length):
    write_sorted_line(starts[n_file],ends[n_file]+1,max_symbols_in_memory,file_result,mmaped[n_file],buffers)
    starts[n_file]=ends[n_file]+1
    end=mmaped[n_file].find(b'\n',starts[n_file]+1)
    end=starts[n_file]+len(mmaped[n_file][starts[n_file]:]) if end==-1 else end
    ends[n_file]=end
    
    if ends[n_file]-starts[n_file]>0:
        buffers[np.where(buffers[:,0]==n_file),2]=mmaped[n_file][starts[n_file]:np.min([ends[n_file],starts[n_file]+max_buffer_length])]
    else:
        buffers=buffers[np.where(buffers[:,0]!=n_file)]
    return(starts,ends,buffers)    

        
def pass_sort_on_new_lines(mmaped,starts,ends,max_symbols_in_memory,file_result,max_buffer_length,buffers):
    order=np.lexsort((buffers[:,2],buffers[:,3]))
    buffers=buffers[order]
    buffers=mark_unique_buffers(buffers)
    
    if buffers[np.where(buffers[:,3]==0)].shape[0]==1:
        n_file=buffers[np.where(buffers[:,3]==0),0][0,0]
        starts,ends,buffers=write_sorted_line_and_read_another(n_file,max_buffer_length,file_result,mmaped,buffers,starts,ends,max_buffer_length)
    elif np.unique(buffers[np.where(buffers[:,3]==0),3])==b'':
        for n_file in buffers[np.where(buffers[:,3]==0),0]:
            starts,ends,buffers=write_sorted_line_and_read_another(n_file,max_buffer_length,file_result,mmaped,buffers,starts,ends,max_buffer_length)
    else:
        buffers[np.where(buffers[:,3]==0),1]+=1
        for n_file in buffers[np.where(buffers[:,3]==0),0]:
            n_buffer=buffers[np.where(buffers[:,0]==n_file)][0,1]
            buffers[np.where(buffers[:,0]==n_file),2]=mmaped[n_file][starts[n_file]+n_buffers*max_buffer_length:np.min([ends[n_file],starts[n_file]+(n_buffers+1)*max_buffer_length])]
    return(buffers)


def sort_by_batches(generated_file,n_buffers_per_batch,max_buffer_length,max_symbols_in_memory,temp_directory):
    file = open(generated_file,'r')

    mmaped = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
    
    file_end_reached=False
    batch_start_position=[0]

    while not(file_end_reached):
        buffers,lines_bounds,file_end_reached=sort_batch(batch_start_position[-1],mmaped,n_buffers_per_batch,max_buffer_length,file_end_reached)
        batch_start_position+=[lines_bounds[-1]]
        write_sorted_batch(lines_bounds,max_symbols_in_memory,batch_start_position,buffers,mmaped,temp_directory)

        
def open_sorted_batches(temp_directory):
    sorted_files=[temp_directory+x for x in os.listdir(temp_directory) if 'sorted' in x]
    
    opened=[]
    mmaped=[]
    starts=[]
    ends=[]

    for i,sorted_file_name in enumerate(sorted_files):
        opened+=[open(sorted_file_name,'r')]
        mmaped+=[mmap.mmap(opened[i].fileno(), 0, access=mmap.ACCESS_READ)]
        starts+=[0]
        end=mmaped[i].find(b'\n',0)
        end=len(mmaped[i]) if end==-1 else end 
        ends+=[end]
        
    return(opened,mmaped,starts,ends)  


def merge_and_sort_batches(opened,mmaped,starts,ends,sorted_file,max_buffer_length,max_symbols_in_memory,temp_directory):
    file_result = open(sorted_file,'w')
    
    buffers=[]
    for i in range(len(mmaped)):
        buffers+=[mmaped[i][starts[i]:np.min([ends[i],max_buffer_length])]]
    
    order=np.argsort(buffers)

    buffers=np.array([range(len(mmaped)),[0]*len(buffers),buffers,[0]*len(buffers)],dtype='object').T
    
    while buffers.shape[0]>0:
        buffers=pass_sort_on_new_lines(mmaped,starts,ends,max_symbols_in_memory,file_result,max_buffer_length,buffers)
        
    file_result.seek(file_result.tell()-1)
    file_result.truncate()         
    file_result.close()
    shutil.rmtree(temp_directory) 
    
    
def hashed(mmaped,max_symbols_in_memory):
    hash_sum=0
    start=0
    end=mmaped.find(b'\n',1)
    while end!=-1:
        hash_sum+=hash(mmaped[start:end])
        start=end+1
        end=mmaped.find(b'\n',start)
    hash_sum+=hash(mmaped[start:])   
    return(hash_sum) 


def compare_two_lines(mmaped_sorted,start_position,max_buffer_length,n_buffer,end_first,end_second):
    file_end=False
    start_first=start_position+n_buffer*max_buffer_length
    end_first=mmaped_sorted.find(b'\n',start_first+1) if n_buffer==0 else end_first
    start_second=end_first+1+n_buffer*max_buffer_length
    end_second=mmaped_sorted.find(b'\n',start_second+1) if n_buffer==0 else end_second
    end_second=start_second+len(mmaped_sorted[start_second:]) if end_second==-1 else end_second
    
    first_line_buffer=mmaped_sorted[start_first:np.min([start_first+max_buffer_length,end_first])]
    second_line_buffer=mmaped_sorted[start_second:np.min([start_second+max_buffer_length,end_second])]
    
    if first_line_buffer<second_line_buffer:
        return(True)
    elif first_line_buffer>second_line_buffer:
        return(False)
    elif (first_line_buffer==second_line_buffer)*(first_line_buffer==b''):
        return(True)
    else:
        n_buffer+=1
        return(compare_two_lines(mmaped_sorted,start_position,max_buffer_length,n_buffer,end_first,end_second))

        
def is_adjacent_lines_are_sorted(mmaped_sorted,max_buffer_length):
    last_line=False
    start_position=0
    is_sorted=[]
    while not(last_line):
        is_sorted+=[compare_two_lines(mmaped_sorted,start_position,max_buffer_length,0,0,0)]
        start_position=mmaped_sorted.find(b'\n',start_position+1)+1
        last_line=True if mmaped_sorted.find(b'\n',start_position+1)==-1 else False
    is_sorted=[x for x in is_sorted if x in [True,False]]
    return(is_sorted) 


def count_lines(mmaped_sorted):
    start_position=[0]
    counted_lines=0

    while start_position[-1]!=-1:
        start_position+=[mmaped_sorted.find(b'\n',start_position[-1]+1)]
        counted_lines=counted_lines+1 if start_position[-1]!=-1 else counted_lines

    if len(mmaped_sorted[start_position[-2]+1:])>0:
        counted_lines+=1
    return(counted_lines)  