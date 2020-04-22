a = [1,2,3,4,5]
count = 0
while count < 4:
    a[count] = a[count+1]
    count += 1
print(a)