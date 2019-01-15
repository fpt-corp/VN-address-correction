from collections import defaultdict
from functools import cmp_to_key

def valid_address(text):
    skip_phrase = ['tập thể', 'ql', 'kcn', 'công nghiệp', 'ck', 'ter', 'tòa nhà', 'lầu',
        'cao ốc', 'bis', 'dtm', 'ktt', 'đtm', 'kđt', 'nhà ở', 'cntt', 'ccn', 'tt', 'đtm', 'nt',
        'cơ quan', 'tdc', 'dân cư', 'đại lộ', 'trung tâm', 'thương mại', 'cn', 'thu nhập',
        'kp', 'tái định cư', 'building', 'đt', 'đô thị', 'bn', 'đh', 'kcx', 'chế x', 'kdc', 'tk',
        'ks', 'khu phố', 'db', 'phố đẹp', 'dh', 'dd', 'ht', 'tower', 'căn hộ', 'city', 'river',
        'gd', 'gđ', 'dịch vụ', 'tđc', 'dv', 'bệnh viện', 'thị trấn', 'tuổi trẻ', 'tp', 'công an',
        'alexandre', 'lake', 'td', 'dg', 'học viện', 'đấu giá', 'chung cư', 'biệt thự', 'tx',
        'dự án', 'đại học', 'nc', 'kqh', 'định cư', 'quy hoạch', 'tch', 'dct', 'đường số', 'km', 'cư xá',
        'công nghệ', 'bờ sông', 'xí nghiệp', 'nội vụ']
    for phrase in skip_phrase:
        if phrase in text:
            return False
    for c in text:
        if not (c.isalnum() or c.isspace()):
            return False
    tokens = text.split()
    nb_of_tokens = len(tokens)
    if len(tokens[0]) == 1:
        return False
    if len(tokens[-1]) > 2 and not tokens[-1].isalpha():
        return False
    for i in range(nb_of_tokens):
        token = tokens[i]
        if len(token) >= 7:
            return False
        if i < nb_of_tokens-1:
            if not token.isalpha():
                return False
            if token == 'the':
                return False
            valid_va = ['mường và', 'đền và', 'đồng và', 'cù và']
            if token == 'và' and text not in valid_va:
                return False
            if token in ['tầng' , 'ngách', 'hoàng', 'nhà', 'khối', 'khóm', 'phố', 'lô', 'khu', 'số', 'phòng', 'tổ', 'tỉnh', 'lộ', 'cụm', 'đội', 'cổng'] and (len(tokens[i+1]) == 1 or not tokens[i+1].isalpha()):
                return False
        if len(token) == 1 and nb_of_tokens < 2:
            return False
    return True

def addr_normalize(addr):
    tokens = addr.split()
    for i in range(len(tokens)):
        if tokens[i].isdigit() and tokens[i][0] == '0':
            tokens[i] = tokens[i][1:]
    return ' '.join(tokens)

def main():
    place_file = open('./output/address_parsed.txt')
    output_file = open('./output/data_normalized.txt', 'w')
    wards = defaultdict(set)
    under_wards = defaultdict(set)
    for line in place_file:
        line = line.strip()
        if not line:
            break
        elements = line.split('\t')
        if not valid_address(elements[-3]):
            continue
        elements[-3] = addr_normalize(elements[-3])
        wards[(elements[-1], elements[-2])].add(elements[-3])
        if len(elements) == 4:
            if not valid_address(elements[-4]):
                continue
            under_wards[(elements[-1], elements[-2], elements[-3])].add(elements[-4])
    districts_provinces = list(wards.keys())
    def compare_district_province_pairs(pair1, pair2):
        if pair1[0] == pair2[0]:
            return pair1[1] < pair2[1]
        elif pair1[0] == 'hà nội':
            return -1
        elif pair2[0] == 'hà nội':
            return 1
        elif pair1[0] == 'hồ chí minh':
            return -1
        elif pair2[0] == 'hồ chí minh':
            return 1
        elif pair1[0] == 'đà nẵng':
            return -1
        elif pair2[0] == 'đà nẵng':
            return 1
        else:
            return pair1[0] < pair2[0]
    districts_provinces.sort(key=cmp_to_key(compare_district_province_pairs))
    # print(districts_provinces)
    for province, district in districts_provinces:
        wss = wards[(province, district)]
        wss = sorted(wss)
        for ws in wss:
            output_file.write('{}\t{}\t{}\n'.format(ws, district, province))
            under_wss = under_wards[(province, district, ws)]
            under_wss = sorted(under_wss)
            for under_ws in under_wss:
                output_file.write('{}\t{}\t{}\t{}\n'.format(under_ws, ws, district, province))
    place_file.close()
    output_file.close()

if __name__ == '__main__':
    main()