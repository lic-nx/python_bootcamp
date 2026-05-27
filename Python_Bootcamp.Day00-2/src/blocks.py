import sys

# пробуем замыкание

def cleaner(param):
    lines = []
    for i in range(param):
        line = input()
        if len(line) == 32:
            if line[:5] == '00000' and line[5] != '0':
                lines.append(line)
    return lines

if __name__ == '__main__':
    param = sys.argv[1]
    if not param.isdigit():
        raise  ("param must be integer")
    param = int(param)
    print(*cleaner(param), sep='\n')
