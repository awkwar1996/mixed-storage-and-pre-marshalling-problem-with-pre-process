import numpy as np

yard = [[2,3,4,5,2,4],
        [2,3,5,4,1,3],
        [5,3,4,2,1,3]]
plateNum = [2,4,5,4,3]
plate_index = [sum(plateNum[:i]) for i in range(len(plateNum))]
    #1.确定出库顺序
allocation = [[-1 for i in range(len(yard[s]))] for s in range(3)]
for h in range(6)[::-1]:
    for s in range(3):
        if len(yard[s]) >= h + 1:
            allocation[s][h] = plate_index[yard[s][h] - 1]
            plate_index[yard[s][h] - 1] += 1
print(allocation)

a = np.array([1.0,2,3])
b = np.array([4,5,6])
d=np.array([1,0,1])
c = (a**1+b**2)*d
print(c)
print(c[0]==17)