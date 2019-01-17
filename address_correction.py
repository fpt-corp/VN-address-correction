import os
from collections import defaultdict
from .utils import StringDistance, extract_digit

class AddressCorrection:
    '''
    Address correction with phrase compare
    '''
    def __init__(self, cost_dict_path=None, provinces_path=None, districts_path=None, wards_path=None, underwards_path=None):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if cost_dict_path is None:
            cost_dict_path = os.path.join(dir_path, 'data', 'cost_char_dict.txt')
        if provinces_path is None:
            provinces_path = os.path.join(dir_path, 'data', 'provinces.txt')
        if districts_path is None:
            districts_path = os.path.join(dir_path, 'data', 'districts.txt')
        if wards_path is None:
            wards_path = os.path.join(dir_path, 'data', 'wards2.txt')
        if underwards_path is None:
            underwards_path = os.path.join(dir_path, 'data', 'underwards.txt')
        self.string_distance = StringDistance(cost_dict_path=cost_dict_path)
        self.provinces = []
        self.districts = defaultdict(list)
        self.wards = defaultdict(list)
        self.underwards = defaultdict(list)
        with open(provinces_path, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                if not entity:
                    break
                entity = entity.split('|')
                self.provinces.extend(entity)

        with open(districts_path, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                districts, provinces = entity.split('\t')
                districts = districts.split('|')
                provinces = provinces.split('|')
                for province in provinces:
                    self.districts[province].extend(districts)
        with open(wards_path, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                wards, districts, provinces = entity.split('\t')
                districts = districts.split('|')
                wards = wards.split('|')
                provinces = provinces.split('|')
                for province in provinces:
                    for district in districts:
                        self.wards[(province, district)].extend(wards)
        with open(underwards_path, 'r', encoding='utf-8') as f:
            for line in f:
                entity = line.strip()
                underward, ward, district, province = entity.split('\t')
                self.underwards[(province, district, ward)].append(underward)

    def correct(self, phrase, correct_phrases, nb_candidates=2, distance_threshold=4):
        candidates = [(None, distance_threshold)] * nb_candidates
        max_diff_length = distance_threshold
        for correct_phrase in correct_phrases:
            if abs(len(phrase) - len(correct_phrase)) >= max_diff_length:
                continue
            if extract_digit(correct_phrase) != extract_digit(phrase):
                distance = 10
            else:
                distance = self.string_distance.distance(phrase, correct_phrase)
            if distance < candidates[-1][1]:
                candidates[-1] = (correct_phrase, distance)
                candidates.sort(key=lambda x:x[1])
        return candidates

    def _wards_correction(self, tokens, prefix_province, province, prefix_district, district,
                          current_district_index, current_distance, current_result_distance):
        result = None
        result_distance = current_result_distance
        district_normalized = district + ',' if len(prefix_district) == 0 else \
            '{} {},'.format(prefix_district, district)
        province_normalized = province if len(prefix_province) == 0 else \
            '{} {}'.format(prefix_province, province)
        for wards_index in range(max(0, current_district_index - 4), current_district_index):
            phrase = ' '.join(tokens[wards_index:current_district_index])
            correct_wards = self.wards.get((province, district), [])
            wards_candidates = self.correct(phrase, correct_wards, distance_threshold=2)
            for wards, wards_distance in wards_candidates:
                new_distance = current_distance + wards_distance
                if new_distance >= result_distance or wards is None:
                    continue
                def check_prefix():
                    new_wards_index = None
                    prefix_wards = None
                    distance = new_distance
                    if wards_index < 1:
                        return new_wards_index, prefix_wards, distance
                    if tokens[wards_index - 1] == 'p':
                        prefix_wards = 'p'
                        new_wards_index = wards_index - 1
                        return new_wards_index, prefix_wards, distance
                    if tokens[wards_index - 1] == 'xã':
                        prefix_wards = 'xã'
                        new_wards_index = wards_index - 1
                        return new_wards_index, prefix_wards, distance
                    if tokens[wards_index - 1] == 'tt':
                        prefix_wards = 'tt'
                        new_wards_index = wards_index - 1
                        return new_wards_index, prefix_wards, distance
                    d = self.string_distance.distance(tokens[wards_index - 1], 'phường')
                    if d < 1:
                        prefix_wards = 'phường'
                        new_wards_index = wards_index - 1
                        distance = d + new_distance
                        return new_wards_index, prefix_wards, distance
                    d = self.string_distance.distance(tokens[wards_index - 1], 'thị trấn')
                    if d <= 2:
                        prefix_wards = 'thị trấn'
                        new_wards_index = wards_index - 1
                        distance = d + new_distance
                        return new_wards_index, prefix_wards, distance
                    if wards_index < 2:
                        return new_wards_index, prefix_wards, distance
                    d = self.string_distance.distance(' '.join(tokens[wards_index - 2:wards_index]), 'thị trấn')
                    if d <= 2:
                        prefix_wards = 'thị trấn'
                        new_wards_index = wards_index - 2
                        distance = d + new_distance
                        return new_wards_index, prefix_wards, distance
                    return new_wards_index, prefix_wards, distance

                new_wards_index, prefix_wards, _ = check_prefix()
                if new_wards_index is None:
                    new_wards_index = wards_index
                wards_normalized = wards + ',' if prefix_wards is None else '{} {},'.format(prefix_wards, wards)
                address_composition = [wards_normalized, district_normalized, province_normalized]
                if new_wards_index > 0:
                    underwards_tokens = tokens[:new_wards_index]
                    correct_underwards = self.underwards[(province, district, wards)]
                    corrected_underwards = None
                    under_wards_index = None
                    for i in range(len(underwards_tokens)-1, max(-1, len(underwards_tokens)-5), -1):
                        if not tokens[i].isalpha():
                            break
                        underwards_phrase = ' '.join(underwards_tokens[i:wards_index])
                        th_distance = 1.5 if len(underwards_phrase) < 6 else 2
                        candidates = self.correct(underwards_phrase, correct_underwards,
                            nb_candidates=1, distance_threshold=th_distance)
                        if candidates[0][0] is not None:
                            corrected_underwards = candidates[0][0]
                            under_wards_index = i
                            break
                    if corrected_underwards is not None:
                        prefix_address = ' '.join(tokens[:under_wards_index] + [corrected_underwards + ','])
                    else:
                        prefix_address = ' '.join(tokens[:new_wards_index]) + ','
                    address_composition = [prefix_address] + address_composition
                result = ' '.join(address_composition)
                result_distance = wards_distance + current_distance
        if result is None and current_distance < 2:
            if not prefix_district:
                result_distance = 4.5
            else:
                result_distance = 4
            prefix_address = ' '.join(tokens[:current_district_index]) + ','
            result = ' '.join([prefix_address, district_normalized , province_normalized])
        return result, result_distance

    def _district_correction(self, tokens, prefix_province, province,
                             current_province_index, current_distance, current_result_distance):
        result = None
        normalized_province = '{} {}'.format(prefix_province, province) if prefix_province else province
        result_distance = current_result_distance
        early_stop_threshold = 0
        stop_correction = False
        for district_index in range(max(0, current_province_index - 4), current_province_index):
            phrase = ' '.join(tokens[district_index:current_province_index])
            correct_districts = self.districts[province]
            district_candidates = self.correct(phrase, correct_districts)
            for district, distance_district in district_candidates:
                new_distance = current_distance + distance_district
                if new_distance >= result_distance or district is None:
                    continue
                if district_index > 0:
                    result_candidate, result_distance_candidate = self._wards_correction(
                        tokens, prefix_province, province, '', district, district_index,
                        new_distance, current_result_distance
                    )
                    if result_distance > result_distance_candidate:
                        result = result_candidate
                        result_distance = result_distance_candidate
                    def check_prefix():
                        new_district_index = None
                        prefix_district = None
                        distance = new_distance
                        if district_index <= 0:
                            return new_district_index, prefix_district, distance
                        d = self.string_distance.distance(tokens[district_index - 1], 'huyện')
                        if d <= 2:
                            prefix_district = 'huyện'
                            new_district_index = district_index - 1
                            distance = d + new_distance
                            return new_district_index, prefix_district, distance
                        if tokens[district_index - 1] == 'tp':
                            prefix_district = 'tp'
                            new_district_index = district_index - 1
                            return new_district_index, prefix_district, distance
                        if tokens[district_index - 1] == 'tx':
                            prefix_district = 'tx'
                            new_district_index = district_index - 1
                            return new_district_index, prefix_district, distance
                        d = self.string_distance.distance(tokens[district_index - 1], 'thành phố')
                        if d < 3:
                            prefix_district = 'thành phố'
                            new_district_index = district_index - 1
                            distance = d + new_distance
                            return new_district_index, prefix_district, distance
                        if district_index < 2:
                            return new_district_index, prefix_district, distance
                        d = self.string_distance.distance(' '.join(tokens[district_index - 2: district_index]), 'thành phố')
                        if d <= 2:
                            prefix_district = 'thành phố'
                            new_district_index = district_index - 2
                            distance = d + new_distance
                            return new_district_index, prefix_district, distance
                        d = self.string_distance.distance(' '.join(tokens[district_index - 2: district_index]), 'thị xã')
                        if d <= 2:
                            prefix_district = 'thị xã'
                            new_district_index = district_index - 2
                            distance = d + new_distance
                            return new_district_index, prefix_district, distance
                        return new_district_index, prefix_district, distance
                    new_district_index, prefix_district, new_distance = check_prefix()
                    if new_district_index is None:
                        continue
                    if new_district_index > 0:
                        result_candidate, result_distance_candidate = self._wards_correction(
                            tokens, prefix_province, province, prefix_district, district,
                            new_district_index, new_distance, current_result_distance
                        )
                        if result_distance > result_distance_candidate:
                            result = result_candidate
                            result_distance = result_distance_candidate
                    else:
                        if new_distance < result_distance:
                            result_distance = new_distance
                            normalized_district = '{} {}'.format(prefix_district, district)
                            result = '{}, {}'.format(normalized_district, normalized_province)
                elif new_distance < result_distance:
                    result = district + ', ' + normalized_province
                    result_distance = new_distance
                if distance_district <= early_stop_threshold:
                    stop_correction = True
                    break
            if stop_correction:
                break
        return result, result_distance

    def _province_correction(self, tokens):
        result_distance = 1000
        result = None
        nb_of_tokens = len(tokens)
        early_stop_threshold = 0
        stop_correction = False
        for index_province in range(max(0, nb_of_tokens - 4), nb_of_tokens):
            phrase = ' '.join(tokens[index_province:])
            province_candidates = self.correct(phrase, self.provinces)
            for province, distance_province in province_candidates:
                if distance_province > result_distance or province is None:
                    continue
                result_candidate, result_distance_candidate = self._district_correction(
                    tokens, '', province, index_province,
                    distance_province, result_distance
                )
                if result_distance_candidate < result_distance:
                    result_distance = result_distance_candidate
                    result = result_candidate
                if index_province > 0:
                    if tokens[index_province-1] == 'tp':
                        if index_province <= 1:
                            result = 'tp ' + province
                            result_distance = distance_province
                            continue
                        result_candidate, result_distance_candidate = self._district_correction(
                            tokens, 'tp', province, index_province - 1,
                            distance_province, result_distance
                        )
                        if result_distance_candidate < result_distance:
                            result_distance = result_distance_candidate
                            result = result_candidate
                    elif self.string_distance.distance(tokens[index_province-1], 'tỉnh') < 2:
                        if index_province <= 1:
                            result = 'tỉnh ' + province
                            result_distance = distance_province
                            continue
                        result_candidate, result_distance_candidate = self._district_correction(
                            tokens, 'tỉnh', province, index_province-1,
                            distance_province, result_distance
                        )
                        if result_distance_candidate < result_distance:
                            result_distance = result_distance_candidate
                            result = result_candidate
                if index_province <= 0:
                    if distance_province < result_distance:
                        result_distance = distance_province
                        result = province
                if distance_province <= early_stop_threshold:
                    stop_correction = True
                    break
            if stop_correction:
                break
        return result, result_distance

    def address_correction(self, address, correct_th=5):
        '''
        Address should be in format: Ngõ ngách... đường... quận/huyện...tỉnh/thành phố
        and only contain characters
        Return: (corrected_address: str, distance: float)
            corrected_address: address after corrected. In case address can't corrected, return
            input address
            distance: distance between corrected address and input address. In case address
            can't correct, return -1
        '''
        if not isinstance(address, str):
            raise ValueError('Address must be a string')
        tokens = address.split()
        prefix_number = ('số', 'đội', 'xóm', 'khu', 'ngách', 'đường', 'tổ', 'ngõ')
        for i in range(1, min(5, len(tokens))):
            if not tokens[i].isalpha():
                corrected_token = self.correct(tokens[i-1], prefix_number, nb_candidates=1, distance_threshold=0.5)[0]
                if corrected_token[0] is not None:
                    tokens[i-1] = corrected_token[0]
        result, distance_result = self._province_correction(tokens)
        if distance_result <= correct_th:
            return result, distance_result
        else:
            return address, -1
