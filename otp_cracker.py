import re
import requests
import string
from sys import argv
import argparse


#ACCEPTED = [' ', '.', ',', '!', '?', '-', '"', "'", ":"]
ACCEPTED = [' ', '.', ',', '!', '?', '-',]



def xor(x, y):
    if x == y:
        return 0
    else:
        return 1



def xor_ciphers(c1, c2):
    res = []

    for i in range(min(len(c1), len(c2))):
        if c1[i] != " " and c2[i] != " ":
            res.append(xor(c1[i], c2[i]))

    return res



def is_space(ciphers, current, column):
    for row in ciphers:
        xored = row[column]^current

        if not (chr(xored).isalpha() or xored == 0):
            return False
        
    return True



def load_ciphers(file_name):
    with open(file_name) as f:
        text = f.read()

    ciphers = [[int(byte, 2) for byte in cipher.split(" ")] for cipher in text.split("\n\n")]

    return ciphers



def find_spaces(ciphers, letter, key):
    length = min(list(map(len, ciphers)))

    for row in ciphers:
        for i in range(length):
            #if is_space(ciphers, row[i], i):
            if is_decodable(ciphers, i, row[i]^ord(letter), letter):
                key[i] = row[i]^ord(letter)

    return key



def get_words(cipher, key):
    decoded = []

    for i in range(len(key)):
        if key[i] != -1:
            decoded.append(chr(cipher[i]^key[i]))
        else:
            decoded.append(chr(0))
        
    dec_str = "".join(decoded)

    words = {dec_str.find(word) : word.replace(chr(0), ".") for word in dec_str.split(" ")}

    return words



def diff(a, b):
    res = []

    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            res.append(i)

    return res



def is_decodable(ciphers, column, key, char):
    global ACCEPTED

    char_found = False

    for row in ciphers:
        xored = row[column]^key

        if chr(xored) == char:
            char_found = True

        #if not (chr(xored).isalnum() or chr(xored) in ACCEPTED or xored == 0):
        if not (chr(xored).isalpha() or chr(xored) in ACCEPTED):
            return False
        
    if char_found:
        return True
    else:
        return False



def get_key(dictionary, val):
    for key, value in dictionary.items(): 
        if val == value: 
            return key
    return None



def check_dictionary(ciphers, key, dictionary, ranges):

    changed = True

    #while changed:
    changed = False

    for row in range(len(ciphers)):
        words = get_words(ciphers[row], key)
        
        for word in words.values():
            
            if 0 < word.count('.') < len(word):
                
                word_lower = word.lower()
                if not word.startswith('.'):
                    try:
                        matched = list(set(re.findall("\\b" + word_lower + "\\b",
                                        dictionary[ranges[word_lower[0]][0] : ranges[word_lower[0]][1]])))
                    except:
                        continue
                else:
                    try:
                        matched = list(set(re.findall("\\b" + word_lower + "\\b", dictionary)))
                    except:
                        continue

            
                if len(matched) == 1:
                    for pos in diff(matched[0], word):
                        if word[pos] == '.':
                            column = get_key(words, word)
                            if is_decodable(ciphers, column+pos, ord(matched[0][pos])^ciphers[row][column + pos], matched[0][pos]):
                                key[column+pos] = ord(matched[0][pos])^ciphers[row][column + pos]
                                changed = True
                                #print(matched)
            
   return key



def decode(encoded, key):
    decoded = ["_"] * len(encoded)

    for i in range(min(len(encoded), len(key))):
        if key[i] > 0:
            decoded[i] = chr(encoded[i]^key[i])

    return "".join(decoded)



def download(indeks):
    x = requests.get(f"https://zagorski.im.pwr.wroc.pl/courses/sec2020/l2.php?id={indeks}")

    text = x.text.split("<br />")
    res = []

    for line in text:
        line = line.strip()
        if line.startswith("0") or line.startswith("1"):
            res.append( list(map(lambda x: int(x, 2), line.split(" "))))

    return res



def dictionary_ranges(dictionary):
    ranges = {c: [0, len(dictionary)] for c in string.ascii_lowercase}

    for i in range(1, len(string.ascii_lowercase)):
        try:
            temp = dictionary.index(f"\n{string.ascii_lowercase[i]}")
        except ValueError:
            continue
        ranges[string.ascii_lowercase[i-1]][1] = temp
        ranges[string.ascii_lowercase[i]][0] = temp

    ranges[string.ascii_lowercase[-1]][1] = len(dictionary)

    return ranges



def get_args():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument("-i", action="store",
                            type=str, required=True)
    my_parser.add_argument("-l", action="store",
                            type=str, required=True)
    my_parser.add_argument("-d", action="store_true")

    return my_parser.parse_args()



def main():
    '''with open("to_decode.txt") as f:
        encoded = list(map(lambda x: int(x, 2), f.read().split(" ")))
    
    ciphers = load_ciphers("ciphers.txt")'''

    args = get_args()

    downloaded = download(args.i)

    ciphers = downloaded[:eval(args.l)]
    encoded = downloaded[-1]

    length = len(encoded)

    for i in range(len(ciphers)):
        ciphers[i] = ciphers[i][:length+20]


    key = [-1] * len(ciphers[0])

    if args.d:
        chars = [' ']
    else:
        chars = [' ', 'a', 'i', 'o', 'e']

    for s in chars:
        key = find_spaces(ciphers, s, key)


    if args.d:
        with open("slowa.txt") as f:
            dictionary = f.read()
            ranges = dictionary_ranges(dictionary)
            key = check_dictionary(ciphers, key, dictionary, ranges)


    for c in ciphers:
        print(decode(c, key))

    print("\n" + decode(encoded, key))


if __name__ == "__main__":
    main()