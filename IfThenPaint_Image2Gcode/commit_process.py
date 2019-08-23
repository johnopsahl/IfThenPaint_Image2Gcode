import os
import json
import cv2
from definitions import DATA_PATH

def commit_process():
    # commits the last line scan process that was run, allows for human review
    # prior to commiting process to memory
    
    with open(os.path.join(DATA_PATH, 'process_temp.txt'), 'r') as f:
        process_temp = json.load(f)
    f.close()
    
    with open(os.path.join(DATA_PATH, 'process_line_temp.txt'), 'r') as f:
        process_line_temp = json.load(f)
    f.close()
    
    # log image of commit line scan
    image_eval = cv2.imread(os.path.join(DATA_PATH, 'image_eval_final.png'))
    
    image_file_name = 'process_commit_' + str(process_temp['name'])
    
    cv2.imwrite(os.path.join(DATA_PATH, image_file_name + '.png'), image_eval)

    process_line_file_path = os.path.join(DATA_PATH, 'process_lines.txt')
    if os.path.isfile(process_line_file_path):
        with open(process_line_file_path, 'r') as f:
            process_lines = json.load(f)
        f.close()
    else:
        process_lines = []

    process_lines.append(process_line_temp)
    
    with open(os.path.join(DATA_PATH, 'process_lines.txt'), 'w') as f:
        json.dump(process_lines, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
    process_file_path = os.path.join(DATA_PATH, 'processes.txt')
    if os.path.isfile(process_file_path):
        with open(process_file_path, 'r') as f:
            processes = json.load(f)
        f.close()
    else:
        processes = []
            
    processes.append(process_temp)
    
    with open(os.path.join(DATA_PATH, 'processes.txt'), 'w') as f:
        json.dump(processes, f, separators = (',', ':'), sort_keys = True, indent = 4)
    f.close()
    
if __name__ == '__main__':

    commit_process()