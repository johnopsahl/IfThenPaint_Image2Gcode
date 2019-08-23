import os
import json
from definitions import DATA_PATH

def remove_process(process_name):
    # remove a paint stroke generation process after committing it to memory
    # with the commit process script
    
    with open(os.path.join(DATA_PATH, 'processes.txt'), 'r') as f:
        processes = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_lines.txt'), 'r') as f:
        process_lines = json.load(f)
    f.close()
    
    process_name_list = [x['name'] for x in processes]
    process_index = process_name_list.index(process_name)
    
    del processes[process_index]
    del process_lines[process_index]

    with open(os.path.join(DATA_PATH, 'processes.txt'), 'w') as f:
        json.dump(processes, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_lines.txt'), 'w') as f:
        json.dump(process_lines, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    image_file_name = 'process_commit_' + process_name
    os.remove(os.path.join(DATA_PATH, image_file_name + '.png'))

if __name__ == '__main__':
   
    remove_process('line_scan_gray')