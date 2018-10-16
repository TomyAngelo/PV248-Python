import re

class Print():
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        print("Print Number: %d" % self.print_id)
        print("Composer: ", end = '' )
        for composer in self.composition().authors:
            print(composer.name, end = '' )
            if composer.born is not None and composer.died is not None:
                print(" (" + str(composer.born) + "--" + str(composer.died) + ")", end='')
            if composer.born is not None and composer.died is None:
                print(" (" + str(composer.born) + "--)", end='')
            if composer.born is None and composer.died is not None:
                print(" (--" + str(composer.died) + ")", end='')
            if composer != self.composition().authors[len(self.composition().authors)-1]:
                print("; ", end='')
        print("")
        
        if self.composition().name is None:
            print("Title: ")
        else:
            print("Title: " + self.composition().name )
       
        if self.composition().genre is None:
            print("Genre: ")
        else:
            print("Genre: " + self.composition().genre )

        if self.composition().key is None:
            print("Key: ")
        else:
            print("Key: " + self.composition().key )

        if self.composition().year is None:
            print("Composition Year: ")
        else:
            print("Composition Year: %d" % self.composition().year )

        if self.edition.name is None:
            print("Edition: ")
        else:
            print("Edition: " + self.edition.name)

        print("Editor: ", end='')
        if self.edition.authors is not None:
            for editor in self.edition.authors:
                print(editor.name, end='')
                if editor != self.edition.authors[len(self.edition.authors)-1]:
                    print(", ", end='')
        print("")

        counter = 1
        for voice in self.composition().voices:
            print("Voice %d: " % counter, end='')
            if voice.range is not None:
                print(voice.range + ", ", end='')
            if voice.name is not None:
                print(voice.name, end='')
            print("")
            counter += 1
              
        print("Partiture: " ,end='')
        if self.partiture is not None:
            if self.partiture == 0 :
                print("no")
            else:
                print("yes")

        if self.composition().incipit is None:
            print("Incipit: ")
        else:
            print("Incipit: " + self.composition().incipit )

    def composition(self):
        return self.edition.composition

class Edition():
    def __init__(self ,composition, authors, name):
        self.composition=composition
        self.authors=authors
        self.name=name

class Composition():
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name=name
        self.incipit=incipit
        self.key=key
        self.genre=genre
        self.year=year
        self.voices=voices
        self.authors=authors

class Voice:
    def __init__(self, name, range):
        self.name=name
        self.range=range

class Person:
    def __init__(self, name, born, died):
        self.name=name
        self.born=born
        self.died=died

def parseComposer(line2):
    line2 = re.sub( "Composer: " , '' , line2 ).strip()
    splitLine = line2.split( ';' )
    composersList = []
    for com in splitLine:
        composerName = com
        composerName = composerName.translate({ord(i):None for i in '0123456789()-/+'}).strip()
        born = None
        died = None

        if re.search("\d{4}", com) is not None : 

            if re.search("\+", com) is not None :
                years = re.search("(\d{4}\.\d+|\d{4})" , com)
                died = int(years.group(1))
            elif re.search("\*", com) is not None : 
                years = re.search("(\d{4}\.\d+|\d{4})" , com)
                born = int(years.group(0)) 
            else :    
                years = re.findall("(\d{4}\.\d+|\d{4})" , com)
           
                if len( years ) == 2 :
                    died = int(years[1])
                
                born = int(years[0])

        composer = Person(composerName, born , died )
        composersList.append(composer)

    return composersList

def parseTitle(line2):
    line2 = re.sub( "Title:" , '' , line2 ).strip()
    if not line2 : line2 = None
    return line2

def parseGenre(line2):
    line2 = re.sub( "Genre:" , '' , line2 ).strip()
    if not line2 : line2 = None
    return line2

def parseKey(line2):
    line2 = re.sub( "Key:" , '' , line2 ).strip()
    if not line2 : line2 = None
    return line2

def parseCompositionYear(line2):
      line2 = re.search( "(\d{4}\.\d+|\d{4})" , line2 )

      if line2 :
        return int( line2.group() )
      else :
        return None

def parseEdition(line2):
    line2 = re.sub( "Edition:" , '' , line2 ).strip()
    if not line2 : line2 = None
    return line2

def parseEditor(line2):
    line2 = re.sub( "Editor:" , '' , line2 ).strip()
    if not line2 : return []
    tmpEditors = line2.split( ',' )
    editors = []
    for name in tmpEditors:
        name = name.strip()
        editors.append(Person(name,None,None))
    
    return editors

def parseVoice(line2):
    voiceName = re.search("(Voice\s)+\d+:", line2)
    line2 = re.sub(voiceName.group(), '', line2)
    rangeX = re.search("\w+--+\w+", line2)

    if rangeX : 
        line2 = re.sub(rangeX.group() + ", ", '', line2).strip()
        return Voice(line2,rangeX.group())
    else:
        return Voice(line2.strip(),None)

def parsePartiture(line2):
    if not line2 : return 0

    if "yes" in line2 :
        return 1
    else:
        return 0

def parseIncipit(line2):
    line2 = re.sub( "Incipit:" , '' , line2 ).strip()
    if not line2 : line2 = None
    return line2

def load(filename):
    prints = []
    file = open(filename,'r')

    for line in file:
        if line == "\n" : continue

        if ( "Print Number:" in line ):
            print_id = int( re.search( "\d+" , line).group(0) )
            voices = []
            title = None
            genre = None
            key = None
            comYear = None
            incipit = None
            composers = None
            partiture = None
            editors = None
            atrEdition = None

            for line2 in file:
                if line2 == "\n" : break

                if ("Composer:" in line2 ) : composers = parseComposer(line2)
                if ("Title:" in line2 ) : title = parseTitle(line2)
                if ("Genre:" in line2 ) : genre = parseGenre(line2)
                if ("Key:" in line2 ) : key = parseKey(line2)
                if ("Composition Year:" in line2 ) : comYear = parseCompositionYear(line2)
                if ("Edition:" in line2 ) : atrEdition = parseEdition(line2)
                if ("Editor:" in line2 ) : editors = parseEditor(line2)
                if ("Voice" in line2 ) : voices.append( parseVoice(line2) )
                if ("Partiture:" in line2 ) : partiture = parsePartiture(line2)
                if ("Incipit:" in line2 ) : incipit = parseIncipit(line2)
                 
            composition = Composition(title,incipit,key,genre,comYear,voices,composers)
            edition = Edition(composition,editors,atrEdition)
            classPrint = Print(edition,print_id,partiture)
            prints.append(classPrint)
    file.close()
    return prints
    
