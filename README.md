# forticare-api

Proof of concept python3 scripts using the FortiCare API to register Fortinet
registration codes and to retrieve license files.

# Before starting

Create in your working directory a `.forticare` in INI format as shown below

```
[forticare]
url = https://Support.Fortinet.COM/ES/FCWS_RegistrationService.svc/REST
token = NZTB-630M-OLYE-PPKG-4WWM-TL2A-WLZ2-0DJU
```

**NOTE:** Please contact your Fortinet representative to get a valid token.

# To register FGT, FMG, FAZ or FAC VM licenses

## Create a CSV file

It should have the following format:

```
# Use the '#' sign to comment a line
<registration_key>,<ip address>,<description>
```

For instance:

```
C6G36-V7TT7-DAE15-4EZ8T-U531B,192.168.244.200,FMG: SD-WAN orchestrator demo
D0UAB-FWEU6-MQ6A5-EVXZH-GHB1W,192.168.244.200,FMG: SD-WAN orchestrator demo
```

We are providing a CSV generator to produce the CSV file out of the ZIP file we
receive from Fortinet when ordering our products.
The above CSV output has been generated by using the following command line:

```
$ ./generate_csv.py -f FMG-VM-BASE_27228669.zip -d "FMG: SD-WAN orchestrator demo" --ip '192.168.244.200'
C6G36-V7TX7-DAE15-4EZ9T-U531B,192.168.244.200,FMG: SD-WAN orchestrator demo
D0UAB-FWEX6-MQ6A5-EVX8H-GHB1W,192.168.244.200,FMG: SD-WAN orchestrator demo
```

Notes:

  [1] For the moment, the CSV generator has been tested against ZIP files for
      FAC-VM, FAZ-VM, FGT-VM, FMG-VM and the 365 bundle entitlement products.

To generate a CSV file, just redirect the output to a file:

```
# For FAC-VM:
./generate_csv.py -f FAC-VM-BASE_30325014.zip  -d "SWST - EBC DEMO - FAC 6.1.x" --ip "10.0.0.1" > fac.csv

# For FAZ-VM:
./generate_csv.py -f FAZ-VM-BASE_30325016.zip -d "SWST - EBC DEMO - FAZ 6.4.x" -i 10.0.0.1 > faz.csv

# For FGT-VM:
./generate_csv.py -f FG-VMUL_30325017.zip -d "SWST - EBC DEMO FGT 6.4.x" --ip "" > fgt.csv

# For FMG-VM:
./generate_csv.py -f FMG-VM-BASE_30325015.zip -d "SWST - EBC DEMO - FMG 6.4.x" -i 10.0.0.1 > fmg.csv
````

# Register your licenses

We can just use the shell script `register.sh`:

```
$ ./register.sh -f fmg.csv
```

The script shell is taking care of saving the license file (when FortiCare
returns one) in a file named `<sn>.lic`.

# To add Service Entitlement on registered products?

## Generate the CSV file for the FortiGate VM licenses

```
$ ./generate_csv.py -f FG-VMUL_27228668.zip -i '' -d 'FG-VMUL: SD-WAN Orchestrator demo" > fgt.csv
```

## Generate the FortiGate VM licenses

```
$ ./register.sh -f fgt.csv
```

## Create a folder for all generated FortiGate VM licenses

```
$ mkdir fgt_licenses
```

## Move generated FortiGate VM licenses in this folder

```
$ mv FG*.lic fgt_licenses
```

## Generate the CSV file for the Service Entitlements

```
$ ./generate_csv.py -f FC-10-FVMUL-819-02-12_27237843.zip -i '' -d '365 Bundle: SD-WAN Orchestrator demo' -l fgt_licenses > fc.csv
```

Double check that all lines of this CSV is having a code (first field) and a
corresponding serial number (last field).

For instance:

```
[...]
0022TV383064,,365 Bundle: SD-WAN Orchestrator demo,FGVMULTM21223222
[...]
```

## Generate the Service Entitlements

```
$ ./register.sh -f fc.csv
```
