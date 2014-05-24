from socialanalyzer.queries import *

def readEmploy(fname='data/Employment.csv'):
    employArray= []
    with open(fname, 'rbU') as c:
        creader = csv.reader(c, delimiter=',')
        firstLine = True
        for row in creader:
            if firstLine:
                firstLine = False
            else:    
                for i in range(1,len(row)):
                    if row[i] != '':
                        line = filter(lambda x: x != "'", row[i])
                        if i>=len(employArray):
                            employArray.append([line])
                        else:
                            employArray[i-1].append(line)
    return filter(lambda x: len(x) > 0, employArray)

def readEmploy2(fname='data/Employment.csv'):
    def _column(matrix, i):
        return [row[i] for row in matrix]

    cols = []

    with open(fname, 'rbU') as f:
        reader = csv.reader(f, delimiter=',')
        rows = []
        for row in reader:

            rows.append(row)

        for i in range(len(rows[0])):
            cols.append(_column(rows, i))
        cols_clean = []
        for col in cols:
            cols_clean.append([x for x in col if x != ''])
    return cols_clean

def readZip(fname='data/Location10th.tsv'):
    zipArray= []
    with open(fname, 'rb') as c:
        creader = csv.reader(c, delimiter='\t')
        firstLine = True
        for row in creader:
            zipArray.append(row[0])
    return [zipArray[0]] + map(int, zipArray[1:])

funEmploy = [employerInList, "Employer" , readEmploy2()]
funAge = [age, "Age", [["15-24", 15,24], ["25-34", 25,34], ["35-44", 35,44], ["45-54", 45, 54], ["55-64", 55, 64], ["65+", 65, 200]]]
funSex = [sex, "Sex", ["Mm", "Ff", "Oo"]]
funCurrentCity  = [ currentCityInList, "Current City", [ readZip(), ["Illinois", "Illinois"]]]
funHometown  = [hometownInList, "Hometown", [readZip(), ["Illinois", "Illinois"]]]
funHighSchool = [highSchoolInList, "High School", [readZip(), ["Illinois", "Illinois"]]]
funCollege = [collegeInList, "College", [readZip(), ["Illinois", "Illinois"]]]

uDict = dict()
funArray = [funEmploy, funAge , funSex, funCurrentCity, funHometown, funHighSchool, funCollege]

def binOr(x,y):
    return bin(int(x,2)|int(y,2))[2:]

def buildTree(depth = 0, funcArray = [], filters=None, printString = ""):

    if filters is not None: 
        users = FacebookUser.query.filter(filters).all()
        length = len(users)
    else: 
        users = []
        length = 0

    line = printString + " : " + str(length)
    print line 
    # f.write(line + "\n")

    if depth < len(funcArray):

        if depth == 0:

            for x in funcArray[depth][2]:
                buildTree(
                    depth + 1, 
                    funcArray, 
                    funcArray[depth][0](x[1:]), 
                    funcArray[depth][1] + ": " + str(x[0])
                )

            buildTree(
                depth +1, 
                funcArray, 
                funcArray[depth][0](unknown=True), 
                funcArray[depth][1] + ": Unknown" 
            )

        else:

            for x in funcArray[depth][2]:   
                buildTree(depth +1, funcArray, 
                    and_(
                        filters, 
                        funcArray[depth][0](x[1:])
                    ), 
                    printString + ", " + funcArray[depth][1] + ": " + str(x[0])
                )

            buildTree(depth +1, funcArray, 
                and_(
                    filters, 
                    funcArray[depth][0](unknown=True)
                ), 
                printString + ", " + funcArray[depth][1] + ": Unknown"
            )

    elif length>0:
        # print printString + " Count : " + str(length)
        
        bitstring = ""
        for i in range(len(funcArray)):
            seg = printString.split(",")[i]
            cat = seg.split(":")[1][1:]
            cats = map(lambda x: x[0], funcArray[i][2])+["Unknown"]
            pos = cats.index(cat)
            bitstring += "0"*pos + "1" + ("0"*(len(cats)-pos-1))
        for q in users:
            if q.uid in uDict:
                uDict[q.uid] = binOr(bitstring, uDict[q.uid])
            else:
                uDict[q.uid] = bitstring


# print len(readEmploy())
# for i in range(len(funArray)):
f2 = open("bitarrays.txt", 'w')
buildTree(funcArray=funArray[0:])
for uid, bitstring in uDict.items():
    f2.write(str(uid) + ":" + bitstring)