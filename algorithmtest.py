import random
a = 50
b = []
c = 0.01
count = 0
while (count<100):
    b.append(a*(1 + random.uniform(-0.0575 + c,0.0425 + c)))
    count += 1
sum = 0
for x in b:
    sum += x
average = (sum/len(b))
print (average)