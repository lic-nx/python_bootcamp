m_matrix = [['*',' ',' ',' ','*'],
            ['*','*',' ','*','*'],
            ['*',' ','*',' ','*']]
if __name__ == '__main__':
    with open('m.txt') as f:
        lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        if len(lines) != 3:
            print("Error")
            exit()
        for i in range(len(lines)):
            if len(lines[i]) != 5 :
                print("Error")
                exit()
            for j in range(len(lines[i])):
                if (m_matrix[i][j] != '*' and lines[i][j] == '*') or (m_matrix[i][j] == '*' and lines[i][j] != '*'):
                    print('False')
                    exit()
    print ("True")