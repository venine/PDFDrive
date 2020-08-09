#!/usr/bin/python3

import re
import os
from collections import defaultdict


                
def printFunction(obj, keys=None):
    if type(obj) == list:
        if not type(obj[0]) == tuple:
            for i, item in enumerate(obj):
                print(f'{i}> {item}')
            return
        else:
            for i, item in obj:
                print(f'{i}> {item}')
            return
    elif type(obj) == dict:
        assert(keys is not None)
        assert(type(keys) == tuple)
        for i in keys:
            item = obj[i]
            if type(item) == list:
                printFunction(item)
            else:
                print('>', item)
    else:
        return False
            
                
def traverseDirectory(dirName):
    if not os.path.isdir(dirName):
        print(f'{dirname} is not a directory.')
        return False
    if not os.path.exists(dirName):
        print(f'{dirname} does not exist. Make ? (y|n)')
        ch = input('%%%% ')
        if 'y' in ch:
            os.makedirs(dirName)
            return True
        else:
            return False
        

def showHelp(helpString = None, help=None):
    print(helpString)
    
class navigateList:
    '''

    * Use this to navigate a list.
    * This prints a list of items that can be printed.
    * It prints items which can be printed. 
    * The number of items printed are by default 10.
    * Uses methods next() and prev() to go back and forth a list.
    * Uses wrapping by default.
    * You have to set the listObject manually. This is to ensure that the length of the object is updated each time you edit it.

    '''

    def __init__(self):
        self.currentIndex = 0
        self.listObject = None
        self.listObjectLen = None
        self.by = 5
        self._lastcommand = ""
        self.lastrange = (0, 0)

    def setObject(self, listObject, by):
        '''
        Set the listObject. 
        "by" indicates the number of items that should be printed. 
        '''
        assert(type(listObject) == list or type(listObject) == dict)

        if type(listObject) == list:
            self.listObject = listObject
            self.listObjectLen = len(listObject)
            assert(self.listObjectLen > by)
            self.by = by
            self.lastrange = (0, by)
            self.currentIndex = by
        
            

    def goto(self, idx):
        if 0 < idx < self.listObjectLen:
            self.curentIndex = idx
        else:
            return False

    def getListByRange(self, a,b, direction):
        obj = self.listObject
        self.lastrange = (a,b)

        if direction == 'n':
            return [(i, obj[i]) for i in range(a,b)]
        elif direction == 'p':
            return [(i, obj[i]) for i in range(a,b, -1)]
        else:
            return [(i, obj[i]) for i in range(self.lastrange[0], self.lastrange[1])]
        
    def next(self):
        ''' 
        By default print 5 items which are NEXT in the series.
        '''
        
        floor = self.currentIndex 
        ceil = self.listObjectLen - 1
        by = self.by 
        obj = self.listObject
        printList = []

        if floor >= ceil:
            floor = floor - ceil
        elif floor < 0:
            floor = ceil + floor

        
        
        if floor == ceil:
            return self.getListByRange(0, by, 'n')
        if self._lastcommand == 0:
            floor += 2
        self._lastcommand = 1

        dist = (floor + by) - ceil
        if dist == 0:
            self.currentIndex = ceil 
            return self.getListByRange(ceil-by, ceil+1, 'n')
        elif dist < 0:
            self.currentIndex = floor + by 
            return self.getListByRange(floor, floor+by, 'n')
        
        elif dist > 0:
            self.currentIndex = ceil 
            printList = self.getListByRange(floor, ceil+1, 'n')
            printList.extend(self.getListByRange(0, dist-1, 'n'))
            return printList

        
    def prev(self):
        floor = self.currentIndex 
        ceil = self.listObjectLen - 1
        by = self.by
        obj = self.listObject
        
        
        if floor > ceil:
            floor = floor - ceil 
        elif floor < 0:
            floor = ceil + floor 
        elif floor == 0:
            self.currentIndex = ceil - by 
            self._lastcommand = 0
            return self.getListByRange(ceil, ceil - by, 'p')
            

        origFloor = floor
        if self._lastcommand == 1:
            origFloor -= by - 2 

        
        floor = origFloor - by
        
        self._lastcommand = 0
        
        if floor > 0:
            self.currentIndex = floor 
            return self.getListByRange(origFloor, floor, 'p')
            
        elif floor < 0:
            self.currentIndex = ceil + floor + 1
            returnList = self.getListByRange(origFloor, -1, 'p')
            returnList.extend(self.getListByRange(ceil, ceil + floor + 1, 'p'))
            return returnList

    def where(self):
        return self.getListByRange(*self.lastrange, None)


class choice:
    ''' 
    * listObject is a list
    * prompt is the prompt shown while accepting input
    * printFunction needs to be set manually.
    '''

    def __init__(self):
        self.listObject = None
        self.listObjectLen = None
        self.prompt = None
        self.printFunction = printFunction
        self.builtin = {'print': printFunction, 'quit' : lambda : False, 'help': showHelp, 'cd' : traverseDirectory}
        self.regex = f'(?P<BUILTIN>{("|").join([i for i in self.builtin.keys()])})?\s*(?P<PARAM>(?P<INDEX>-?\d+)|(?P<INDEXSTRING>s:(?:-|\+)?\d+)|(?P<STRING>.+))?'
        
        self.regex = re.compile(self.regex)
        
    
    def appendBuiltin(self, add):
        self.builtin[add[0]] = add
        self.regex = f'(?P<BUILTIN>{("|").join(i[0] for i in self.builtin.keys())})?\s*(?P<PARAM>(?P<INDEX>-?\d+)|(?P<INDEXSTRING>s:(?:-|\+)?\d+)|(?P<STRING>.+))?'
        print(self.regex)
            

    def setObject(self, listObject):
        self.listObject = listObject
        self.listObjectLen = len(self.listObject)
        assert(self.listObjectLen > 1)
        

    def setPrompt(self, promptString):
        self.prompt = promptString

    def _checkRegex(self, userInput):
        userInput = userInput.lstrip().rstrip()
        match = self.regex.search(userInput)
        

        if not match:
            return False
        
        ret = defaultdict(lambda :None)
        
        
        if match.group('STRING'):
            ret['searchStr'] = match.group('STRING')
        elif match.group('INDEXSTRING'):
            ret['PARAM'] = match.group('PARAM')
            ret['searchInd'] = match.group('INDEXSTRING').replace('s:','')
        elif match.group('INDEX'):
            ret['idx'] = match.group('INDEX')
            ret['idx'] = int(ret['idx'])
        elif match.group('BUILTIN'):
            ret['command'] = match.group("BUILTIN")
        
        return ret
            
    def _checkCommand(self, cmd, args=None):
        print(cmd)
        if not cmd:
            return False
        cmdFunc = self.builtin[cmd]

        if 'print' in cmd:
            return cmdFunc(self.listObject)
        if cmd == 'quit':
            exit 
        elif args:
            return cmdFunc(*args)
        else:
            return cmdFunc()
    
    def getUserInput(self, recursionObject=False, recursionObjectLen = False):
        obj = self.listObject
        objLen = self.listObjectLen
        if recursionObject:
            print('recursing')
            obj = recursionObject
            objLen = recursionObjectLen
            
        assert(self.printFunction  != False)
        
  
        if not self.prompt:
            self.prompt = "% "

        self.printFunction(obj)
        searchStr = None
        searchInd = None
        command = None
        idx = None
        param = None
        
        while True:
            u = input(self.prompt)
            u = self._checkRegex(u)
            if u == False:
                print('invalid input')
                continue

            if u['searchStr']:
                searchStr = u['searchStr']
            if u['searchInd']:
                searchInd = u['searchInd']
            if u['command']:
                command = u['command']
            if u['idx']:
                idx = u['idx']
            if u['PARAM']:
                param = u['PARM']

            checkIndex = lambda a, l: a < l
            
 

            if idx:
                if idx < 0:
                    print('(negative index.)')
                    continue
                elif idx >= objLen:
                    print('(greater than the max number of list.)')
                    continue
                return obj[idx]
            elif searchInd or searchStr:
                s = None
                if searchInd:
                    s = searchInd.replace('s:','')
                else:
                    s = searchStr

                    
                matches = [i for i in obj if s in str(i)]
                lmatches = len(matches)
                
                if lmatches == 0:
                    print('(search yielded nothing.)')
                    continue
                else:
                    if lmatches == 1:
                        return matches[0]
                    
                    
                    rep = self.getUserInput(recursionObjectLen = lmatches, recursionObject=matches) #should be a single elemenet
                    if rep == False:
                        continue
                    else:
                        return rep

            elif command:
                self._checkCommand(command, param)
                
            else:
                print('(cannot recognize this string)')
                continue

    def getUserInputCustom(self, checkFunction):
        '''
        Use this when you have to force the input to be correct. However, you can exit the prompt anyway by typing 'quit' '''
        while True:
            u = input('%%%% ')
            if 'quit' in u:
                return False

            r = checkFunction(u)
            if r == False:
                print('invalid input')
                continue
            else:
                return r # exits when the user input is valid and also returns the value
    
            
            
            
            
