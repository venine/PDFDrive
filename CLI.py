import filetype
import sys
import shutil
from cmd import Cmd
import readline
from exceptions import *
from downloadLink import downloadLink
import subprocess
import re
import os
import pandas as pd
import requests
from printer import printer
from CLIUtils import *

printer = printer()
choice = choice()

def isSessionActive(func):
    def MOD(*args, **kwargs):
        if not args[0].dl:
            printer.ALERT('You need to start a session first.')
            return 
        return func(*args, **kwargs)
    return MOD



class CLI(Cmd):
    prompt = '% '

    def __init__(self, dirname=os.environ['HOME']):
        Cmd.__init__(self)

        # stores all the previous sessions. 
        self.dlHistory = []
        self.markedL = 0

        #current session
        self.sessionNumber = 0
        self.currentSession = ""
        self.dl = None
        self.df = None
        self.line = ""
        self.showIndex = 0
        self.dirname = dirname
        self.originalDirectory = dirname
        self.changeDirectoryPrompt(self.dirname)
        self.navigateList = navigateList()

    def emptyline(self):
        if not self.dl:
            printer.alert('(cmd ?)')
        else:
            self.NAVIGATION(direction = None, steps = 5)


    def help_ls(self, line=None):
        print(''' show all the files in the current directory''')

    def help_c(self, line=None):
        print(        '''
        Change to another session.
        Each session is defined by a search query. Therefore, you will be given a small menu to choose the apt session.
        ''')

    def help_cd(self, line=None):
        print('''
        Your standard cd.

        Note that each session will have its separate download directory. However, if you wish to proceed with a default one for all, provide a commandline parameter while executing the script.

        ''')

    def help_n(self, line=None):
        print('''Traverse the list by INT amount. The default value is 5.''')

    def help_p(self, line=None):
        print('''Traverse the list background by INT amount. The default value is 5''')

    def help_l(self, line=None):
        print(        '''
        Load the next 20 results. 

        Why not load several pages at once ?
        > You will mostly find your desired file in the first set of results. Trust me.
        ''')

    def help_m(self, line=None):
        print(        '''
        mark desired PDF by index
        
        for eg.
        m 1,2,3,4
        m 0
  
        additional commands:
        m this : show all the marked files of THIS session (search query)
        m all  : show all the marked files of ALL the sessions (all search queries)

        misc:
        After a 'd' has been run, the list of files will be updated.
        All the marked files which were found will not be downloaded again.
        All the files that were not found will not be downloaded on the second run.

        This is done so because getting the download link for each file is an extremely expensive process.
        It is very time-consuming. Therefore, you should be cautious and run this command when you are definitely done surfing.

        ''')

    def help_u(self, line=None):
        print(        ''' 
        unmark desired PDF by index
        
        for eg.
        u 1,2,3,4
        u 0

        ''')

    def help_d(self, line=None):
        print(        '''
        Serially download all the marked files of all the sessions.
        Please note that this is the non multithreaded version. Therefore, run this at the very end.

        ''')
        
    @isSessionActive
    def do_ls(self,line):
        ''' show all the files in the current directory'''
        for idx, f in enumerate(os.listdir()):
            if os.path.isdir(f):
                printer.notice(f'{idx}> <d> {f}/')
            elif os.path.isfile(f):
                printer.notice(f'{idx}> <f> {f}')
            else:
                printer.notice(f'{idx}> <unknown> {f}')
        

    @isSessionActive
    def changeDirectoryPrompt(self,dirname=None, noupdate=False):
        ''' change the directory and update the prompt. '''
        d = ""
        if dirname:
            d = dirname
        else:
            d = self.dl.currentPDF[3]

        if not noupdate:
            d = os.path.abspath(d)
            self.dl.currentPDFDownloadDirectory = d
            self.dl.currentPDF[3] = d
            os.chdir(d)
        
        d = d.replace(os.environ['HOME'],'~')
        CLI.prompt = f'<{self.currentSession}>\n<{d}>> '
        return 
        
    @isSessionActive
    def do_cd(self, directory):
        '''
        Your standard cd.

        Note that each session will have its separate download directory. However, if you wish to proceed with a default one for all, 
        provide a commandline parameter while executing the script.

        '''

        if not self.currentSession:
            printer.ALERT('(start a session)')
            return
        
        if directory:
            orig = directory
            self.originalDirectory = os.getcwd()
            if '~' in directory :
                directory = directory.replace('~', os.environ['HOME'])
            if os.path.exists(directory):
                self.changeDirectoryPrompt(directory)
                                
            elif not os.path.exists(directory):
                printer.ALERT(f'(directory {directory} does not exist. Create ? (NO for no))')
                e = 0
                while e != 1:
                    ch = input('%%%% ')
                    if not ch:
                        print.alert('(no arg provided)')
                    elif re.match('^ls|\sls\s|^ls$',ch):
                        self.do_ls(line)
                    elif re.match('^..\s|^../$|^../\s', ch):
                        curdir = os.getcwd().split('/')
                        curdir.pop()
                        os.chdir(('/').join(curdir))
                        continue
                        
                    else:
                        if 'NO'  in ch:
                            printer.comment('(not creating a directory. Cannot change directory)')
                            e = 1
                            break
                        else:
                            try:
                                os.makedirs(directory)
                                self.changeDirectoryPrompt(directory)
                                e = 1
                                break
                            except Exception as e:
                                printer.ALERT('(could not make directory. Not changing from the current directory)')
                                raise e
                

        else:
            printer.alert('(path ?)')

        return 

    
    def do_s(self,line=None):
        '''
        Start from scratch.
        Provide a search query.
        
        '''
        # starting from scratch.
        self.line = line
        if not line:
            printer.alert('(no arg supplied)')
            return
        else:
            try:
                if not self.dl:
                    self.dl = downloadLink(line)
                    
                self.currentSession = line
                self.dl.search(line)
                self.dl.getSearchQueryResults()
                self.dl.currentPDFDownloadDirectory = os.path.abspath(self.dirname)
                self.dl.currentPDF[3] = os.path.abspath(self.dirname)
                self.changeDirectoryPrompt(self.dirname)
                self.navigateList.setObject(self.dl.currentPDF[0]['year'], 5)
                
                                                                
            except InvalidSearchQuery:
                self.currentSession = None
                printer.ALERT('(invalid search query)')
                

    
    @isSessionActive
    def do_m(self,line=None):
        '''
        mark desired PDF by index
        
        for eg.
        m 1,2,3,4
        m 0
  
        additional commands:
        m this : show all the marked files of THIS session (search query)
        m all  : show all the marked files of ALL the sessions (all search queries)

        misc:
        After a 'd' has been run, the list of files will be updated.
        All the marked files which were found will not be downloaded again.
        All the files that were not found will not be downloaded on the second run.

        This is done so because getting the download link for each file is an extremely expensive process.
        It is very time-consuming. Therefore, you should be cautious and run this command when you are definitely done surfing.

        '''
        
        if not self.currentSession:
            printer.ALERT('(the search has not been performed yet)')
            return 
        if not line:
            printer.alert('(no input provided)')
            return
        if re.search('\d+[^,0-9]+\d+',line):
            printer.comment('(more than one indices are passed but are not comma separated)')
            return
        

        marked = self.dl.currentPDF[2]
        line = line.replace(' ','').split(',')
        line = list(filter(lambda x: len(x) > 0, line))
        printer.notice(f'(prev: {marked})')


        for i in line:
            idx = i
            try:
                idx = int(i)

                if (idx < 0 or idx >= self.dl.currentPDFlen):
                    printer.comment(f'(0 < {idx} <= {self.dl.currentPDFlen}) ?')
                elif idx in marked:
                    printer.comment(f'({idx} is already marked)')
                else:
                    marked.append(idx)
                    if not self.dl.currentPDF[0]['marked'][idx] == 'Downloaded':
                        self.dl.currentPDF[0]['marked'][idx] = True
                        self.markedL += 1
                    elif self.dl.currentPDF[0]['marked'][idx] == 'Cannot Download':
                        printer.comment(f'({idx}: cannot be downloaded. The file is not available.)')
                                            

            except ValueError:
                if 'this' in idx:
                    printer.notice(f'[{self.currentSession}]')
                    for i in self.dl.currentPDF[2]:
                        printer.notice(f'{i}> ' + self.dl.currentPDF[0]['name'][i])

                elif 'all' in idx:
                    for i in self.dl.PDF.keys():
                        printer.notice(f'[{i}]')
                        for j in self.dl.PDF[i][2]:
                            printer.notice(f'{j}> ' + self.dl.PDF[i][0]['name'][j])
                        print()

                else:
                    printer.comment(f'({i} is not an integer, hence not marking)')
            
        printer.notice(f'(now: {marked})')
        

        
    @isSessionActive
    def do_u(self,line=None):
        ''' 
        unmark desired PDF by index
        
        for eg.
        u 1,2,3,4
        u 0

        '''
        if line == None:
            printer.alert('(no arg provided.)')
            return

        if not self.currentSession:
            printer.ALERT('(start a session by the command "s")')
            return 
        if re.search('\d+[^,]+\d+',line):
            printer.comment('(The parameters should be comma separated)')
            return 
        else:
            marked = self.dl.currentPDF[2]
            line = line.replace(' ','').split(',')
            line = list(filter(lambda x: len(x) > 0, line))
            popped = []
            printer.notice(f'(marked: {marked})')
            
            for i in line:
                idx = None
                try:
                    idx = int(i)
                    if (idx < 0 or idx >= self.dl.currentPDFlen):
                        printer.comment(f'(0 < {idx} <= {self.dl.currentPDFlen}) ?')
                    elif idx in popped:
                        printer.comment(f'({idx} is already unmarked)')

                    elif idx not in marked:
                        printer.comment(f'({idx} has not been marked)')
                    else:
                        printer.comment(f'(dropped: {self.dl.currentPDF[0]["name"][idx]})')
                        if not self.dl.currentPDF[0]['marked'][idx] == 'Downloaded.':
                            self.dl.currentPDF[0]['marked'][idx] = False
                        marked.pop(marked.index(idx))
                        
                except ValueError:
                    printer.comment(f'({i} is not an integer, hence not unmarking)')
                    
            printer.notice(f'(now marked: {marked})')


        

    @isSessionActive
    def do_d(self,line=None):
        '''
        Serially download all the marked files of all the sessions.
        Please note that this is the non multithreaded version. Therefore, run this at the very end.

        '''
        if not self.currentSession:
            printer.ALERT('(you need to search first)')
            return
        
        allSessionNames = self.dl.PDF.keys()

        for name in allSessionNames:
            session = self.dl.PDF[name]
            marked = session[2]
            PDF = session[0]
            downloadDirectory = session[3]
            
            os.chdir(downloadDirectory)
            self.currentSession = name
            
            if len(marked) < 0:
                printer.comment('(nothing has been marked yet.)')
                return
            else:
                ret = self.dl.downloadByIndex(marked)
                for i in marked:
                    dl = PDF['downloadLink'][i]
                    
                    if not dl:
                        PDF['marked'][i] = 'Cannot Download'
                        continue
                    
                    fn = PDF['name'][i]
                    r = requests.get(dl, headers={'Referer':'www.pdfdrive.com', 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0)'})
                    
                    with open(fn,'wb') as F:
                        F.write(r.content)
                        printer.GOOD(f'(file written: {fn})')
                        t = filetype.guess(fn)
                        if 'pdf' in t.mime:
                            shutil.move(fn, f"{fn}.pdf")
                        elif 'epub' in t.mime:
                            shutil.move(fn,f"{fn}.epub")
                        elif 'mobi' in t.mime:
                            shutil.move(fn,f'{fn}.mobi')
                        else:
                            printer.alert('unknown filetype.')
                    PDF['marked'][i] = 'Downloaded'
                    
            session[2] = []
                        
                    
    
    def do_q(self,line=None):
        ''' Shut the program down.'''
        os.chdir(self.originalDirectory)
        if self.dl:
            del self.dl 
        return True

    

 
    @isSessionActive
    def do_c(self, line):
        '''
        Change to another session.
        Each session is defined by a search query. Therefore, you will be given a small menu to choose the apt session.
        '''
        printer.notice('Changing session.')
        sessions = list(self.dl.PDF.keys())
        
        if len(sessions) > 1:
            choice.setObject(sessions)
        else:
            printer.alert('this is the only session.')
            return
        
        ch = choice.getUserInput()
        self.currentSession = ch
        self.changeDirectoryPrompt(noupdate=False)
        self.dl.currentPDF = self.dl.PDF[self.currentSession]
        return 
        
        
    @isSessionActive
    def do_n(self, steps=5): #By default, show 10 of the results found.
        '''
        Traverse the list by INT amount. The default value is 5.
        '''
        if steps:
            steps = int(steps)
        if steps == '':
            steps = 5
        elif steps > 20:
            printer.comment('(cannot display >= 20 results)')
            return
        elif steps < 1:
            printer.comment('(huh?)')
            return
        
        self.NAVIGATION('n', steps)
        

    @isSessionActive
    def do_p(self, steps=5):
        '''
        Traverse the list background by INT amount. The default value is 5
        '''
        if steps == '':
            steps = 5
        elif steps > 20:
            printer.comment('(cannot display >= 20 results)')
            return
        elif steps < 1:
            printer.comment('(huh?)')
            return

        self.NAVIGATION('p', steps)
        
        
    @isSessionActive
    def do_l(self, load=1):
        '''
        Load the next 20 results. 

        Why not load several pages at once ?
        > You will mostly find your desired file in the first set of results. Trust me.
        '''
        if not self.currentSession:
            printer.DEGRADED('(start a new session)')
            return
        else:
            self.dl.nextPage()
            self.navigateList.setObject(self.dl.currentPDF[0]['year'], 5)
            return
        

    @isSessionActive
    def PRINTFIELD(self, userange):
        PDF = self.dl.currentPDF[0]
        columns = shutil.get_terminal_size().columns
        
        for i in userange:
            print()
            printer.notice(f'<<{i}>>')
            print()
            for k in self.dl.KEYS:
                key = k
                left = 10 - len(k)
                k = k + " " * left + '| '
                print(f'{k}', end="")
                printer.notice(f'{PDF[key][i]}')
                
            print()
            printer.notice(f'<<{i}>>')
            printer.DEGRADED("_" * columns)
            
        
    @isSessionActive
    def NAVIGATION(self, direction=None, steps=5):

        steps = int(steps)
        self.navigateList.by = steps
        if not 1 <= steps and steps < self.navigateList.listObjectLen:
            printer.comment('does not fall in range')
            return
        else:
            self.navigateList.by = steps

        if direction == 'n':
            printList = self.navigateList.next()

        elif direction  == 'p':
            printList = self.navigateList.prev()

        elif direction == None:
            printList = self.navigateList.where()


        self.PRINTFIELD([i[0] for i in printList])

        
C = None
if len(sys.argv) > 1:
    if not os.path.exists(sys.argv[1]):
        printer.ALERT(f"{sys.argv[1]} non-existent directory.")
        sys.exit(1)
    C = CLI(sys.argv[1])
else:
    C = CLI(os.environ['HOME'])
    
C.cmdloop()

                        
                            
