# Programs for custom generation of tests when using standards grading
# Tom LoFaro, Gustavus Adolphus College
# April 2019

# Summary of programs
# 1.  readStudents, Done:  Reads students standards scores from a file
#     downloaded from Moodle (see mcs-121-stds.csv) and returns a dictionary
#     with keys student name and values a list of standards needed.
#
#     Notes and issues:
#       a. This assumes a csv file of the format that Moodle creates when
#       grades are downloaded from Moodle.  The slicing of the data depends
#       on this particular structure.
#
# 2.  readTest, Done: Reads a LaTeX (like) file of test problems labeled with
#     standards and returns a dictionary with keys problem statement
#     (in LaTeX) and values lists of all standards covered.
#
#     Notes and issues:
#       a. Assumes the use of a custom LaTeX command
#       '\standarditem{standards}{problem text}'
#       The definition of this command is written to the output .tex file
#       in the writePreamble function.
#       b. Assumes that the information on each problem is contained on a single
#       line. (WORKING ON THIS ISSUE)
#       c. No LaTeX information other than the problems should be contained in
#       this file.
#
# 3.  assembleTest, Done: Takes in the dictionaries created above and writes a
#     LaTeX file with a custom generated test for each student.
#
#     Notes and issues:
#       a. This is currently NOT SUITABLE FOR TWO-SIDED PRINTING.  It is possible
#       that the first page of one student's test could be the back side of the
#       previous test.  Fixing this requires adjusting the LaTeX written by this
#       program so that at the end of a student test either a single \newpage
#       is executed (if the current page number is even) or a double \newpage
#       (if the current page number is odd).
#
# 4.  subsetOf, Done: used to determine whether the standards of a problem
#     have already been met by a student.
#
# 5.  standardsCompleted, Done: creates a list of standards completed by a given
#     student.
#
#     Notes and issues:
#       a. Assumes that the student must successfully complete a standard
#       exactly twice.
#       b. Assumes the standards are listed in order.
#       c. Think about how to make this customizable.  Maybe reading from
#       same file used in readTest.
#       d.  It is dependent on the format that the grade is saved in. (FIXED)
#
# 6.  WritePreamble, Done: Writes all of the preamble material into the LaTeX
#    output.
#
# 7.  WriteTitle, Done: creates the title, directions, etc. for each student.
#    Also writes the student name and id.
############################################################################

# list, list -> Boolean
def subsetOf(list1,list2):
    # returns True if list1 is a subset of list2
    for item in list1:
        if item not in list2:
            return False
    return True

############################################################################

# string (filename) -> dictionary with keys strings and values lists of strings
def readStudents(studentFile):
    # read the file
    gradeFile = open(studentFile)
    gradeData = gradeFile.readlines()
    gradeFile.close()

    # reformat the data into a usable structure
    gradeData = [aline.split(',') for aline in gradeData]
    gradeData = gradeData[1:] #strip off header line

    gradeDict = {}
    for studentInfo in gradeData:
        # the key is first, last: id
        studentName = studentInfo[0] + ' ' + studentInfo[1] + ': ' + studentInfo[2]
        # the value is a list of strings
        # not getting the last column because Moodle writes a datestring there
        standardsListTemp = studentInfo[6:-1]  # list of strings (either grade or '-')
        # make standardsList a list of ints
        standardsList = []
        for grade in standardsListTemp:
            if grade.strip() == '-':
                standardsList.append(0)
            else:
                standardsList.append(int(float(grade)))
        gradeDict[studentName] = standardsList
    return gradeDict

# string -> list of ints
# gets the student from the studentDictionary and returns a list of standards completed
def standardsCompleted(studentDict, student):
    scores = studentDict[student]
    completedList = []
    for i in range(len(scores)):
        if scores[i] == 2:
            completedList.append(i+1)
    return completedList
        
############################################################################

# string (filename) -> dictionary with keys problem text and values list of ints
def readTest(testFile):
    # read the file
    problemFile = open(testFile)

    problemDict = {}
    # assumes the first line of the file is a \standarditem
    problemTeX = problemFile.readline()
    sIndex1 = problemTeX.find('{') + 1
    sIndex2 = problemTeX.find('}')
    standards = problemTeX[sIndex1:sIndex2]
    standards = standards.split(',')
    standards = [int(item) for item in standards]

    for aline in problemFile:
        if aline[:13] == '\\standarditem':
            problemDict[problemTeX] = standards  # put previous prob in dict.
            problemTeX = aline                   # start new problem
            sIndex1 = problemTeX.find('{') + 1
            sIndex2 = problemTeX.find('}')
            standards = problemTeX[sIndex1:sIndex2]
            standards = standards.split(',')
            standards = [int(item) for item in standards]
        else:
            problemTeX = problemTeX + aline
    problemDict[problemTeX] = standards
    problemFile.close()
    return(problemDict)

############################################################################
# Functions for writing various necessary LaTeX pieces

# file object -> writefile
def writePreamble(TeXFile):
    # write preamble material
    TeXFile.write('\\documentclass{exam} \n')
    TeXFile.write('\\usepackage{amsmath,amssymb,amsthm,graphicx}\n')
    TeXFile.write('\\newcommand{\\standarditem}[2]{\\item {\\bf Objectives} #1: #2}\n')
    TeXFile.write('\\begin{document}\n') #\\pagestyle{empty}\n

# file object,str -> writefile
def writeTitle(TeXFile,name):
    # write title (maybe input in future)
    TeXFile.write('\\begin{center}\n{\\Large\\bf Math 121 - Standards Assessment 6}\n\\end{center}\n\n \\medskip\n\n')
    # write honor code
    TeXFile.write('\\fbox{\\parbox{6in}{\n\\vspace{10pt}\n')
    TeXFile.write('{\\bf Honor Pledge:} On my honor, I pledge that I have not given, received, or tolerated others use of unauthorized aid in completing this work.\n\n')
    TeXFile.write('\\smallskip \n\n Signature \\hrulefill\n\n\\smallskip\n')
    TeXFile.write('\\bigskip\n\n')
    TeXFile.write('{\\bf Name: ' + name + '}\n\n\\vspace{10pt}}}\n\n')
    # write directions
    TeXFile.write('\\noindent{\\bf Directions:} For any problem you skip, place a line through the problem number and the objective number next to it. For any problem you want graded, circle the problem number and the objective number next to it.\n')
    TeXFile.write('\n\\noindent The objective of this assessment is for you to demonstrate that you have mastered learning objectives.  A correct answer with no work shown does not demonstrate mastery!\n')

############################################################################

def assembleTest(studentFile, questionFile, outputFile):
    # make dictionary of students -> list standards scores
    studentDict = readStudents(studentFile)
    studentRoster = list(studentDict.keys())
    # make a dictionary of standard num -> list of exam problems
    standardDict = readTest(questionFile)
    problemList = list(standardDict.keys())

    # open the output file and write the preamble to it
    examFile = open(outputFile,'w')
    writePreamble(examFile)

    for student in studentRoster:
        dontIncludeList = standardsCompleted(studentDict,student)
        # write title etc
        writeTitle(examFile, student)
        # start list of problems
        examFile.write('\\begin{enumerate}\n')

        for problem in problemList:
            if not subsetOf(standardDict[problem],dontIncludeList):
                examFile.write(problem + '\n')

        examFile.write('\n \\end{enumerate}\n')
        examFile.write('\n \\cleardoublepage\n\n') #two-sided printing I think
 #       examFile.write('\n \\newpage\n')

    examFile.write('\n\n \\end{document}')
    examFile.close()

        
 # implementation
 # assembleTest('grades-input.csv','test-input.tex','test-output.tex')
 
    
    
