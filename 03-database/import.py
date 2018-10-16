#!/usr/bin/python3

import sqlite3
from sys import argv
import scorelib

input = argv[1]
output = argv[2]

connection = sqlite3.connect(output)
cursor = connection.cursor()

with open("scorelib.sql") as schemaFile:
    schema = schemaFile.read()
    cursor.executescript(schema)
    connection.commit()

def storePerson(cursor, person):
    # check if person is already in database
    cursor.execute("SELECT id, born, died FROM person WHERE person.name = ?", (person.name,))
    row = cursor.fetchone()
    if row == None:
        # person in not in database
        cursor.execute("INSERT INTO person(born, died, name) VALUES(?, ?, ?)",
                       (person.born, person.died, person.name))
    else:
        # person is in database
        if (person.born is not None or person.died is not None) and \
                (row[1] is None and row[2] is None):
            cursor.execute("UPDATE person SET born = ?, died = ? WHERE name = ?",
                           (person.born, person.died, person.name))
    return cursor.lastrowid

def storeComposition(cursor, composition):
    cursor.execute("INSERT INTO score(name, genre, key, incipit, year) VALUES(?, ?, ?, ?, ?)",
                   (composition.name, composition.genre, composition.key, composition.incipit,
                   composition.year) )
    return cursor.lastrowid

def storeScoreAuthor(cursor, compositionId, personId):
    cursor.execute("INSERT INTO score_author(score, composer) VALUES(?, ?)",
                   (compositionId, personId) )

def storeEdition(cursor, edition, scoreId):
    cursor.execute("INSERT INTO edition(score, name) VALUES(?, ?)",
                   (scoreId, edition.name) )
    return cursor.lastrowid


def storeEditionAuthor(cursor, edition_id, personId):
    cursor.execute("INSERT INTO edition_author(edition, editor) VALUES(?, ?)",
                   (edition_id, personId) )


def storeVoice(cursor, voice, counter, compositionId):
    cursor.execute("INSERT INTO voice(number, score, range, name) VALUES(?, ?, ?, ?)",
                   (counter, compositionId, voice.range, voice.name) )

def storeOnePrint(cursor, print, edition_id):
    if print.partiture :
        part = 'Y'
    else:
        part = 'N'

    cursor.execute("INSERT INTO print(id, partiture, edition) VALUES(?, ?, ?)",
                   (print.print_id, part, edition_id) )


def storeAllPrints(cursor, itemPrint):

    #store score/composition
    tmpCom = itemPrint.composition()
    cursor.execute("SELECT * FROM score WHERE name IS ? AND genre IS ? AND key IS ? AND incipit IS ? AND year IS ?",
                   (tmpCom.name, tmpCom.genre, tmpCom.key, tmpCom.incipit, tmpCom.year))

    row = cursor.fetchone()
    if row == None :
        compositionId = storeComposition(cursor, itemPrint.edition.composition)
    else:
        compositionId = row[0]

    # store edition
    cursor.execute("SELECT * FROM edition WHERE name IS ? AND score IS ?",
                   (itemPrint.edition.name, compositionId))

    row = cursor.fetchone()
    if row == None:
        edition_id = storeEdition(cursor, itemPrint.edition, compositionId)
    else:
        edition_id = row[0]

    # store composers and score_authors
    for person in itemPrint.edition.composition.authors:
        personId = storePerson(cursor, person)
        storeScoreAuthor(cursor, compositionId, personId)

    #store editors and edition
    for person in itemPrint.edition.authors:
        personId = storePerson(cursor, person)
        storeEditionAuthor(cursor, edition_id , personId)

    #store voices
    counter = 1
    for voice in itemPrint.edition.composition.voices:
        storeVoice(cursor, voice, counter, compositionId)
        counter += 1

    #store print
    storeOnePrint(cursor, itemPrint, edition_id)

prints = scorelib.load(input)
for item in prints:
    storeAllPrints(cursor, item)

connection.commit()
connection.close()