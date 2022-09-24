import requests
import schedule
import time
import colorama
from steampy.client import SteamClient
import authdata

colorama.init()
steam_client = SteamClient(authdata.api_key)

def log_in_steam():
    try:
        steam_client.login(authdata.login, authdata.password, "guard.json")
    except Exception as e:
        print(colorama.Fore.RED + f"fatal steam login error: {str(e)}")
        exit(1)

def check_trade():
    try:
        res_trader = requests.get(f"https://api.steam-trader.com/exchange/?key={authdata.trader_api}")
        res_trade_json = res_trader.json()
        print(colorama.Fore.BLUE + "[Info] Request has been sent to check tradeofferid on website")
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
            
    except Exception as e:
        print(colorama.Fore.RED + f"steam-trader request failed: {str(e)}")

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

start_bot()
