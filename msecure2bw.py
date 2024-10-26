import sys
import argparse
import hashlib
import datetime
import json

useFolder = False

def getTokens(line):
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
        if end < 0: break
        end = line.find(',', start)
    if start > 0:
        item = line[start:]
        tokens.append(item)
    return tokens

def getId(name):
    md5 = hashlib.md5(name.encode())
    md5digit = md5.digest()
    Id = ""
    fmt = "{:02x}"
    for i in range(4):
        Id += fmt.format(md5digit[i])
    Id += "-"
    for i in range(4, 6):
        Id += fmt.format(md5digit[i])
    Id += "-"
    for i in range(6, 8):
        Id += fmt.format(md5digit[i])
    Id += "-"
    for i in range(8, 10):
        Id += fmt.format(md5digit[i])
    Id += "-"
    for i in range(10, 16):
        Id += fmt.format(md5digit[i])
    return Id

def getDate():
    d = datetime.datetime.now()
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def addField(fields, name, value):
    if len(value) > 0:
        field = dict()
        field["name"] = name
        field["value"] = value
        field["type"] = 0
        field["linkedId"] = None
        fields.append(field)

def main() -> int:
    parser = argparse.ArgumentParser(description = "Convert mSecure csv file to bitWarden json file.")
    parser.add_argument("file", help = "csv file exported from mSecure.")
    parser.add_argument("-f", "--folder", action="store_true", help = "Output folder elements instead of collection elements.")
    parser.add_argument("-e", "--encoding", default = "utf_8", help = "Specify the file encoding. Default is utf_8.")
    args = parser.parse_args()
    useFolder = args.folder
    groupName = list()
    groupData = list()
    f = open(args.file, "r", encoding = args.encoding)
    for line in f:
        line = line.strip()
        # split string to tokens
        # token 0 is group name
        # token 1 is collection type
        # token 2 is item name
        # token 3 is item notes
        # other tokens are based on the collection type
        tokens = getTokens(line)
        # Add this group into group list
        for i in range(len(groupName)):
            if tokens[0] == groupName[i]:
                break
        else:
            groupName.append(tokens[0])
            group = dict()
            group["encrypted"] = False
            if useFolder:
                group["folders"] = list()
            else:
                group["collections"] = list()
            group["items"] = list()
            groupData.append(group)
        # get the groupId from the group list
        groupId = 0
        while groupId < len(groupName):
            if tokens[0] == groupName[groupId]:
                break
            groupId += 1
        if useFolder:
            collections = groupData[groupId].get("folders")
        else:
            collections = groupData[groupId].get("collections")
        collectionId = getId(tokens[1])
        items = groupData[groupId].get("items")
        for i in range(len(collections)):
            if collections[i].get("name") == tokens[1]:
                break
        else:
            # Add collection type into collections set
            collection = dict()
            collection["id"] = collectionId
            collection["name"] = tokens[1]
            if not useFolder:
                collection["organizationId"] = None
                collection["externalId"] = None
            collections.append(collection)
        item = dict()
        item["passwordHistory"] = None
        item["revisionDate"] = getDate()
        item["creationDate"] = getDate()
        item["deletedDate"] = None
        item["id"] = getId(tokens[2])
        item["organizationId"] = None
        if useFolder:
            item["folderId"] = getId(tokens[1])
        else:
            item["folderId"] = None
        item["reprompt"] = 0
        item["name"] = tokens[2]
        item["notes"] = tokens[3]
        item["favorite"] = False
        # Add other items based on the collection type
        if tokens[1] == "Bank Accounts":
            # token 4 is Account Number
            # token 5 is PIN
            # token 6 is Name
            # token 7 is Branch
            # token 8 is Phone No.
            # Encodee into BW card
            if len(tokens[7]) > 0 or len(tokens[8]) > 0:
                fields = list()
                addField(fields, "Branch", tokens[7])
                addField(fields, "Phone", tokens[8])
                item["fields"] = fields
            item["type"] = 3
            card = dict()
            card["cardholderName"] = tokens[6]
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = None
            card["code"] = tokens[5]
            item["card"] = card
        elif tokens[1] == "Birthdays":
            # token 4 is Birthday
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = None
            card["brand"] = None
            card["number"] = None
            card["expMonth"] = None
            card["expYear"] = tokens[4]
            card["code"] = None
            item["card"] = card
        elif tokens[1] == "Calling Cards":
            # token 4 is Access No.
            # token 5 is PIN
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = None
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = None
            card["code"] = tokens[5]
            item["card"] = card
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
                fields = list()
                addField(fields, "Shirt Size", tokens[4])
                addField(fields, "Pant Size", tokens[5])
                addField(fields, "Shoe Size", tokens[6])
                addField(fields, "Dress Size", tokens[7])
                item["fields"] = fields
            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
        elif tokens[1] == "Combinations":
            # token 4 is Code
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = None
            card["brand"] = None
            card["number"] = None
            card["expMonth"] = None
            card["expYear"] = None
            card["code"] = tokens[4]
            item["card"] = card
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
                fields = list()
                addField(fields, "Bank", tokens[8])
                addField(fields, "Security Code", tokens[9])
                addField(fields, "Web", tokens[10])
                addField(fields, "User Name", tokens[11])
                addField(fields, "Password", tokens[12])
                addField(fields, "Phone", tokens[13])
                addField(fields, "Phone(International)", tokens[14])
                item["fields"] = fields
            item["type"] = 3
            card = dict()
            card["cardholderName"] = tokens[6]
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = tokens[5]
            card["code"] = tokens[7]
            item["card"] = card
        elif tokens[1] == "Email Accounts":
            # token 4 is Username
            # token 5 is Password
            # token 6 is POP3 Host
            # token 7 is SMTP Host
            # Encode into BW Login
            if len(tokens[6]) > 0 or \
                len(tokens[7]) > 0:
                fields = list()
                addField(fields, "POP3 Host", tokens[6])
                addField(fields, "SMTP Host", tokens[7])
                item["fields"] = fields
            item["type"] = 1
            login = dict()
            uris = list()
            uri = dict()
            uri["match"] = None
            uri["uri"] = None
            uris.append(uri)
            login["uris"] = uris
            login["username"] = tokens[4]
            login["password"] = tokens[5]
            login["totp"] = None
            item["login"] = login
        elif tokens[1] == "Frequent Flyer":
            # token 4 is Number
            # token 5 is URL
            # token 6 is Username
            # token 7 is Password
            # token 8 is Mileage
            # Encode into BW Login
            if len(tokens[4]) > 0 or \
                len(tokens[8]) > 0:
                fields = list()
                addField(fields, "Number", tokens[4])
                addField(fields, "Mileage", tokens[8])
                item["fields"] = fields
            item["type"] = 1
            login = dict()
            uris = list()
            uri = dict()
            uri["match"] = None
            uri["uri"] = tokens[5]
            uris.append(uri)
            login["uris"] = uris
            login["username"] = tokens[6]
            login["password"] = tokens[7]
            login["totp"] = None
            item["login"] = login
        elif tokens[1] == "Government cards":
            # token 4 is Name
            # token 5 is Number
            # token 6 is Expire Date
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = tokens[4]
            card["brand"] = None
            card["number"] = tokens[5]
            card["expMonth"] = None
            card["expYear"] = tokens[6]
            card["code"] = None
            item["card"] = card
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
                fields = list()
                addField(fields, "Office Phone", tokens[16])
                addField(fields, "Mobile Phone", tokens[17])
                addField(fields, "Email2", tokens[19])
                addField(fields, "Skype", tokens[20])
                addField(fields, "Website", tokens[21])
                item["fields"] = fields
            item["type"] = 4
            id = dict()
            id["title"] = tokens[8]
            id["firstName"] = tokens[4]
            id["middleName"] = tokens[6]
            id["lastName"] = tokens[5]
            id["address1"] = tokens[9]
            id["address2"] = tokens[10]
            id["address3"] = None
            id["city"] = tokens[11]
            id["state"] = tokens[12]
            id["postalCode"] = tokens[14]
            id["country"] = tokens[13]
            id["company"] = tokens[7]
            id["email"] = tokens[18]
            id["phone"] = tokens[15]
            id["ssn"] = None
            id["username"] = None
            id["passportNumber"] = None
            id["licenseNumber"] = None
            item["identity"] = id
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
                fields = list()
                addField(fields, "Policy No.", tokens[4])
                addField(fields, "Group No.", tokens[5])
                addField(fields, "Insured", tokens[6])
                addField(fields, "Date", tokens[7])
                addField(fields, "Phone", tokens[8])
                item["fields"] = fields
            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
        elif tokens[1] == "Memberships":
            # token 4 is Account No.
            # token 5 is Name
            # token 6 is Date
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = tokens[5]
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = tokens[6]
            card["code"] = None
            item["card"] = card
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
                fields = list()
                addField(fields, "Name", tokens[4])
                addField(fields, "Number", tokens[5])
                addField(fields, "Type", tokens[6])
                addField(fields, "Issuing Country", tokens[7])
                addField(fields, "Issuing Authority", tokens[8])
                addField(fields, "Nationality", tokens[9])
                addField(fields, "Exoiration", tokens[10])
                addField(fields, "Place of Birth", tokens[11])
                item["fields"] = fields
            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
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
                fields = list()
                addField(fields, "RX Number", tokens[4])
                addField(fields, "Name", tokens[5])
                addField(fields, "Doctor", tokens[6])
                addField(fields, "Pharmacy", tokens[7])
                addField(fields, "Phone", tokens[8])
                item["fields"] = fields
            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
        elif tokens[1] == "Registration Codes":
            # token 4 is Number
            # token 5 is Date
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = None
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = tokens[5]
            card["code"] = None
            item["card"] = card
        elif tokens[1] == "Social Security":
            # token 4 is Name
            # token 5 is Number
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = tokens[4]
            card["brand"] = None
            card["number"] = tokens[5]
            card["expMonth"] = None
            card["expYear"] = None
            card["code"] = None
            item["card"] = card
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
                fields = list()
                addField(fields, "License No.", tokens[4])
                addField(fields, "VIN", tokens[5])
                addField(fields, "Date Purchased", tokens[6])
                addField(fields, "Tire Size", tokens[7])
                item["fields"] = fields
            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
        elif tokens[1] == "Voice Mail":
            # token 4 is Access No.
            # token 5 is PIN
            # Encode into BW card
            item["type"] = 3
            card = dict()
            card["cardholderName"] = None
            card["brand"] = None
            card["number"] = tokens[4]
            card["expMonth"] = None
            card["expYear"] = None
            card["code"] = tokens[5]
            item["card"] = card
        elif tokens[1] == "Web Logins":
            # token 4 is URL
            # token 5 is Username
            # token 6 is Password
            # Encode into BW Login
            item["type"] = 1
            login = dict()
            uris = list()
            uri = dict()
            uri["match"] = None
            uri["uri"] = tokens[4]
            uris.append(uri)
            login["uris"] = uris
            login["username"] = tokens[5]
            login["password"] = tokens[6]
            login["totp"] = None
            item["login"] = login
        else:
            # Handle Unassigned, Note and other undefined collection
            # Encode into BW notes
            fields = list()
            fid = 1
            for i in range(4, len(tokens)):
                if len(tokens[i]) > 0:
                    addField(fields, f"Field{fid}", tokens[i])
                    fid += 1
            item["fields"] = fields

            item["type"] = 2
            note = dict()
            note["type"] = 0
            item["secureNote"] = note
        if useFolder:
            item["collectionIds"] = None
        else:
            item["collectionIds"] = collectionId
        # Add into items
        items.append(item)
    f.close()

    for i in range(len(groupName)):
        fname = groupName[i] + ".json"
        outstr = json.dumps(groupData[i], ensure_ascii = False, indent = 4)
        outstr = outstr.replace("\\\\", "\\")
        with open(fname, "w", encoding = args.encoding) as f:
            f.write(outstr)
        print(fname + "generated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
