#!/usr/bin/python3

import sqlite3
import json
from sys import argv

print_number = argv[1]

connection = sqlite3.connect("scorelib.dat")
cursor = connection.cursor()

composers = cursor.execute("SELECT person.name, person.born, person.died FROM print JOIN edition JOIN score JOIN score_author JOIN person "
                    "WHERE print.edition = edition.id "
                    "AND edition.score = score.id "
                    "AND score.id = score_author.score "
                    "AND score_author.composer = person.id "
                    "AND print.id = ?", (print_number,)).fetchall()

list = []
for composer in composers:
    prepareComposer = {}
    prepareComposer["name"] = composer[0]
    if composer[1]:
        prepareComposer["born"] = composer[1]
    if composer[2]:
        prepareComposer["died"] = composer[2]
    list.append(prepareComposer)


print(json.dumps(list, indent=4, ensure_ascii=False))
cursor.close()
