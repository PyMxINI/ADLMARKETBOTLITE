import requests
import schedule
import time
import os.path
import pickle
import colorama
from steampy.client import SteamClient
import authdata

colorama.init()
steam_client = SteamClient(authdata.api_key)

def log_in_steam():
    # Shitty hack for cookie caching right here
    # imagine the smell, mmmmm 
    if os.path.exists('./main.dat'):
        print('cookie file exists')
        if os.path.isfile('./main.dat'):
            print('cookie file surely exist and is file')
            print('loading cookies...')
            try:
                with open('./main.dat', "rb") as f:
                    steam_client._session.cookies._cookies = pickle.load(f)
            except Exception as e:
                print('restoring cookies from file failed: '+repr(e))
    else:
        print('cookie file not found')

    steam_client.was_login_executed = True
    steam_client.username = authdata.login
    steam_client._password = authdata.password
    if steam_client.is_session_alive():
        print('session is alive, no need to relogin')
        return
    else:
        print('no, session is kill, need to (re)login')
        steam_client.was_login_executed = False

    print('login in Steam...')
    try:
        steam_client.login(authdata.login, authdata.password, "guard.json")
    except Exception as e:
        print(colorama.Fore.RED + f"fatal steam login error: {repr(e)}")
        exit(1)
    else:
        print('logged into Steam, saving cookies...')
        with open('./main.dat', "wb") as f:
            pickle.dump(steam_client._session.cookies._cookies, f)

def check_trade():
    print(colorama.Fore.BLUE + "[Info] Request has been sent to check trades on steam-trader")
    try:
        res_trader = requests.get(f"https://api.steam-trader.com/exchange/?key={authdata.trader_api}")
    except Exception as e:
        print(colorama.Fore.RED + f"steam-trader request failed: {repr(e)}")

    try:
        res_trade_json = res_trader.json()
    except Exception as e:
        print(colorama.Fore.RED + f"steam-trader response parsing failed: {repr(e)}")
    else:
        try_amount = 10

        success_steamtrader = res_trade_json.get("success", "")
        errcode_steamtrader = res_trade_json.get("code", "")
        errstr__steamtrader = res_trade_json.get("error", "")
        if success_steamtrader:
            offer = (res_trade_json["offerId"])
            trade_accepted = False
            while not trade_accepted:
                try:
                    steam_client.accept_trade_offer(str(offer))
                    trade_accepted = True
                    print(colorama.Fore.GREEN + f"[Trade] {str(offer)} Accepted")
                except:
                    if try_amount < 0:
                        print(colorama.Fore.RED + f"[Trade] Can't accept trade {str(offer)},skipping")
                        break
                    print(colorama.Fore.RED + f"[Trade] Can't accept trade, trying one more time: {str(try_amount)}")
                    try_amount -= 1
                    time.sleep(10)
        elif success_steamtrader == False and errcode_steamtrader == 4:
            print(colorama.Fore.GREEN + f"nothing to trade right now")
        elif success_steamtrader == False and errcode_steamtrader:
            print(colorama.Fore.GREEN + f"steam-trader exchange error: {errstr__steamtrader} ({errcode_steamtrader})")
        else:
            print('wut?')

def session_ok():
    if steam_client.is_session_alive():
        print(colorama.Fore.GREEN + '[Info]Steam Session Online!')
    else:
        if not steam_client.is_session_alive():
            print(colorama.Fore.RED + '[Info]Session expired relogin....!')
            log_in_steam()


def start_bot():
    check_trade()

    schedule.every(180).seconds.do(check_trade)
    schedule.every(30).minutes.do(session_ok)

    while True:
        schedule.run_pending()
        time.sleep(1)

log_in_steam()
start_bot()
