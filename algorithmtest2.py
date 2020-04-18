import random
bias = -0.03
a =  50*(1 + random.uniform(-0.0575 + bias,0.0425 + bias))
b = []
count = 0
count2 = 0
while (count2<=2):
    while (count<40):
        a = a*(1 + random.uniform(-0.0575 + bias,0.0425 + bias))
        count += 1
        b.append(a)
    count2 += 1
print(a)