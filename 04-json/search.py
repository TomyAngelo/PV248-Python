#!/usr/bin/python3

import sqlite3
import json
from sys import argv

class MyPrintClass():
    def __init__(self, id, composers, title, genre, key, year, edition, editors, voices, partiture, incipit):
        self.id = id
        self.composers = composers
        self.title = title
        self.genre = genre
        self.key = key
        self.year = year
        self.edition = edition
        self.editors = editors
        self.voices = voices
        self.partiture = partiture
        self.incipit = incipit

def findPrintsByComposerId(cursor, id):
    ourPrints = cursor.execute("SELECT DISTINCT print.id FROM print JOIN edition JOIN score JOIN score_author JOIN person "
                               "WHERE print.edition = edition.id "
                               "AND edition.score = score.id "
                               "AND score.id = score_author.score "
                               "AND score_author.composer = person.id "
                               "AND person.id = ?", (id,)).fetchall()

    list = []
    for printId in ourPrints:
        list.append( loadPrintFromDb(cursor, printId[0]) )

    return list


def loadPrintFromDb(cursor, printId):
    ourPrint = cursor.execute("SELECT partiture, edition FROM print WHERE id = ? ", (printId,)).fetchall()

    partiture = ourPrint[0][0]
    ourEdition = cursor.execute("SELECT score, name FROM edition WHERE id = ?", (ourPrint[0][1],)).fetchall()

    edition = ourEdition[0][1]
    ourScore = cursor.execute("SELECT name, genre, key, incipit, year FROM score WHERE id = ?", (ourEdition[0][0],)).fetchall()

    title = ourScore[0][0]
    genre = ourScore[0][1]
    key = ourScore[0][2]
    incipit = ourScore[0][3]
    year = ourScore[0][4]

    voices = cursor.execute("SELECT range, name FROM voice WHERE score = ?", (ourEdition[0][0],)).fetchall()

    composers = cursor.execute("SELECT person.name, person.born, person.died FROM score JOIN score_author JOIN person "
                               "WHERE score_author.score = score.id "
                               "AND score_author.composer = person.id "
                               "AND score.id = ?",(ourEdition[0][0],)).fetchall()

    editors = cursor.execute("SELECT person.name, person.born, person.died FROM edition JOIN edition_author JOIN person "
                             "WHERE edition_author.edition = edition.id "
                             "AND edition_author.editor = person.id "
                             "AND edition.id = ?", (ourPrint[0][1],)).fetchall()

    tmpClass = MyPrintClass(printId, composers, title, genre, key, year, edition, editors, voices, partiture, incipit)

    return changeClassToDict(tmpClass)


def changeClassToDict(myClass):
    result = {}
    result["Print Number"] = myClass.id
    result["Composer"] = formatPersons(myClass.composers)
    if myClass.title :
        result["Title"] = myClass.title
    else:
        result["Title"] = None

    if myClass.genre:
        result["Genre"] = myClass.genre
    else:
        result["Genre"] = None

    if myClass.key:
        result["Key"] = myClass.key
    else:
        result["Key"] = None

    if myClass.year:
        result["Composition Year"] = myClass.year
    else:
        result["Composition Year"] = None

    if myClass.edition:
        result["Edition"] = myClass.edition
    else:
        result["Edition"] = None

    if myClass.editors:
        result["Editor"] = formatPersons(myClass.editors)
    else:
        result["Editor"] = None

    if myClass.voices:
        result["Voices"] = formatVoices(myClass.voices)
    else:
        result["Voices"] = None

    if myClass.partiture:
        if myClass.partiture == 'Y':
            result["Partiture"] = True
        else:
            result["Partiture"] = False
    else:
        result["Partiture"] = None

    if myClass.incipit:
        result["Incipit"] = myClass.incipit
    else:
        result["Incipit"] = None

    return result


def formatPersons(persons):
    result = []
    for person in persons:
        onePerson = {}
        onePerson["name"] = person[0]
        if person[1]:
            onePerson["born"] = person[1]
        if person[2]:
            onePerson["died"] = person[2]
        result.append(onePerson)

    return result


def formatVoices(voices):
    result = []
    for voice in voices:
        oneVoice = {}
        if voice[0]:
            oneVoice["range"] = voice[0]
        else:
            oneVoice["range"] = None

        if voice[1]:
            oneVoice["name"] = voice[1]
        else:
            oneVoice["name"] = None

        result.append(oneVoice)

    return result


inputName = argv[1]

connection = sqlite3.connect("scorelib.dat")
cursor = connection.cursor()

composers = cursor.execute("SELECT person.id, person.name FROM person WHERE person.name LIKE ?",
                           ("%" + inputName + "%",)).fetchall()
myDict = {}
for composer in composers:
    composerName = composer[1]
    listOfPrints = findPrintsByComposerId(cursor, composer[0])
    myDict[composerName] = listOfPrints

print(json.dumps(myDict, indent=4, ensure_ascii=False))
cursor.close()