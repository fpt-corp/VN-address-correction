from collections import defaultdict

def normalize_address(address: str)->str:
    if address == 'phạm đình hồ':
        return 'phạm đình hổ'
    if address == 'ly nam de':
        return 'lý nam đế'
    if address == 'thuận lương':
        return 'thuần lương'
    if address == 'ap dinh':
        return 'ấp đình'
    tokens = address.split()
    if len(tokens) > 2 and tokens[0] in ['đường', 'phố', 'phường', 'thôn', 'p', 'tt', 'tx', 'đ', 'x']:
        return ' '.join(tokens[1:])
    else:
        return ' '.join(tokens)

def check_address(address: str):
    tokens = address.split()
    if len(tokens) > 4:
        return False
    no_space_addr = ''.join(tokens)
    if len(tokens) == 2 and tokens[0] in ['phường', 'quận'] and tokens[1].isdigit():
        return True
    if no_space_addr.isalpha():
        return True
    else:
        return False

def main():
    f_in = open('./ggmap_address.txt')
    f_wards = open('./src/data/wards.txt')
    f_underwards = open('./src/data/underwards.txt', 'w')
    f_wards2 = open('./src/data/wards2.txt', 'w')
    wards = defaultdict(set)
    under_wards = defaultdict(set)
    for line in f_wards:
        line = line.strip()
        if len(line) == 0:
            break
        ward, district, province = line.strip().split('\t')
        wards[(province, district)].add(ward)
    for line in f_in:
        line = line.strip().replace('.', ' ').lower()
        if len(line) == 0:
            continue
        elements = line.split('\t')
        if len(elements) < 4 or len(elements) > 5:
            continue
        elements = [normalize_address(element) for element in elements]
        valid_address = True
        for element in elements:
            if not check_address(element):
                valid_address = False
                break
        if not valid_address:
            continue
        wards[(elements[-2], elements[-3])].add(elements[-4])
        if len(elements) == 5:
            under_wards[(elements[-2], elements[-3], elements[-4])].add(elements[-5])
    for province, district in wards:
        for ward in wards[(province, district)]:
            f_wards2.write('{}\t{}\t{}\n'.format(ward, district, province))
    for province, district, ward in under_wards:
        for under_ward in under_wards[(province, district, ward)]:
            f_underwards.write('{}\t{}\t{}\t{}\n'.format(under_ward, ward, district, province))
    f_in.close()
    f_wards.close()
    f_underwards.close()
    f_wards2.close()

if __name__ == '__main__':
    main()