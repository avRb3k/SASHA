import json

# file = open('komplimente.txt','r',encoding='utf-8')
# #file = open('komplimente.txt','r')
liste = []

with open('komplimente.txt','r',encoding='utf-8') as file:
    zeig = file.readlines()

z = 0

for i in zeig:
    if (z % 2) == 0:
        i = i.replace("\n"," ")
        i = i.replace("Du", "Anna du")
        i = i.replace("Dein", "Anna dein")
        i = i.replace("Ich", "Anna ich")
    else:
        i = i.replace("\n"," Anna")
    z += 1
    liste.append(i)


print(liste)

with open('komplimente.json','w') as json_file:
    json.dump(liste, json_file)
