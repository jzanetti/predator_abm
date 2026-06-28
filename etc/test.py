import requests
import pandasdmx as sdmx
import io

url = "https://api.data.stats.govt.nz/rest/data/STATSNZ,HES_HES_003,1.0/2010+2007+2013+2016+2019.10+9+8+7+6+5+4+3+1+2.14+13+11+10+09+08+07+06+04+03+05+02+98+01.AV_WKLY_AMT?dimensionAtObservation=AllDimensions"
api_key = "8b72260631d74d9998b35f110478210d"  # Replace with your actual API key

headers = {
    "Ocp-Apim-Subscription-Key": api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    sdmx_msg = sdmx.read_sdmx(io.BytesIO(response.content))
    df = sdmx.to_pandas(sdmx_msg.data[0])
    df = df.to_frame().reset_index()
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}, Message: {response.text}")


import io
sdmx_msg = sdmx.read_sdmx(io.StringIO(response.content))