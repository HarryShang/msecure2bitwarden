""" Convert msecure csv file to bitwarden json file """

import sys
import argparse
import uuid
import hashlib
import datetime
import json

groupName = []
groupData = []

def gettokens(line):
    """ Get tokens from string """
    tokens = []
    start = 0
    end = line.find(',', start)
    while end > 0:
        if line[start] == '"':
            start += 1
            end = line.find('"', start)
            if end > 0:
                item = line[start:end]
                end = line.find(',', end)
            else:
                item = line[start:]
        else:
            item = line[start:end]
        tokens.append(item)
        start = end + 1
        if end < 0:
            break
        end = line.find(',', start)
    if start > 0:
        item = line[start:]
        tokens.append(item)
    return tokens

def getid(name):
    """ Calculate ID string from name """
    md5 = hashlib.md5(name.encode())
    return str(uuid.UUID(bytes = md5.digest()))

def getdate():
    """ Return current date string """
    d = datetime.datetime.now()
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def addfield(fields, name, value):
    """ Add name and value into fields """
    if len(value) > 0:
        field = {
            "name": name,
            "value": value,
            "type": 0,
            "linkedId": None
        }
        fields.append(field)

def addrecord(line, usefolder):
    """ Add one record """
    # split string to tokens
    # token 0 is group name
    # token 1 is collection type
    # token 2 is item name
    # token 3 is item notes
    # other tokens are based on the collection type
    tokens = gettokens(line)
    # Add this group into group list
    for gname in groupName:
        if tokens[0] == gname:
            break
    else:
        groupName.append(tokens[0])
        if usefolder:
            group = {
                "encrypted": False,
                "folders": [],
                "items": []
            }
        else:
            group = {
                "encrypted": False,
                "collections": [],
                "items": []
            }
        groupData.append(group)
    # get the groupid from the group list
    groupid = groupName.index(tokens[0])
    if usefolder:
        collections = groupData[groupid].get("folders")
    else:
        collections = groupData[groupid].get("collections")
    collectionid = getid(tokens[1])
    items = groupData[groupid].get("items")
    for col in collections:
        if col.get("name") == tokens[1]:
            break
    else:
        # Add collection type into collections set
        collection = {
            "id": collectionid,
            "name": tokens[1]
        }
        if not usefolder:
            collection["organizationId"] = None
            collection["externalId"] = None
        collections.append(collection)
    item = {
        "passwordHistory": None,
        "revisionDate": getdate(),
        "creationDate": getdate(),
        "deletedDate": None,
        "id": getid(tokens[2]),
        "organizationId": None,
        "folderId": getid(tokens[1]) if usefolder else None,
        "reprompt": 0,
        "name": tokens[2],
        "notes": tokens[3],
        "favorite": False
    }
    # Add other items based on the collection type
    if tokens[1] == "Bank Accounts":
        # token 4 is Account Number
        # token 5 is PIN
        # token 6 is Name
        # token 7 is Branch
        # token 8 is Phone No.
        # Encodee into BW card
        if len(tokens[7]) > 0 or len(tokens[8]) > 0:
            fields = []
            addfield(fields, "Branch", tokens[7])
            addfield(fields, "Phone", tokens[8])
            item["fields"] = fields
        item["type"] = 3
        item["card"] = {
            "cardholderName": tokens[6],
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": None,
            "code": tokens[5]
        }
    elif tokens[1] == "Birthdays":
        # token 4 is Birthday
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": None,
            "brand": None,
            "number": None,
            "expMonth": None,
            "expYear": tokens[4],
            "code": None
        }
    elif tokens[1] == "Calling Cards":
        # token 4 is Access No.
        # token 5 is PIN
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": None,
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": None,
            "code": tokens[5]
        }
    elif tokens[1] == "Clothes Size":
        # token 4 is Shirt Size
        # token 5 is Pant Size
        # token 6 is Shoe Size
        # token 7 is Dress Size
        # Encode into BW notes
        if len(tokens[4]) > 0 or \
                len(tokens[5]) > 0 or \
                len(tokens[6]) > 0 or \
                len(tokens[7]) > 0:
            fields = []
            addfield(fields, "Shirt Size", tokens[4])
            addfield(fields, "Pant Size", tokens[5])
            addfield(fields, "Shoe Size", tokens[6])
            addfield(fields, "Dress Size", tokens[7])
            item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}
    elif tokens[1] == "Combinations":
        # token 4 is Code
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": None,
            "brand": None,
            "number": None,
            "expMonth": None,
            "expYear": None,
            "code": tokens[4]
        }
    elif tokens[1] == "Credit Cards":
        # token 4 is CodeCard No.
        # token 5 is Expiration Date
        # token 6 is Name
        # token 7 is PIN
        # token 8 is Bank
        # token 9 is Security Code
        # token 10 is Web
        # token 11 is User Name
        # token 12 is Password
        # token 13 is Phone
        # token 14 is Phone(International)
        # Encode into BW card
        if len(tokens[8]) > 0 or \
                len(tokens[9]) > 0 or \
                len(tokens[10]) > 0 or \
                len(tokens[11]) > 0 or \
                len(tokens[12]) > 0 or \
                len(tokens[13]) > 0 or \
                len(tokens[14]) > 0:
            fields = []
            addfield(fields, "Bank", tokens[8])
            addfield(fields, "Security Code", tokens[9])
            addfield(fields, "Web", tokens[10])
            addfield(fields, "User Name", tokens[11])
            addfield(fields, "Password", tokens[12])
            addfield(fields, "Phone", tokens[13])
            addfield(fields, "Phone(International)", tokens[14])
            item["fields"] = fields
        item["type"] = 3
        item["card"] = {
            "cardholderName": tokens[6],
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": tokens[5],
            "code": tokens[7]
        }
    elif tokens[1] == "Email Accounts":
        # token 4 is Username
        # token 5 is Password
        # token 6 is POP3 Host
        # token 7 is SMTP Host
        # Encode into BW Login
        if len(tokens[6]) > 0 or \
                len(tokens[7]) > 0:
            fields = []
            addfield(fields, "POP3 Host", tokens[6])
            addfield(fields, "SMTP Host", tokens[7])
            item["fields"] = fields
        item["type"] = 1
        item["login"] = {
            "fido2Credentials": [],
            "uris": [
                {
                    "match": None,
                    "uri": None,
                }
            ],
            "username": tokens[4],
            "password": tokens[5],
            "totp": None
        }
    elif tokens[1] == "Frequent Flyer":
        # token 4 is Number
        # token 5 is URL
        # token 6 is Username
        # token 7 is Password
        # token 8 is Mileage
        # Encode into BW Login
        if len(tokens[4]) > 0 or \
                len(tokens[8]) > 0:
            fields = []
            addfield(fields, "Number", tokens[4])
            addfield(fields, "Mileage", tokens[8])
            item["fields"] = fields
        item["type"] = 1
        item["login"] = {
            "fido2Credentials": [],
            "uris": [
                {
                    "match": None,
                    "uri": tokens[5],
                }
            ],
            "username": tokens[6],
            "password": tokens[7],
            "totp": None
        }
    elif tokens[1] == "Government cards":
        # token 4 is Name
        # token 5 is Number
        # token 6 is Expire Date
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": tokens[4],
            "brand": None,
            "number": tokens[5],
            "expMonth": None,
            "expYear": tokens[6],
            "code": None
        }
    elif tokens[1] == "Identity":
        # token 4 is First Name
        # token 5 is Last Name
        # token 6 is Nick Name
        # token 7 is Company
        # token 8 is Title
        # token 9 is Address
        # token 10 is Address2
        # token 11 is City
        # token 12 is State/Provonce
        # token 13 is Country
        # token 14 is Zip/Post Code
        # token 15 is Home Phone
        # token 16 is Office Phone
        # token 17 is Mobile Phone
        # token 18 is Email
        # token 19 is Email2
        # token 20 is Skype
        # token 21 is Website
        # Encode into BW identity
        if len(tokens[16]) > 0 or \
                len(tokens[17]) > 0 or \
                len(tokens[19]) > 0 or \
                len(tokens[20]) > 0 or \
                len(tokens[21]) > 0:
            fields = []
            addfield(fields, "Office Phone", tokens[16])
            addfield(fields, "Mobile Phone", tokens[17])
            addfield(fields, "Email2", tokens[19])
            addfield(fields, "Skype", tokens[20])
            addfield(fields, "Website", tokens[21])
            item["fields"] = fields
        item["type"] = 4
        item["identity"] = {
            "title": tokens[8],
            "firstName": tokens[4],
            "middleName": tokens[6],
            "lastName": tokens[5],
            "address1": tokens[9],
            "address2": tokens[10],
            "address3": None,
            "city": tokens[11],
            "state": tokens[12],
            "postalCode": tokens[14],
            "country": tokens[13],
            "company": tokens[7],
            "email": tokens[18],
            "phone": tokens[15],
            "ssn": None,
            "username": None,
            "passportNumber": None,
            "licenseNumber": None
        }
    elif tokens[1] == "Insurance":
        # token 4 is Policy No.
        # token 5 is Group No.
        # token 6 is Insured
        # token 7 is Date
        # token 8 is Phone
        # Encode into BW notes
        if len(tokens[4]) > 0 or \
                len(tokens[5]) > 0 or \
                len(tokens[6]) > 0 or \
                len(tokens[7]) > 0 or \
                len(tokens[8]) > 0:
            fields = []
            addfield(fields, "Policy No.", tokens[4])
            addfield(fields, "Group No.", tokens[5])
            addfield(fields, "Insured", tokens[6])
            addfield(fields, "Date", tokens[7])
            addfield(fields, "Phone", tokens[8])
            item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}
    elif tokens[1] == "Memberships":
        # token 4 is Account No.
        # token 5 is Name
        # token 6 is Date
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": tokens[5],
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": tokens[6],
            "code": None
        }
    elif tokens[1] == "Passport":
        # token 4 is Name
        # token 5 is Number
        # token 6 is Type
        # token 7 is Issuing Country
        # token 8 is Issuing Authority
        # token 9 is Nationality
        # token 10 is Exoiration
        # token 11 is Place of Birth
        # Encode into BW notes
        if len(tokens[4]) > 0 or \
                len(tokens[5]) > 0 or \
                len(tokens[6]) > 0 or \
                len(tokens[7]) > 0 or \
                len(tokens[8]) > 0 or \
                len(tokens[9]) > 0 or \
                len(tokens[10]) > 0 or \
                len(tokens[11]) > 0:
            fields = []
            addfield(fields, "Name", tokens[4])
            addfield(fields, "Number", tokens[5])
            addfield(fields, "Type", tokens[6])
            addfield(fields, "Issuing Country", tokens[7])
            addfield(fields, "Issuing Authority", tokens[8])
            addfield(fields, "Nationality", tokens[9])
            addfield(fields, "Exoiration", tokens[10])
            addfield(fields, "Place of Birth", tokens[11])
            item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}
    elif tokens[1] == "Prescriptions":
        # token 4 is RX Number
        # token 5 is Name
        # token 6 is Doctor
        # token 7 is Pharmacy
        # token 8 is Phone
        # Encode into BW notes
        if len(tokens[4]) > 0 or \
                len(tokens[5]) > 0 or \
                len(tokens[6]) > 0 or \
                len(tokens[7]) > 0 or \
                len(tokens[8]) > 0:
            fields = []
            addfield(fields, "RX Number", tokens[4])
            addfield(fields, "Name", tokens[5])
            addfield(fields, "Doctor", tokens[6])
            addfield(fields, "Pharmacy", tokens[7])
            addfield(fields, "Phone", tokens[8])
            item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}
    elif tokens[1] == "Registration Codes":
        # token 4 is Number
        # token 5 is Date
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": None,
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": tokens[5],
            "code": None
        }
    elif tokens[1] == "Social Security":
        # token 4 is Name
        # token 5 is Number
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": tokens[4],
            "brand": None,
            "number": tokens[5],
            "expMonth": None,
            "expYear": None,
            "code": None
        }
    elif tokens[1] == "Vehicle Info":
        # token 4 is License No.
        # token 5 is VIN
        # token 6 is Date Purchased
        # token 7 is Tire Size
        # Encode into BW notes
        if len(tokens[4]) > 0 or \
                len(tokens[5]) > 0 or \
                len(tokens[6]) > 0 or \
                len(tokens[7]) > 0:
            fields = []
            addfield(fields, "License No.", tokens[4])
            addfield(fields, "VIN", tokens[5])
            addfield(fields, "Date Purchased", tokens[6])
            addfield(fields, "Tire Size", tokens[7])
            item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}
    elif tokens[1] == "Voice Mail":
        # token 4 is Access No.
        # token 5 is PIN
        # Encode into BW card
        item["type"] = 3
        item["card"] = {
            "cardholderName": None,
            "brand": None,
            "number": tokens[4],
            "expMonth": None,
            "expYear": None,
            "code": tokens[5]
        }
    elif tokens[1] == "Web Logins":
        # token 4 is URL
        # token 5 is Username
        # token 6 is Password
        # Encode into BW Login
        item["type"] = 1
        item["login"] = {
            "fido2Credentials": [],
            "uris": [
                {
                    "match": None,
                    "uri": tokens[4],
                }
            ],
            "username": tokens[5],
            "password": tokens[6],
            "totp": None
        }
    else:
        # Handle Unassigned, Note and other undefined collection
        # Encode into BW notes
        fields = []
        fid = 1
        for i in range(4, len(tokens)):
            if len(tokens[i]) > 0:
                addfield(fields, f"Field{fid}", tokens[i])
                fid += 1
        item["fields"] = fields
        item["type"] = 2
        item["secureNote"] = {"type": 0}

    item["collectionIds"] = [None] if usefolder else [collectionid]
    # Add into items
    items.append(item)

def main() -> int:
    parser = argparse.ArgumentParser(description = "Convert mSecure csv file to bitWarden json file.")
    parser.add_argument("file", help = "csv file exported from mSecure.")
    parser.add_argument("-f", "--folder", action="store_true", help = "Output folder elements instead of collection elements.")
    parser.add_argument("-e", "--encoding", default = "utf_8", help = "Specify the file encoding. Default is utf_8.")
    args = parser.parse_args()
    with open(args.file, "r", encoding = args.encoding) as f:
        for line in f:
            addrecord(line.strip(), args.folder)

    for gname in groupName:
        fname = gname + ".json"
        outstr = json.dumps(groupData[groupName.index(gname)], ensure_ascii = False, indent = 4)
        # Do not escape \n
        outstr = outstr.replace("\\\\n", "\\n")
        with open(fname, "w", encoding = args.encoding) as f:
            f.write(outstr)
        print(fname + " generated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
