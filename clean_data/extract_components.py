# Script này xử lý dữ liệu địa chỉ trong file "address_thongtincongty_toan-quoc.csv"
# Dữ liệu địa chỉ sẽ phân ra các trường thôn xóm đường, phường xã, quận huyện, tỉnh tp
import os
from collections import defaultdict

data_path = os.path.join(os.path.dirname(__file__), '../data')

def get_provinces_districts_wards():
    provinces = []
    districts = defaultdict(list)
    wards = defaultdict(list)
    with open(os.path.join(data_path, 'provinces.txt')) as f:
        for line in f:
            entity = line.strip()
            if not entity:
                break
            entity = entity.split('|')
            provinces.extend(entity)
    with open(os.path.join(data_path, 'districts.txt')) as f:
        for line in f:
            entity = line.strip()
            ds, ps = entity.split('\t')
            ds = ds.split('|')
            ps = ps.split('|')
            for p in ps:
                districts[p].extend(ds)
    with open(os.path.join(data_path, 'wards.txt')) as f:
        for line in f:
            entity = line.strip()
            ws, ds, ps = entity.split('\t')
            ds = ds.split('|')
            ws = ws.split('|')
            ps = ps.split('|')
            for p in ps:
                for d in ds:
                    wards[(p, d)].extend(ws)
    return provinces, districts, wards

def normalize_spelling(text):
    tokens = text.strip().lower().split()
    result = []
    if len(tokens) >= 5 and tokens[-3] == '-':
        tokens = tokens[:-3] + tokens[-2:]
    for token in tokens:
        if token.endswith('oá'):
            result.append(token[:-2] + 'óa')
        elif token.endswith('oà'):
            result.append(token[:-2] + 'òa')
        # elif token.endswith('oá,'):
        #     result.append(token[:-3] + 'óa,')
        # elif token.endswith('oà,'):
            # result.append(token[:-3] + 'òa,')
        elif token.endswith('uỷ'):
            result.append(token[:-2] + 'ủy')
        # elif token.endswith('uỷ,'):
        #     result.append(token[:-3] + 'ủy,')
        elif token.endswith('uỵ'):
            result.append(token[:-2] + 'ụy')
        # elif token.endswith('uỵ,'):
        #     result.append(token[:-3] + 'ụy,')
        elif token == 'quí':
            result.append('quý')
        elif token == 'qui':
            result.append('quy')
        elif token != '-':
            result.append(token)
    return ' '.join(result)

def separate_address(address, provinces, districts, wards):
    if len(address) > 15:
        address = address[:-15].replace('-', ',') + address[-15:]
    elements = address.split(',')
    if len(elements) < 3:
        return
    elements = [normalize_spelling(element) for element in elements]
    skip_provinces = ['đắc lắc', 'đắk nông', 'bắc cạn']
    for skip_province in skip_provinces:
        if skip_province in elements[-1]:
            return
    province_address = None
    for province in provinces:
        if province in elements[-1]:
            province_address = province
            break
    if province_address is None:
        return
    district_address = None
    for district in districts[province_address]:
        if district in elements[-2] and \
            (district_address is None or len(district_address) < len(district)):
            district_address = district
    if district_address is None:
        return
    # ward_address = None
    # for ward in wards[(province_address, district_address)]:
    #     if ward in elements[-3]:
    #         ward_address = ward
    # if ward_address is None:
    #     print(elements)
    return elements[:-2], district_address, province_address

def contain_digit(word):
    for c in word:
        if c.isdigit():
            return True
    return False

def extract_wards(text):
    if len(text) == 0:
        return
    if text[:2] == 'p ':
        text = 'phường ' + text[2:]
    else:
        text = text.replace('p.', 'phường ')
        text = text.replace(' p ', 'phường ')
    tokens = text.split()
    if len(tokens) < 2:
        return
    if tokens[0] in ['phường', 'xã', 'tx', 'tt']:
        if len(tokens) > 2:
            return ' '.join(tokens[1:])
        else:
            return ' '.join(tokens)
    if tokens[0] == 'thị' and tokens[1] == 'trấn':
        return ' '.join(tokens[2:])
    if len(tokens) in [2, 3]:
        if ''.join(tokens).isalpha():
            return ' '.join(tokens)
    nb_of_tokens = len(tokens)
    for i in range(nb_of_tokens - 2, -1, -1):
        if tokens[i] in ['phố', 'phường', 'đường', 'xã', 'kđt'] or contain_digit(tokens[i]):
            if i < nb_of_tokens -2:
                return ' '.join(tokens[i+1:])
            else:
                return ' '.join(tokens[i:])
        elif tokens[i] == 'thị' and tokens[i+1] == 'trấn':
            return ' '.join(tokens[i+2:])

def extract_under_wards(text):
    for c in text:
        if not (c.isalnum() or c.isspace() or c == '/'):
            return
    tokens = text.split()
    if len(tokens) <= 1:
        return
    nb_of_tokens = len(tokens)
    if tokens[-2] == 'số' and not tokens[-1].isalpha():
        return
    for i in range(nb_of_tokens-2, max(-1, nb_of_tokens-6), -1):
        if tokens[i] in ['đường', 'ấp', 'kv', 'thôn', 'xóm', 'phố', 'bis', 'ngõ']:
            if i < nb_of_tokens-2:
                if tokens[i+1] != 'mới':
                    return ' '.join(tokens[i+1:])
                elif i < nb_of_tokens-4:
                    return ' '.join(tokens[i+2:])
                else:
                    return
            elif tokens[-1].isalpha():
                return ' '.join(tokens[i:])
            else:
                return
        if i < nb_of_tokens-2:
            if tokens[i] == 'thị' and i > 0 and tokens[i-1] == 'đô' and tokens[i+1] != 'mới':
                return ' '.join(tokens[i+1:])
            if tokens[i] == 'khu':
                if tokens[i+1] not in ['phố', 'vực']:
                    return ' '.join(tokens[i+1:])
                elif i < nb_of_tokens-4:
                    return ' '.join(tokens[i+2:])
                else:
                    return
            if not tokens[i].isalpha():
                return ' '.join(tokens[i+1:])


def main():
    provinces, districts, wards = get_provinces_districts_wards()

    # line = 'Đường Thành, Quận Hoàn Kiếm, Hà Nội'
    # address_parsing = separate_address(line, provinces, districts, wards)
    # if address_parsing is None:
    #     # error_file.write('error parsing' + line+'\n')
    #     print('err')
    # head, district, province = address_parsing
    # wards = extract_wards(head[-1])
    # print('wards:', wards)
    # print(head)
    # under_wards = extract_under_wards(head[-2])
    # print(under_wards)

    address_file = open('./only_address_thongtincongty_toan-quoc.txt')
    address_parsed = open('./output/address_parsed.txt', 'w')
    # error_file = open('./output/error_wards.txt', 'w')
    # under_error_file = open('./output/error_under_wards.txt', 'w')
    # output_file = open('./output/address_parsing.txt', 'w')
    for line in address_file:
        line = line.strip()
        address_parsing = separate_address(line, provinces, districts, wards)
        if address_parsing is None:
            # error_file.write('error parsing' + line + '\n')
            continue
        head, district, province = address_parsing
        wards = extract_wards(head[-1])
        if wards is None or len(wards) == 0:
            # error_file.write(line+'\n')
            continue
        # address_parsed.write(line+'\n')
        under_wards = None
        if len(head) > 1:
            under_wards = extract_under_wards(head[-2])
        if under_wards is None or len(under_wards) == 0:
            address_parsed.write('{}\t{}\t{}\n'.format(wards, district, province))
            # under_error_file.write('{}\n{}\t{}\t{}\t{}\n'.format(line, head[:-1], wards, district, province))
        else:
            address_parsed.write('{}\t{}\t{}\t{}\n'.format(under_wards, wards, district, province))
            # output_file.write('{}\n{}\t{}\t{}\t{}\t{}\n'.format(line, head[:-2], under_wards, wards, district, province))
    address_file.close()
    address_parsed.close()

    # error_file.close()
    # output_file.close()

if __name__ == '__main__':
    main()
