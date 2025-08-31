import os
import sys
import json
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, NumberParseException
from colorama import init, Fore, Style

init(autoreset=True)

# ========== CONFIG FILE ========== #
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {}

NUMVERIFY_API_KEY = config.get("NUMVERIFY_API_KEY", "")
ABSTRACT_API_KEY = config.get("ABSTRACT_API_KEY", "")
TWILIO_ACCOUNT_SID = config.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = config.get("TWILIO_AUTH_TOKEN", "")

# ========== FUNCTIONS ========== #

def normalize_number(number, region="US"):
    try:
        parsed = phonenumbers.parse(number, region)
        return {
            "E.164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "National": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "International": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "Valid": phonenumbers.is_valid_number(parsed),
            "Carrier": carrier.name_for_number(parsed, "en"),
            "Region": geocoder.description_for_number(parsed, "en")
        }
    except NumberParseException as e:
        return {"Error": str(e)}


def check_numverify(number):
    if not NUMVERIFY_API_KEY:
        return {"Error": "NUMVERIFY_API_KEY not set"}
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={number}"
    r = requests.get(url)
    data = r.json()
    keys = ["valid", "number", "international_format", "country_code", "country_name", "carrier", "line_type"]
    return {k: data.get(k) for k in keys}


def check_abstractapi(number):
    if not ABSTRACT_API_KEY:
        return {"Error": "ABSTRACT_API_KEY not set"}
    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&phone={number}"
    r = requests.get(url)
    data = r.json()
    result = {
        "Valid": data.get("valid"),
        "Phone": data.get("phone"),
        "Carrier": data.get("carrier"),
        "Type": data.get("type"),
        "Country": data.get("country", {}).get("name"),
        "International": data.get("format", {}).get("international"),
        "Local": data.get("format", {}).get("local"),
        "Location": data.get("location")
    }
    return result


def check_twilio(number):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        return {"Error": "Twilio credentials not set"}
    url = f"https://lookups.twilio.com/v2/PhoneNumbers/{number}"
    r = requests.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
    data = r.json()
    keys = ["phone_number", "national_format", "line_type_intelligence", "caller_name", "country_code"]
    return {k: data.get(k) for k in keys}

# ========== MAIN OSINT FUNCTION ========== #

def osint_phone(number, region="US"):
    results = {"Normalized": normalize_number(number, region)}

    try:
        results["Numverify"] = check_numverify(number)
    except Exception as e:
        results["Numverify_Error"] = str(e)

    try:
        results["AbstractAPI"] = check_abstractapi(number)
    except Exception as e:
        results["AbstractAPI_Error"] = str(e)

    try:
        results["Twilio"] = check_twilio(number)
    except Exception as e:
        results["Twilio_Error"] = str(e)

    return results

# ========== ENTRY POINT ========== #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(Fore.RED + "Usage: python phone_osint.py <phone> [--region REGION] [--json]")
        sys.exit(1)

    number = sys.argv[1]
    region = "US"
    json_output = False

    if "--region" in sys.argv:
        region = sys.argv[sys.argv.index("--region") + 1]

    if "--json" in sys.argv:
        json_output = True

    data = osint_phone(number, region)

    if json_output:
        print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print(Fore.CYAN + "\n=== Numintel Results ===\n")
        for source, info in data.items():
            print(Fore.YELLOW + f"{source}:")
            if isinstance(info, dict):
                for k, v in info.items():
                    print(Fore.GREEN + f"{k}: {Fore.WHITE}{v}")
            else:
                print(Fore.WHITE + str(info))
            print()

