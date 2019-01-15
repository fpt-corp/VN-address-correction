import requests
import json
import csv
import os
import traceback

def get_data(filepath):
    '''
    Extract address and home in labeled json file with file path
    '''
    f = open(filepath, 'rb')
    data = json.load(f)
    f.close()
    result = {}
    address_labels = []
    for label in data['address']:
        label = label['label']
        address_labels.append(label)
    address = ' '.join(address_labels)
    result['gt_address'] = address
    home_labels = []
    for label in data['home']:
        label = label['label']
        home_labels.append(label)
    home = ' '.join(home_labels)
    result['gt_home'] = home
    result['image_file'] = data['file']
    return result

def main():
    url = 'http://10.3.9.222:5001'
    output_file = './benchmark_address_full_p2.csv'
    data_path = '/media/trivu/data/DataScience/CV/CMT_data/reg+json+ID_images/'
    json_fns = os.listdir(os.path.join(data_path, 'json'))[2256:]
    i = 0
    file_nums = len(json_fns)
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['json_file', 'image_file', 'gt_address', 'gt_home', 'pd_address', 'pd_home']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for json_fn in json_fns:
            i += 1
            print(i, '/', file_nums)
            try:
                result = get_data(os.path.join(data_path, 'json', json_fn))
                result['json_file'] = json_fn
                file = {'image': open(os.path.join(data_path, 'tagme_jpg', result['image_file']), 'rb')}
                r = requests.post(url, files=file)
                res = r.json()
                data = res['data'][0]
                result['pd_address'] = data['address']
                result['pd_home'] = data['home']
                writer.writerow(result)
            except Exception as e:
                print('-------------------------')
                print('file error: ', json_fn)
                print('error: ', str(e))
                traceback.print_tb(e.__traceback__)

if __name__ == '__main__':
    main()