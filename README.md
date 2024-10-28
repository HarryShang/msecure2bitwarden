# msecure2bitwarden

The BitWarden doesn't support importing the mSecure exported csv file.
The mSecure csv file format have variable length for each record. So the BitWarde almost impossible to directlly import the mSecure csv file.
I create a small Python app msecure2bw to do the convertion. It can almost perfect convert all the mSecure record to BitWarden supported format.
The usage is simple. First export the mSecure records and create the msecure_pass.csv file.
Then run the command "msecure2bw msecure_pass.csv" on Linux. Or run the command "msecure2bw.exe msecure_pass.csv" to convert the csv file to json file.
The msecure2bw will convert the csv file into different json file. Each mSecure group will be generated into one json file.
The mSecure group will be converted to BitWarden organization. And the mSecure record type (Like Bank Account, Credit Card etc) will be converted to BitWarden Collections.
In the BitWarden app, you have to create the organization first to match the mSecure group.
Then go to the Admin Console and select that organization. Select Settings->Import data. Do not select any collection. And select the file format to Bitwarden json.
Click the Choose file to select that group json file then click Import data button.
