import socket
import socks
import ssl
import json
from threading import Thread, Lock, active_count
import requests
from typing import List, Tuple
from time import sleep
from itertools import cycle
import sys
import subprocess

from colorama import Fore, init
import requests
import msmcauth


class Socket:
    pass

class PandoraException(Exception):
    def __init__(self, message) -> None:
        self.message = f"{Fore.RED} {message}"
        super().__init__(self.message)
        
class InvalidFormatting(PandoraException):
    pass

class InvalidAccountType(PandoraException):
    pass


class MicrosoftAccount:
    def __init__(self, email: str, password: str, target: str) -> None:
        self.email = email
        self.password = password
        self.target = target
        self.bearer = self.authenticate()
        
        self.URL = "https://api.minecraftservices.com/minecraft/profile/name/%s/available" % (target)
        self.HEADERS = {"Authorization": f"Bearer {self.bearer}"}
        self.check_payload = bytes(f"GET /minecraft/profile/name/{target}/available HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer " + f"{self.bearer}\r\n\r\n", 'utf-8')
        self.payload = bytes(f"PUT /minecraft/profile/name/{self.target} HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer {self.bearer}\r\nContent-Length: 0\r\n\r\n", 'utf-8')
            
        self.successful_snipe = None
        
        self.skin_change_result = None
    
    def create_threads(self) -> None:
        threads = [Thread(target=self.send_requests) for _ in range(14)]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
    
        
    def authenticate(self) -> str:
        return msmcauth.login(self.email, self.password).access_token
    
    
    def send_requests(self) -> None:
        global sockets_available
        
        if PROXIES_ENABLED:
            proxy = next(proxy_iter)
            
            sock = socks.create_connection(
                ('api.minecraftservices.com', 443),
                proxy_type=proxy['proxy_type'],
                proxy_addr=proxy['host'],
                proxy_port=['port']
            )
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            sock.connect(('api.minecraftservices.com', 443))
        
        sock_ = ssl.create_default_context().wrap_socket(sock, server_hostname='api.minecraftservices.com')
        
        sock_.send(self.check_payload)
        
        data = sock_.recv(1024).decode('utf-8')
        try:
            resp_json = json.JSONDecoder().raw_decode(data[data.index('{')::])[0]
            try:
                status = resp_json.__getitem__('status')
                
            except KeyError:
                thread_safe_print(f"{Fore.LIGHTRED_EX}You're being Rate Limited")
                
                return sock.close()
        except json.JSONDecodeError:
            thread_safe_print(f"{Fore.CYAN}{self.target} is taken/not avaliable")
            
            return sock.close()
        
        if status == "DUPLICATE":
            thread_safe_print(f"{Fore.CYAN}{self.target} is taken/not avaliable")
            
        elif status == "AVAILABLE":
            thread_safe_print(f"{Fore.GREEN}{self.target} is avaliable.")
            
            if sockets_available > 0:
                Thread(target=self.change_name, args=(sock_,)).start()
                sockets_available -=1
                
                sleep(3)
                
        sock.close()
                               
    def change_name(self, sock: socket.socket) -> None:
        # Send data
        sock.send(self.payload)
        
        # recive data
        data = sock.recv(2048).decode('utf-8')
        
        # status code
        try:
            status = int(data.split('Content-Type')[0].rstrip()[8:12].rstrip())
        except ValueError:
            thread_safe_print(f'{Fore.RED}Request failed due to an error')
            return
            
        if status in (200, 203):
            global global_success
            thread_safe_print(f"{Fore.CYAN}[{Fore.LIGHTGREEN_EX}{status}{Fore.CYAN}] ~ :))")
            self.successful_snipe = True
            global_success = True
                 
        elif status >= 500:
            thread_safe_print(f'{Fore.LIGHTYELLOW_EX}[{Fore.MAGENTA}{status}{Fore.LIGHTYELLOW_EX}] {Fore.LIGHTRED_EX}Lagged :((\n')
            
        elif status == 400:
            thread_safe_print(f"{Fore.YELLOW}[{Fore.RED}{status}{Fore.YELLOW}] ~ :((")
            
        else:
            thread_safe_print(f"{Fore.YELLOW}[{Fore.RED}{status}{Fore.YELLOW}] ~ :((")
        
    def turbo(self) -> None:
        global thread_safe_fail_print, global_success
        while True:
            self.create_threads()
            if sockets_available <= 0:
                break
            sleep(60)
            
        if self.successful_snipe:
            self.success()
            
        else:
            if thread_safe_fail_print < 1 and not global_success:
                thread_safe_fail_print +=1
                print(f"{Fore.GREEN}Failed to snipe {self.target}")
     
    def success(self) -> None:
        print(f"{Fore.RED}Succesfully Sniped {Fore.CYAN}{self.target} onto {Fore.LIGHTGREEN_EX}{self.email}!")
        if SKIN_CHANGE:
            Thread(target=self.skin_change).start()
            
            # fancy fake loading screen :D
            while self.skin_change_result is None:
                for loading_symbol in cycle(['|', '/', '-', '\\']):
                    print(f"{Fore.LIGHTMAGENTA_EX}Changing skin: {Fore.YELLOW}{loading_symbol}", end="\r", flush=True)
                    sleep(0.1)
                    if self.skin_change_result != None:
                        break
            
            if self.skin_change_result in (200, 203):
                print(f"{Fore.LIGHTGREEN_EX}Successfuly changed skin: {self.skin_change_result}✔️")
                
            else:
                print(f"{Fore.RED}Failed to change skin: {self.skin_change_result}❌")
                
                
    def skin_change(self) -> None:
        sleep(5)
        self.skin_change_result = requests.post(
                    "https://api.minecraftservices.com/minecraft/profile/skins",
                        headers={
                                "Authorization": f"Bearer {self.bearer}",
                                 "Content-Type": "application/json"
                                 },
                            json={
                                "url": f"{SKIN_URL}",
                                  "variant": f"{SKIN_VARIANT}"
                                  }
                            ).status_code
        
class BearerAccount(MicrosoftAccount):
    def __init__(self, bearer: str, target: str, *, acc_type=None):
        self.bearer = bearer
        self.target = target
        if acc_type == "nc":
            self.payload = bytes(f"PUT /minecraft/profile/name/{self.target} HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer {self.bearer}\r\nContent-Length: 0\r\n\r\n", 'utf-8')
        
        elif acc_type == "gc":
            self.payload = bytes("\r\n".join(["POST /minecraft/profile HTTP/1.1", "Host: api.minecraftservices.com", "Content-Type: application/json", f"Authorization: Bearer {bearer}", "User-Agent: Pandora", "Content-Length: %d" % len('{"profileName": "%s"}') % (target), "", '{"profileName": "%s"}' % (target)]), "utf-8")
        
        self.session = requests.Session()
        self.URL = "https://api.minecraftservices.com/minecraft/profile/name/%s/available" % (target)
        self.HEADERS = {"Authorization": f"Bearer {self.bearer}"}
        self.successful_snipe = None
        
        
    def turbo(self) -> None:
        return super().turbo()
        
    def change_name(self, sock: socket.socket) -> None:
        return super().change_name(sock)
    
    def create_threads(self) -> None:
        return super().create_threads()
    
    def send_requests(self) -> None:
        return super().send_requests()      
        
    def success(self) -> None:
        return super().success()
                       
    def skin_change(self) -> None:
        return super().skin_change()
    

def parse_accounts(target) -> str:
    bearers_authenticated = int(); microsoft_accounts_authenticated = int()
    
    if ACC_TYPE not in ("nc", "gc", "ncgc", "ncb", "gcb"):
        raise InvalidAccountType(
            message="Invalid account type"
        )
    
    if ACC_TYPE in ('nc', 'gc') and len(BEARERS) <1 and len(ACCOUNTS) > 1:
        for idx, account in enumerate(ACCOUNTS):
            if len((split_co := account.split(":"))) != 2:
                print(f"{Fore.RED}Invalid account at index {idx+1}")
                continue
            
            email, password = split_co
            
            accounts.append(MicrosoftAccount(email, password, target))
            
        if len(accounts) < 1:
            raise InvalidFormatting(
                message="None of your accounts were formatted correctly"
            )
        
        return f"{Fore.GREEN}Authenticated {len(accounts)} Microsoft Accounts"
    
    elif ACC_TYPE in ('nc', 'gc') and len(BEARERS) >= 1:
        print(f"{Fore.YELLOW}[!] {Fore.RED}Any bearer you entered incorrectly will not be checked!!")
        for BEARER in BEARERS:
            if BEARER == "leave empty if you're not using bearers":
                continue 
            accounts.append(BearerAccount(BEARER, target))
            
            
        return f"{Fore.GREEN}Authenticated {len(accounts)} bearers"
            
    elif ACC_TYPE in ("ncgc", "ncb", "gcb") and len(ACCOUNTS) >= 1 and len(BEARERS) >= 1:
        print(f"{Fore.YELLOW}[!] {Fore.RED}Any bearer you entered incorrectly will not be checked!!")
        for idx, account in enumerate(ACCOUNTS):
            if len((split_co := account.split(":"))) != 2:
                print(f"{Fore.RED}Invalid account at index {idx+1}")
                continue
            
            email, password = split_co
            
            accounts.append(MicrosoftAccount(email, password, target))
            microsoft_accounts_authenticated +=1
            
        for BEARER in BEARERS: 
            if BEARER == "leave empty if you're not using bearers":
                continue
            
            accounts.append(BearerAccount(BEARER, target, acc_type="nc")) if ACC_TYPE == "ncb" else accounts.append(BearerAccount(BEARER, target, acc_type="gc"))
            bearers_authenticated +=1
            
        return f"{Fore.GREEN}Authenticated {microsoft_accounts_authenticated} Microsoft Accounts and {bearers_authenticated} Bearers/gcs"
                   
        
def parse_json() -> Tuple[str, List, List, bool, str, str]:
    try:
        with open("config.json", mode="r") as file:
            config = json.load(file)
        return config.__getitem__('account_type'), config.__getitem__('bearers'), config.__getitem__('accounts'), config.__getitem__('skin_change'), config.__getitem__('skin_variant'), config.__getitem__('skin_url')
        
    except FileNotFoundError as e:
        e.add_note(f"{Fore.RED}config.json not found")
        e.__notes__.append(f"{Fore.RED}Auto config not implemented yet...")
        raise

def clear() -> None:
    if sys.platform == "win32":
        subprocess.run('cls', shell=True)
        
    else:
        subprocess.run('clear')

def main() -> None:
    print(f"""{Fore.MAGENTA}
 _  (`-') (`-')  _ <-. (`-')_  _(`-')                 (`-')  (`-')  _     (`-')                   (`-') <-.(`-')            
 \-.(OO ) (OO ).-/    \( OO) )( (OO ).->     .->   <-.(OO )  (OO ).-/     ( OO).->       .->   <-.(OO )  __( OO)      .->   
 _.'    \ / ,---.  ,--./ ,--/  \    .'_ (`-')----. ,------,) / ,---.      /    '._  ,--.(,--.  ,------,)'-'---.\ (`-')----. 
(_...--'' | \ /`.\ |   \ |  |  '`'-..__)( OO).-.  '|   /`. ' | \ /`.\     |'--...__)|  | |(`-')|   /`. '| .-. (/ ( OO).-.  '
|  |_.' | '-'|_.' ||  . '|  |) |  |  ' |( _) | |  ||  |_.' | '-'|_.' |    `--.  .--'|  | |(OO )|  |_.' || '-' `.)( _) | |  |
|  .___.'(|  .-.  ||  |\    |  |  |  / : \|  |)|  ||  .   .'(|  .-.  |       |  |   |  | | |  \|  .   .'| /`'.  | \|  |)|  |
|  |      |  | |  ||  | \   |  |  '-'  /  '  '-'  '|  |\  \  |  | |  |       |  |   \  '-'(_ .'|  |\  \ | '--'  /  '  '-'  '
`--'      `--' `--'`--'  `--'  `------'    `-----' `--' '--' `--' `--'       `--'    `-----'   `--' '--'`------'    `-----' 
""")
    name = input(f"{Fore.LIGHTYELLOW_EX}[?] Target? ~ ").rstrip()
    if name.__len__() < 3 or name.__len__() > 16:
        clear()
        main()
        
    print(parse_accounts(name))
    
    threads = [Thread(target=account.turbo) for account in accounts]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    
    quit()

def thread_safe_print(message) -> None:
    with lock:
        print(message)        

def quit() -> None:
    threads = active_count() - 1
    while threads:
        threads = active_count() - 1
        sleep(0.5)
        
    sys.exit("Program finished")
    
def setup_proxies() -> dict:
    with open('config.json') as config:
        config_ = json.load(config)
    
    try:
        _proxies = config_['proxies']
    except Exception:
        sys.exit("Proxies option not found in 'config.json'")
    
    for proxy in _proxies:
        proxy_type = proxy['proxy_type']
        
        if proxy_type == "SOCK5":
            proxy['proxy_type'] = socks.PROXY_TYPE_SOCKS5
            
        elif proxy_type == "SOCK4":
            proxy['proxy_type'] = socks.PROXY_TYPE_SOCKS4
            
        elif proxy_type == "HTTP":
            proxy['proxy_type'] = socks.PROXY_TYPE_HTTP
            
        else:
            print(f"{Fore.RED}Invalid proxy type '{proxy_type}'")
            quit()
        
        
    return _proxies, len(_proxies) > 0

if __name__ == "__main__":
    clear()
    init(autoreset=True)
    proxies, PROXIES_ENABLED = setup_proxies()
    if PROXIES_ENABLED:
        proxy_iter = cycle(proxies)
    
    
    accounts: List[MicrosoftAccount] = []
    lock = Lock()
    thread_safe_fail_print: int = 0
    sockets_available: int = 5
    global_success = False
    ACC_TYPE, BEARERS, ACCOUNTS, SKIN_CHANGE, SKIN_VARIANT, SKIN_URL = parse_json()
    
    main()
