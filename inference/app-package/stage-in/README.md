# Stage-in
To test the inference module, the user must stage-in a sentinel-2 L1C data from the [https://dataspace.copernicus.eu](https://dataspace.copernicus.eu). The instruction for stage-in process is discussed below:

- Create an account on https://dataspace.copernicus.eu
- Edit the [usersetting.json](./usersettings.json) with your credentials:
```
{
    "Plugins": {
        "Terradue": {
            "Suppliers": {
                "CDS1": {
                    "Type": "Terradue.Stars.Data.Suppliers.DataHubSourceSupplier",
                    "ServiceUrl": "https://catalogue.dataspace.copernicus.eu/odata/v1",
                    "Priority": 1
                }
            }
        }
    },
    "Credentials": {
        "CDS1": {
            "AuthType": "basic",
            "UriPrefix": "https://identity.dataspace.copernicus.eu",
            "Username": "your registered email",
            "Password": "your password"
        }
    }
} 
```

- Change the product reference in [stage-in.sh](./stage-in.sh) with your desired Sentinel-2 L1C.
- Make the bash script executable:
```
chmod +x stage-in.sh
```
- Run it
```
./stage-in.sh
```