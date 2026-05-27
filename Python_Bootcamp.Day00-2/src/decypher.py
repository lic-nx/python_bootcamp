import sys
if __name__ == '__main__':
    input_str = sys.argv[1]
    answer_row = ''
    print(input_str)
    for i in input_str.split(' '):
        answer_row += i[0]
    print(answer_row)