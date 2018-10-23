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
        return cursor.lastrowid
    else:
        # person is in database
        if (person.born is not None or person.died is not None) and \
                (row[1] is None and row[2] is None):
            cursor.execute("UPDATE person SET born = ?, died = ? WHERE name = ?",
                           (person.born, person.died, person.name))
        return row[0]


def storeComposition(cursor, composition):
    cursor.execute("INSERT INTO score(name, genre, key, incipit, year) VALUES(?, ?, ?, ?, ?)",
                   (composition.name, composition.genre, composition.key, composition.incipit,
                   composition.year) )

    compositionId = cursor.lastrowid
    # store composers and score_authors
    if len(composition.authors) != 0:
        for person in composition.authors:
            personId = storePerson(cursor, person)
            storeScoreAuthor(cursor, compositionId, personId)

    #store voices
    counter = 1
    for voice in composition.voices:
        storeVoice(cursor, voice, counter, compositionId)
        counter += 1

    return compositionId

def storeScoreAuthor(cursor, compositionId, personId):
    cursor.execute("INSERT INTO score_author(score, composer) VALUES(?, ?)",
                   (compositionId, personId) )

def storeEdition(cursor, edition, scoreId):
    cursor.execute("INSERT INTO edition(score, name) VALUES(?, ?)",
                   (scoreId, edition.name) )

    editionId = cursor.lastrowid

    #store editors and edition
    if len(edition.authors) != 0:
        for person in edition.authors:
            personId = storePerson(cursor, person)
            storeEditionAuthor(cursor, editionId , personId)

    return editionId


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


def isCompositionAlreadyInTable(cursor, composition):
    foundCompositions = cursor.execute("SELECT * FROM score WHERE name IS ? "
                                       "AND genre IS ? "
                                       "AND key IS ? "
                                       "AND incipit IS ? "
                                       "AND year IS ?",
                   (composition.name, composition.genre, composition.key, composition.incipit, composition.year))\
                        .fetchall()

    if not foundCompositions: return (False, None)

    for foundCompo in foundCompositions:
        #check authors
        newAuthors = cursor.execute( "SELECT person.name FROM person JOIN score_author WHERE score_author.score = ? "
                        "AND score_author.composer = person.id",(foundCompo[0],)).fetchall()

        newAuthorsList = []
        for aut in newAuthors:
            newAuthorsList.append( aut[0] )

        if len(composition.authors) != len(newAuthorsList):
            return (False, None)

        for person in composition.authors:
            if person.name not in newAuthorsList:
                return (False, None)

        #authors are the same
        #check voices
        newVoices = cursor.execute("SELECT voice.name, voice.range FROM voice WHERE voice.score = ?",
                                   (foundCompo[0],)).fetchall()

        newVoicesList = []
        for voice in newVoices:
            newVoicesList.append( (voice[0], voice[1]) )

        if len(composition.voices) != len(newVoicesList):
            return (False, None)

        for voice in composition.voices:
            tuple = (voice.name, voice.range)
            if tuple not in newVoicesList:
                return (False, None)

        #voices are the same so this composition is already in the table
        return (True, foundCompo[0])

def isEditionAlreadyInTable(cursor, edition):
    foundEditions = cursor.execute("SELECT * FROM edition WHERE name IS ?",(edition.name,) ).fetchall()

    if not foundEditions: return (False, None)

    for foundEdit in foundEditions:
        #check editors
        newEditors = cursor.execute( "SELECT person.name FROM person JOIN edition_author WHERE edition_author.edition = ? "
                        "AND edition_author.editor = person.id",(foundEdit[0],)).fetchall()

        newEditorsList = []
        for aut in newEditors:
            newEditorsList.append( aut[0] )

        if len(edition.authors) != len(newEditorsList):
            return (False, None)

        for person in edition.authors:
            if person.name not in newEditorsList:
                return (False, None)

        #check if compositions are the same
        newComposition = cursor.execute("SELECT * FROM score WHERE score.id = ?",(foundEdit[1],)).fetchone()
        if edition.composition.name != newComposition[1]: return (False, None)
        if edition.composition.genre != newComposition[2]: return (False, None)
        if edition.composition.key != newComposition[3]: return (False, None)
        if edition.composition.incipit != newComposition[4]: return (False, None)
        if edition.composition.year != newComposition[5]: return (False, None)

        # check authors
        newAuthors = cursor.execute("SELECT person.name FROM person JOIN score_author WHERE score_author.score = ? "
                                    "AND score_author.composer = person.id", (newComposition[0],)).fetchall()

        newAuthorsList = []
        for aut in newAuthors:
            newAuthorsList.append(aut[0])

        if len(edition.composition.authors) != len(newAuthorsList):
            return (False, None)

        for person in edition.composition.authors:
            if person.name not in newAuthorsList:
                return (False, None)

        # authors are the same
        # check voices
        newVoices = cursor.execute("SELECT voice.name, voice.range FROM voice WHERE voice.score = ?",
                                   (newComposition[0],)).fetchall()

        newVoicesList = []
        for voice in newVoices:
            newVoicesList.append((voice[0], voice[1]))

        if len(edition.composition.voices) != len(newVoicesList):
            return (False, None)

        for voice in edition.composition.voices:
            tuple = (voice.name, voice.range)
            if tuple not in newVoicesList:
                return (False, None)

        return (True, foundEdit[0])

def storeAllPrints(cursor, itemPrint):
    #store composition, score authors and voices
    tupleBooleanAndIdComposition = isCompositionAlreadyInTable(cursor, itemPrint.composition())
    compositionId = tupleBooleanAndIdComposition[1]
    if not tupleBooleanAndIdComposition[0]:
        compositionId = storeComposition(cursor, itemPrint.composition())

    #store edition and edition author
    tupleBooleanAndIdEdition = isEditionAlreadyInTable(cursor,itemPrint.edition)
    editionId = tupleBooleanAndIdEdition[1]
    if not tupleBooleanAndIdEdition[0]:
        editionId = storeEdition(cursor, itemPrint.edition, compositionId)

    #store print
    storeOnePrint(cursor, itemPrint, editionId)


prints = scorelib.load(input)
for item in prints:
    storeAllPrints(cursor, item)

connection.commit()
connection.close()