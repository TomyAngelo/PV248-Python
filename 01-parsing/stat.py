#!/usr/bin/python3

import sys
import collections
import re

f = open(sys.argv[1],'r')

def takeSecond(elem):
    return elem[1]

if sys.argv[2] == "composer":
    c = collections.Counter()

    for line in f:
        if ( "Composer:" in line ):
            line2 = re.sub( "Composer: " , '' , line ).strip()
            composersList = line2.split( ';' )
            for composer in composersList:
                composer = composer.translate({ord(i):None for i in '0123456789()-/+'}).strip()
                composer += ":"
                c.update({composer:1})

    for key,value in sorted( c.items(), key = takeSecond,reverse = True ):
        if key != ":" :
           print( key, value )

if sys.argv[2] == "century":
    c = collections.Counter()

    for line in f:
        if( "Composition Year: " in line ):
            if ( "century" in line ):
                year = re.search( "\d\d", line )
                century = int( year.group(0) )
                c.update({century:1})
            else:    
                year = re.search( "(\d{4}\.\d+|\d{4})" , line )
                if year :
                    century = int( year.group(0) )
                    century = ( -(-century // 100) )
                    c.update({century:1})

    for key, value in sorted( c.items() ):
        print( str( key ) + "th century:" + str( value ) )

if sys.argv[2] == "c_minor":
    i=0
    for line in f:
        if( "Key: c minor" in line ):
            i +=1
    print(i)

