# A Python script to download files from PDFDrive.

This is a very basic script made in python to traverse PDFDrive and download files off it without the hassle of waiting for the infamous 20 seconds that a user is forced to bear to download a single file. 

For anyone who would like to fork this project and make their own implementations, you are free to do so. To contact, use this email: kpamkar@gmail.com

## Usage
To run: `% python CLI.py [OPTIONAL DEFAULT DIRECTORY]`

## First run caveats
On your first run, do the following things:
1. Change `self.headless = True` to `self.headless = False` inside downloadLink.py
2. Run `firstrun.py`
3. Install uBlock Origin addon.
4. Change `self.headless = False` to `self.headless = True`
5. Start using CLI.py.

## Caveats
* 0 based indicing. 
* Fetching another 20 results needs to be done manually. This is deliberately done so that the program does not take too long to initiate and secondly, you will, in 99% of the cases, obtain your desired file in the first set of 20 results. I found it useless to download 400 results (on an average) by default. 
* No multithreading (yet) support. Unfortunately the program is a RAM and a CPU hog already due to its virtue of using selenium. 
* May crash. Don't worry much though. It will not in most cases.
* Strictly CLI. 
* You may need to manually change the waiting time based on your internet. However, according to my research, it is a mandatory 17 seconds waiting period which is independent of the speed of the connection. In some cases, it exceeds 17 seconds and in those cases, it is usually the case that the underlying file is missing. But to be on the safer side, the program waits for 20 seconds instead of 17. The edits can be made in downloadLink.py
* downloadLink.py can be used as an API independently. But it has bad naming convention. I will fix it soon.
* There is a bonus CLIUtils.py which can be used for any kind of CLI implementations. 
* Downloading is slow. This is not related to your internet but the constant waiting for 20 seconds. Moreover, selenium is being used, therefore, the program is bound to not be very responsive when it is searching for download links. However, since the downloading is handled by requests, you need to worry. 
* Still under development. This implementations may not be stable. 

## Features
* Can initiate multiple sessions. Each session is defined by the initial search query that is put in. 
* Ability to set different directories for the downloads for each session.
* Basic abilities such as marking, unmarking indices, ls(), cd().
* Colored output. 

## Requirements
1. selenium (Please install the geckodriver as well)
2. termcolor
3. filetype
4. lxml

## Commandline commands
* ls : Display files in the current directory
* cd : Change directory
* m  : Mark indices. eg. m 1,2,3,4 or m 0. `m this` will show all the marked files in *that* session and `m all` will show all the marked files of *all* the sessions.
* u  : Unmark indices
* q  : Quit.
* s  : Start a session using a search query.
* c  : Change session
* l  : Load the next set of results
* d  : Download all marked files 
* n [INT] : Display the next INT number of results. By default, this is set to 5
* p [INT] :             previous
* <ENTER> : (no input) Display the number of results that were displayed previously without going backwards and forwards. 
  
  
## Upcoming features
1. Multithreading. This means simultaneous downloading from all the sessions. The current implementations processes all the links serially. 
2. Proper naming convention. 
3. Documentation for CLIUtils.py



