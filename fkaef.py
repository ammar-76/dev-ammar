sequence = [23, 35, 53, 46, 66]

for i in range(1 , len(sequence)) : 
    curretn = sequence[i] 
    previous = sequence[ i - 1] 
    print(f'{curretn} {previous}')