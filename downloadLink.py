import sys
import time
import re
import threading
import requests
import subprocess
import os
import threading

from collections import defaultdict
from printer import printer

from exceptions import *
from lxml import etree

from selenium.webdriver.common.alert import Alert
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import FirefoxOptions, FirefoxProfile
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC

from dataclasses import dataclass 
printer = printer()

class downloadLink:
    def __init__(self, search):
        self.rootLink = 'https://www.pdfdrive.com'
        
        # concoct the search url
        self.link = 'https://www.pdfdrive.com/search?q={}'.format(('+').join(search.split()))
        self.currentSession = None
        self.currentPDF = None
        self.currentPDFDownloadDirectory = None
        self.currentPDFlen = 0
        self.currentSessionInvalid = True
        self.KEYS = ('hits', 'name', 'url', 'pages', 'size', 'year', 'marked')
        self.PDF = {}

        # load Firefox
        self.driverOptions = FirefoxOptions()
        self.driverProfile = FirefoxProfile()
        
        self.addonPath = f'{os.environ["HOME"]}/.mozilla/firefox/qdoeuau8.default-release/extensions/uBlock0@raymondhill.net.xpi'


 # set headless or otherwise.
        self.driverOptions.headless = True
        
        self.driver = False # Firefox(options=self.driverOptions, firefox_profile=self.driverProfile)
        
        
    # This is a helper function for checkForAlertDialogue. 
    def bypassDialog(self,usepath = None, usemethod = None, isAlternate=False):
        driver = self.driver
        try:
            dialogBackground = driver.find_element_by_css_selector('div#pdfdriveAlerts')
            dialogBackground.click()

            try: 
                element = usemethod(usepath)
                return True
            except NoSuchElementException:
                return (True,'alt')

        except UnexpectedAlertPresentException:
            Alert(driver).dismiss()
            return True

        except (InvalidSelectorException,ElementNotInteractableException):

            # both of the selectors do not yield any result. 
            if isAlternate: 
                return False
            else:
                return (True,'alt')

        except Exception as e:
            raise e

    # There is some modification required for this function. 
    def checkForAlertDialog(
            self,
            path=False,
            alternatePath = False,
            useAlternatePath = False,
            alternatePathCss = False,
            alternatePathXpath = False,
            css=False,
            xpath=False,
            several=False,
            idx=0):

        driver = self.driver
        usepath = path
        usecss = css
        usexpath = xpath

        if idx == 3:
            return False
        
        if useAlternatePath:
            usepath = alternatePath
            usecss = alternatePathCss
            usexpath = alternatePathXpath


        el = None

        if usepath:
            if several:
                if usecss:
                    el = driver.find_elements_by_css_selector
                elif usexpath:
                    el = driver.find_elements_by_xpath
            else:
                if usecss:
                    el = driver.find_element_by_css_selector
                elif usexpath:
                    el = driver.find_element_by_xpath

            if not (usexpath or usecss):
                raise Exception("find method has not been defined.")


        else:
            el = driver.find_element_by_css_selector
            usepath = 'input#q'

        try:
            element = None
            element = el(usepath)
            
            return element

        except (ElementNotVisibleException , ElementNotSelectableException , ElementNotInteractableException , NoSuchElementException , StaleElementReferenceException):

            ret = self.bypassDialog( usepath=path, usemethod = el, isAlternate = useAlternatePath)

            if type(ret) == tuple and ret[1] == 'alt':
                # There is no alternatePath defined. All avenues have been exhausted. This is likely a bad selector.
                if not alternatePath:
                    return False
                else:
                    return self.checkForAlertDialog(
                        alternatePath = alternatePath,
                        alternatePathCss = alternatePathCss,
                        alternatePathXpath = alternatePathXpath,
                        useAlternatePath=True,
                        idx=idx+1)

            elif ret:
                return element


        except UnexpectedAlertPresentException:
            Alert(driver).dismiss()
            
            return self.checkForAlertDialog(
                alternatePath = alternatePath,
                path = path,
                css = css,
                xpath = xpath,
                useAlternatePath = useAlternatePath,
                alternatePathXpath = alternatePathXpath,
                alternatePathCss = alternatePathCss,
                idx = idx + 1)


        except Exception as e:
            raise e


        
    # requires an iterator. 
    def goToLink(self,elementIterator,index):
        if not len(elementIterator) == 0:
            self.driver.getelementIterator[index].get_attribute('href')
            return elementIterator[index].get_attribute
        else:
            return False


    # More preferrable than the above one and hence overriding.
    def getSearchQueryResults(self):
        '''
        Makes a dataframe out of the HTML parsed.
        The arg: currentSessionName is important as it helps in indexing the PDF DataFrame accordingly
        '''
        maxPages = None
        maxPagesL = 0

        appendPDF = self.getDataFrame()[0]
        
        
        if self.currentSessionInvalid:
            return InvalidSearchQuery
        else:
            root = self.searchResultsHTML
            thumbnailBoth = root.cssselect('img.img-zoom.file-img')
            page = int(next(root.cssselect('div.Zebra_Pagination ul li a.current')[0].itertext()))
            
            if len(self.currentPDF[1]) == 0:
               self.currentPDF[1] = root.cssselect('div.Zebra_Pagination ul li a[rel*=nofollow]')
               self.currentPDF[1] = [next(i.itertext()) for i in self.currentPDF[1]]
               self.currentPDF[1].pop(0)
               self.currentPDF[1].pop() 
               self.currentPDF[1] = [int(i) for i in self.currentPDF[1]]
               if len(self.currentPDF[1]) > 0:
                   maxPagesL = max(self.currentPDF[1])


               if maxPagesL > 1:
                   self.currentPDF[1] = list(range(maxPagesL,0,-1))
                   self.currentPDF[1].pop()
               else:
                   self.currentPDF[1] = [2]

                    
                    
            printer.notice('(results found: {})'.format(len(thumbnailBoth)))
            t = thumbnailBoth[0]
            
            for idx,i in enumerate(thumbnailBoth):
                appendPDF['thumbnailSmall'][idx] = t.get('src')
                appendPDF['thumbnailBig'][idx] = i.get('original')
                appendPDF['name'][idx] =  i.get('title')
                appendPDF['url'][idx] =  self.rootLink + i.getparent().get('href') 
            
            
            for idx, i in enumerate(thumbnailBoth):
                span = i.getparent().getparent().getnext().getchildren()[1].getchildren()
                notnone = []
                for detail in span:
                    t = detail.text
                    
                    if t != None:
                        if 'Download' in t:
                            appendPDF['hits'][idx] = t
                            
                        elif 'Page' in t:
                            appendPDF['pages'][idx] = t

                        elif 'B' in t:
                            appendPDF['size'][idx] = t
                            
                        elif re.search('\d{4}',t):
                            appendPDF['year'][idx] = t
                            
                            
                                                            
                
            for i in appendPDF.keys():
                p = appendPDF[i]
                p = list(filter(lambda x: x is not None, p))
                self.currentPDF[0][i] = list(filter(lambda x: x is not None, self.currentPDF[0][i]))
                self.currentPDF[0][i].extend(p)
                
                
            self.currentPDFlen = len(self.currentPDF[0]['year'])
            return True
        
                        
    # check verity - can download ? # here refers to the element number from PDF DataFrame
    def canDownloadCheck(self,idx):
        # load the page

        downloadLink = None
        
        if not self.driver:
            self.driver = Firefox(options=self.driverOptions, firefox_profile=self.driverProfile)
            self.driver.install_addon(self.addonPath)
            
        
        try:
            self.driver.get(self.currentPDF[0]['url'][idx])
        except WebDriverException:
            downloadLink = False
            printer.ALERT("(could not load link: '{self.currentPDF[0]['url'][idx]}')")
            return False

        
        # check if the book is present or nort.
        found = self.checkForAlertDialog('span#download-button a[title*=Sorry]',css=True)
        if found:
            printer.ALERT(f'(book has been removed for copyright infringement:{self.currentPDF[0]["name"][idx]})')
            downloadLink = False
            return False
            
        else:
            downloadLink= True
            
            
        downloadElement = self.checkForAlertDialog('a#download-button-link',css=True)
        
        downloadElement.click()

        
        try:
            time.sleep(20)

            downloadLink = self.checkForAlertDialog(path='//a[@class="btn btn-success btn-responsive"]',alternatePath='//a[@class="btn btn-primary btn-user"]',xpath = True, alternatePathXpath = True)

            if not downloadLink:
                downloadLink = False
            else:
                downloadLink = downloadLink.get_attribute('href')
                
            self.currentPDF[0]['downloadLink'][idx] = downloadLink
            printer.notice(f'(found: {self.currentPDF[0]["name"][idx]})')
            return True
            
            
        except TimeoutException as e:
            printer.ALERT(f'(timed out: {self.currentPDF[0]["name"][idx]})')
            downloadLink = False
            self.currentPDF[0]['downloadLink'][idx] = downloadLink
            return False

        
        
    
    # check all the links for their downloadability 
    def downloadByIndex(self, specific):
        for i in specific:
            if i >= self.currentPDFlen or i < 0:
                    printer.comment('idx {} is invalid'.format(i))
                    printer.comment('shall be skipped.')
            else:
                    url = self.canDownloadCheck(i)
                    if not url:
                        printer.ALERT(f"could not find the download link: '{self.currentPDF[0]['name'][i]}'")
        
        return True
                        
        
    def __del__(self):
        if self.driver:
            self.driver.quit()
        else:
            printer.OK('Bye !')
            sys.exit(0)
        return True

    def get(self):
        return self.PDF

    def getDataFrame(self):
        ''' 
        Return a DataFrame and another blank list which is supposed to indicate the page number.
        fmt = [ df, [1,2,3,4], [3,4,3]] [1] = page numbers left; [2] = marked for downloaded
        '''

        d = defaultdict(lambda : [None for i in range(20)])
        return [d, [], [], ""]

        

    def search(self, search, pageNumber=None):
        ''' 
        downloads the HTML page and then searches for the provided query.
        '''
        
        self.link = 'https://www.pdfdrive.com/search?q={}'.format(('+').join(search.split()))

        if not pageNumber == None:
            self.link += f'&page={pageNumber}'

        self.searchResultsHTML = requests.get(self.link)
        self.searchResultsHTML = etree.HTML(self.searchResultsHTML.text)

        root = self.searchResultsHTML
        thumbnailBoth = root.cssselect('img.img-zoom.file-img')
        thumbnailBothL = len(thumbnailBoth)
        
        if thumbnailBothL == 0:
            self.currentSessionInvalid = True
            raise InvalidSearchQuery
        
        else:
            self.currentSession = search
            self.currentSessionInvalid = False

            try:
                self.PDF[self.currentSession]
            except KeyError:
                self.PDF[self.currentSession] = self.getDataFrame()
                self.currentPDF = self.PDF[self.currentSession]
                
                
            
        return True
        
    def nextPage(self):
        l = len(self.currentPDF[1])
        
        if l == 0:
            printer.comment('(This is the only page. Cannot load the next non-existent page)')
        elif l == 1:
            printer.comment('(loading the next page. But this is the last page.)')
            try:
                self.search(self.currentSession, pageNumber=self.currentPDF[1].pop())
            except InvalidSearchQuery:
                printer.ALERT('(cannot load any more pages.)')
                return
            
            self.getSearchQueryResults()
            
        elif l > 1:
            l = l-1
            printer.comment(f'(loading the next page. {l} pages left.)')
            send = self.currentPDF[1].pop()
            self.search(self.currentSession, pageNumber=send)
            self.getSearchQueryResults()
            return 
            
            
    def setCurrentPDF(self, sessionname):
        self.currentSession = sessionname
        self.currentPDF = self.PDF[self.currentSession]
        return
    
        
