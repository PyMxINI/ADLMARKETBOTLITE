import requests
import schedule
import time
import colorama
from steampy.client import SteamClient
import authdata

colorama.init()
steam_client = SteamClient(authdata.api_key)
steam_client.login(authdata.login, authdata.password, "guard.json")


def check_trade():
    res_trader = requests.get(f"https://api.steam-trader.com/exchange/?key={authdata.trader_api}")
    res_trade_json = res_trader.json()
    print(colorama.Fore.BLUE + "[Info] Request has been sent to check tradeofferid on website")
    try_amount = 10

    success_steamtrader = res_trade_json.get("success", "")
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
    else:
        print(colorama.Fore.GREEN + f"[Info] No available trades")


def session_ok():
    if steam_client.is_session_alive():
        print(colorama.Fore.GREEN + '[Info]Steam Session Online!')
    else:
        if not steam_client.is_session_alive():
            print(colorama.Fore.RED + '[Info]Session expired relogin....!')
            steam_client.login(authdata.login, authdata.password, "guard.json")


def start_bot():
    check_trade()

    schedule.every(180).seconds.do(check_trade)
    schedule.every(30).minutes.do(session_ok)

    while True:
        schedule.run_pending()


start_bot()
