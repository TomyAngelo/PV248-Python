#!/usr/bin/env python

from sys import argv
import re
import numpy


def parseLine(line):
    equation, result = line.split('=')
    objects = equation.split()
    result = int(result)

    dict = {}
    sign = int(1)
    for obj in objects:
        if (obj != "+" and obj != "-"):
            parseObj = re.search(r"(\d*)([a-z])", obj)
            if parseObj.group(1) == "":
                digit = 1
            else:
                digit = int(parseObj.group(1))

            var = parseObj.group(2)
            digit = digit * sign
            dict[var] = digit
        else:
            if obj == "+" :
                sign = 1
            else:
                sign = -1
    return (dict, result)


input = argv[1]
equations = []
with open(input) as file:
    for line in file:
        lineTuple = parseLine(line)
        equations.append(lineTuple)

#adding missing 0s
for equa in equations:
    for key, value in equa[0].items():
        for tuple in equations:
            if not key in tuple[0]:
                tuple[0][key] = 0

#transform dicts to matrix
matrix = []
results = []
for equa in equations:
    row = []
    results.append(equa[1])
    for key, value in sorted(equa[0].items()):
        row.append(value)
    matrix.append(row)


###########################3
for m in matrix:
    print(m)

print(results)

#########################

numpyMatrix = numpy.array(matrix)
numpyResults = numpy.array(results)

rankOfMatrix = numpy.linalg.matrix_rank(numpyMatrix)
rankOfMatrixWithResults = numpy.linalg.matrix_rank(numpy.column_stack((numpyMatrix, numpyResults)))

if rankOfMatrix != rankOfMatrixWithResults:
    print("no solution")
elif rankOfMatrix < len(matrix[0]):
    print("solution space dimension: %d" % (len(matrix[0]) - rankOfMatrix))
else:
    solution = numpy.linalg.solve(numpyMatrix,numpyResults)

    result = []
    counter = 0
    for key, value in sorted(equations[0][0].items()):
        var = key + " = " + str(solution[counter])
        result.append(var)
        counter += 1

    print("solution: " + ", ".join(result))



#######################
for e in equations:
    for key, value in e[0].items():
        print(str(value) + key + " ")

    print(e[1])
    print()
    #####################