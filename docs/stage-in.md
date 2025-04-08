# Stage-in

To test the inference module, the user must first **stage in Sentinel-2 L1C data** from [Copernicus Data Space](https://dataspace.copernicus.eu).

This is done by running a Bash script that uses the `Stars` tool to download and prepare the data.  
For more information on how `Stars` works, refer to its [official documentation](https://github.com/Terradue/Stars).

## For developers:
The user can stage-in a sentinel-2 L1C data using the instructions below:
1- Go to stage-in directory where a bash script is provided.
```
cd inference/app-package/stage-in/
```
2- Update the `usersettings.jaon` with your user name and password on [Copernicus Data Space](https://dataspace.copernicus.eu).
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
            "Username": "your_user_name",
            "Password": "your_password"
        }
    }
} 
```
3- Update the product reference in `stage-in.sh` with your desired product.

4- Make the bash script executable:
```
chmod +x stage-in.sh
```

5- Run the script.
```
./stage-in.sh
```