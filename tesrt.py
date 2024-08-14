# is 
names1=("ahmed omar ali salam").split(" ") 
games1=("99,99,89,90").split(",")
# { key : vlue }
# [1,2] [3,4] 
dict1 = dict(zip(names1,games1)) 
if len(names1) != len(games1) :
    print("The names and grades are not matching") 
sum1 = 0 
for int(i) in games1 : 
    sum1 += i 
average = sum1 / len(names1)


# step 1 completed 
for name , grade in dict1.items() :
    print(f"{name} go to {grade}")

average = sum1/ len(names1) 
print(f"the average value is :{average}")

MaxGrade = max(games1) 

print("The Highest grades :")
for name , grade in dict1.items() : 
    if grade == MaxGrade : 
        print(f"{name} -> {grade}")

# # for grade in games1 : 
#     intgrade = int(grade) 
#     sum += intgrade
