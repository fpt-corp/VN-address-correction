class StringDistance:
    '''
    Implement distance between two strings use edit distance
    '''
    def __init__(self, cost_dict_path=None):
        self.cost_dict = dict()
        if cost_dict_path is not None:
            self.load_cost_dict(cost_dict_path)

    def load_cost_dict(self, filepath):
        if self.cost_dict is None:
            self.cost_dict = dict()
        with open(filepath) as f:
            for line in f:
                char1, char2, cost = line.strip().split('\t')
                if char1 and char2:
                    self.cost_dict[(char1, char2)] = int(cost)

    def distance(self, source, target):
        '''
        Levenshtein distance between source string and target string
        '''
        if source == target: return 0
        elif len(source) == 0: return len(target)*10
        elif len(target) == 0: return len(source)*10
        v0 = [None] * (len(target) + 1)
        v1 = [None] * (len(target) + 1)
        for i in range(len(v0)):
            v0[i] = i * 10
        for i in range(len(source)):
            v1[0] = (i + 1)*10
            for j in range(len(target)):
                cost = 0 if source[i] == target[j] else self.cost_dict.get((source[i], target[j]), 8)
                v1[j + 1] = min(v1[j] + 10, v0[j + 1] + 10, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(target)]

def extract_digit(text: str):
    res = ''
    for char in text:
        if char.isdigit():
            res += char
    return res