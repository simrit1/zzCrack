#######################################
#             zzCrack                  
#         made by robi0t              
#    https://github.com/robi0t        
#                                     
#             LICENSE:
#           MIT License
#######################################
#If you experience any error please let me know
#version 2.2

from colorama import Fore,Back,Style,init
from itertools import chain,product
from optparse import OptionParser
from zipfile import ZipFile
import string
import signal
import time
import sys
import os

banner='''
▒███████▒▒███████▒ ▄████▄   ██▀███   ▄▄▄       ▄████▄   ██ ▄█▀
▒ ▒ ▒ ▄▀░▒ ▒ ▒ ▄▀░▒██▀ ▀█  ▓██ ▒ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ 
░ ▒ ▄▀▒░ ░ ▒ ▄▀▒░ ▒▓█    ▄ ▓██ ░▄█ ▒▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ 
  ▄▀▒   ░  ▄▀▒   ░▒▓▓▄ ▄██▒▒██▀▀█▄  ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ 
▒███████▒▒███████▒▒ ▓███▀ ░░██▓ ▒██▒ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄
░▒▒ ▓░▒░▒░▒▒ ▓░▒░▒░ ░▒ ▒  ░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒
░░▒ ▒ ░ ▒░░▒ ▒ ░ ▒  ░  ▒     ░▒ ░ ▒░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░
░ ░ ░ ░ ░░ ░ ░ ░ ░░          ░░   ░   ░   ▒   ░        ░ ░░ ░ 
  ░ ░      ░ ░    ░ ░         ░           ░  ░░ ░      ░  ░   
░        ░        ░                           ░               '''


class main():
    def __init__(self):
        self.passFound_print = lambda tries,word: f"{Style.RESET_ALL}Password was found after {Fore.LIGHTCYAN_EX+str(tries)} {Style.RESET_ALL}tries. The password is: {Fore.LIGHTGREEN_EX+word}"
        self.tries_print = lambda tries,word: f"Tries: {tries} > {word}"
        self.saves_dir = os.path.dirname(os.path.abspath(__file__))+"/stateSaves"
        self.passFound = False
        self.done = False
    
    def signal_handler(self, signal, frame):
        self.done=True


    #############
    # Wordlist
    #############
    def wlist_crack(self, tries, wordlist, z, stream, archive_dir, wordlist_inp):
        content = z.namelist()
        for word in wordlist:
            try:
                if self.done==True:
                    confirm = input("\nAre you sure you want to stop (y/n) > ").lower()
                    if confirm == "y": self.save_state(archive_dir, wordlist_inp, word, stream, wordlist); return
                    self.done = False

                tries += 1
                if stream: print(self.tries_print(tries,word))
                z.setpassword(word.encode('utf8', errors='ignore'))
                z.read(content[0])
                self.passFound = True
                print(self.passFound_print(tries,word))
                return
            except:
                pass

    def wlist_crack_entry(self, archive_dir, wordlist_inp, showoutput_b, resume_index):
        tries = 0
        try:
            try: _archive = ZipFile(archive_dir, "r")
            except Exception as ex: print(ex); sys.exit(1)

            print("Loading Wordlist, Please wait")
            _wordlist = open(wordlist_inp, 'r', encoding="utf8", errors='ignore')
            wordlist = _wordlist.read().splitlines()
            _wordlist.close()
            if resume_index != None:
                wordlist = wordlist[resume_index-1:]
                tries = resume_index-1
            print("Generation complete, Trying Passwords")

            self.wlist_crack(tries, wordlist, _archive, showoutput_b, archive_dir, wordlist_inp)
        except IOError:
            print("Archive Or Wordlist Doesen't Exist")
            sys.exit(1)


    #############
    # Bruteforce
    #############
    def generate_charlist(self, charset):
        chars = [
            string.ascii_lowercase,  # 0
            string.ascii_uppercase,  # 1
            string.digits,          # 2
            string.punctuation,     # 3
            string.printable        # 4
        ]

        allowed_chars = set("01234+")
        charlist = ''.join(''.join([chars[int(c)] for c in charset.split('+') if c in allowed_chars]))
        if charlist == "": print("Invalid charset"); sys.exit(1)
        return charlist

    def memsafe_generate_bruteforce_list(self, charset, max_lenght):
        charlist = self.generate_charlist(charset)
        return (''.join(candidate)
            for candidate in chain.from_iterable(product(charlist, repeat=i)
            for i in range(1, max_lenght + 1)))
            
    def bruteforce_crack(self, tries, brutelist, z, stream, charset, max_lenght):
        content = z.namelist()
        for word in self.memsafe_generate_bruteforce_list(charset, max_lenght):
            try:
                if self.done == True:
                    confirm = input("\nAre you sure you want to stop (y/n) > ").lower()
                    if confirm == "y": return
                    self.done = False

                tries += 1
                if stream: print(self.tries_print(tries,word))
                z.setpassword(word.encode('utf8', errors='ignore'))
                z.read(content[0])
                self.passFound = True
                print(self.passFound_print(tries,word))
                return
            except:
                pass

    def bruteforce_crack_entry(self, archive_dir, charset, max_letters, showoutput_b, resume_index):
        tries = 0
        try:
            try: _archive = ZipFile(archive_dir, "r")
            except Exception as ex: print(ex); sys.exit(1)
            print("Started...")
            self.bruteforce_crack(tries,None,_archive,showoutput_b, charset, max_letters)
        except IOError:
            print("Zipfile Doesent Exist")
            sys.exit(1)


    ######################
    # Restore/Save state
    ######################
    def save_state(self, archive_dir, wordlist_inp, current_word, showoutput_b, generated_list):
        while True:
            saveState = input("\nDo you want to save the Current State and continue from here later? [--restore]  (y/n) > ").lower()
            if saveState == "y":
                try:
                    print("[+] Saving Current State")
                    if not os.path.exists(self.saves_dir): os.makedirs(self.saves_dir)
                    
                    name = f"{self.saves_dir}/{time.strftime('%b-%d-%Y-%H-%M-%S')}-wordlist.txt"
                    f = open(name,"w")
                    f.write(f"{os.path.abspath(archive_dir)},{os.path.abspath(wordlist_inp)},{int(showoutput_b)},{generated_list.index(current_word)}")
                    f.close()
                    print(f"[finished] {name}")
                    break
                except IOError as ex:
                    print(f"Error when saving file: {ex}")
                except Exception as ex:
                    print(f"Unexpected error: {ex}")
            elif saveState == "n":
                break
                    

    def restore(self):
        try:
            savefiles = [f for f in os.listdir("./stateSaves") if os.path.isfile(os.path.join("./stateSaves", f))]
            restoreNbr = int(options.restore)
            print(savefiles[restoreNbr])
            f = open(f"./stateSaves/{savefiles[restoreNbr]}")
            resfile = f.read().split(',')
            f.close()

            self.wlist_crack_entry(resfile[0], resfile[1], bool(int(resfile[2])), int(resfile[3]))
        except FileNotFoundError:
            print("No restore files found")
        except IndexError as ex:
            print(f"Restore file index given is not valid or the restorefile is broken {ex}")
        except Exception as ex:
            print(f"Unexpected error: {ex}")

    #################
    # No args / Args
    #################
    def _noargs(self):
        print(Fore.CYAN + banner)
        print("\nhttps://github.com/robi0t\n"+Style.RESET_ALL)
        archive_dir = input('\nEnter a directory/name to a .zip file > ')
        attack_type = input('Which attack type would you like to run\n0: Bruteforce\t 1: Wordlist > ')

        if attack_type == "1":
            wordlist_inp = input("[+] Enter a directory/name to a password list > ")
            showOutPut = input("\nDo you want to output everything (slower) or not (faster)  y/n > ")
            if showOutPut.lower() == "y":
                showoutput_b = True
            else:
                showoutput_b = False
            self.wlist_crack_entry(archive_dir, wordlist_inp, showoutput_b, None)

        elif attack_type == "0":
            charset = input('\n[+] Which characters to use in the attack (combine to use multiple, separated by +)\n 0: Only small letters\n 1: Only big letters\n 2: Only numbers\n 3: Only signs\n 4: Everything\n> ')
            try:
                max_letters = int(input("\n[-+] Max length > "))
                if max_letters < 0:
                    print("The given number is not a vaild Positive number")
                    sys.exit(1)
            except:
                print("The input given is not a vaild Integer number")
                sys.exit(1)
            showOutPut = input("\nDo you want to output everything (slower) or not (faster)  y/n > ")
            if showOutPut.lower() == "y": showoutput_b = True
            else: showoutput_b = False
            self.bruteforce_crack_entry(archive_dir, charset, max_letters, showoutput_b, None)
        else:
            print("Invalid Input")
        sys.exit(1)

    def _args(self):
        if options.archive == None and options.reslist == False and options.restore == None:
            print("No Zipfile Given")
            sys.exit(1)
        archive_dir = options.archive
            
        if options.wordlist != None:
            wordlist_inp = options.wordlist
            showoutput_b = options.showoutput
            
            self.wlist_crack_entry(archive_dir, wordlist_inp, showoutput_b, None)

        elif options.bruteforce == True:
            charset = options.charlist
            if charset == None:
                print("No Charlist Given")
                sys.exit(1)

            max_letters_inp = options.maxlenght
            if max_letters_inp == None:
                print("No MaxLenght Given")
            try:
                max_letters = int(max_letters_inp)
                if max_letters < 0:
                    print("The given MaxLenght is not a vaild Positive number")
                    sys.exit(1)
            except:
                print("The given MaxLenght is not a vaild Integer number")
                sys.exit(1)

            showoutput_b = options.showoutput
            self.bruteforce_crack_entry(archive_dir, charset, max_letters, showoutput_b, None)

        elif options.restore != None:
            self.restore()
        
        elif options.reslist == True:
            try:savefiles = [f for f in os.listdir("./stateSaves") if os.path.isfile(os.path.join("./stateSaves", f))]
            except: print("No savefiles found"); sys.exit(1)
            print('\n'.join(f"{savefiles.index(saves)} > {savefiles[savefiles.index(saves)]}" for saves in savefiles))
            print("\n\nusage:[-r (file index)] [--restore (file index)]")
            
        else:
            print("No Cracking Method Given")
        sys.exit(1)


    #################
    # Main
    #################
    def main(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        if len(sys.argv[1:]) == 0:
            self._noargs()
        else:
            self._args()
        print(Style.RESET_ALL)
    
        if self.passFound == False:
            print("Couldnt Crack The Password With The Current Options")
        

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", dest="archive", metavar=" ",
                    help="Archive To Crack")
    parser.add_option("-w", dest="wordlist",
                    help="Enter the name Or directory to the wordlist for a wordlist attack", metavar=" ")
    parser.add_option("-b",
                    action="store_true", dest="bruteforce", default=False,
                    help="Attack method to bruteforce the zipfile password")              
    parser.add_option("-c", dest="charlist",
                    help="(Required for Bruteforce)\nWhich characters to use in the Bruteforce attack (combine to use multiple, separated by +) 0: Only small letters | 1: Only big letters | 2: Only numbers | 3: Only signs | 4: Everything", metavar=" ") #byt
    parser.add_option("-l", dest="maxlenght",
                    help="The max lenght for the bruteforce passwords (Required for Bruteforce)", metavar=" ")
    parser.add_option("-s", "--stream",
                    action="store_true", dest="showoutput", default=False,
                    help="Stream tried passwords (slower)")
    #restore
    parser.add_option("-r", "--restore", dest="restore",
                    help="Restore state From save (do --rl for a list of vaild options)", metavar=" ")
    parser.add_option("--rl",
                    action="store_true", dest="reslist", default=False,
                    help="Shows a list of all restore files found")
    (options, args) = parser.parse_args()

    init()    
    main().main()
