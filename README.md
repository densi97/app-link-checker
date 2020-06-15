# app-link-checker
Many android apps still lack the verification of the app links. If this verification is missing, serious attacks can be carried out against the users. Therefore it is crucial to protect your app against these attack by simply putting the `assetlinks.json` file inside the `.well-known` directory on your webserver.

This script extracts all domains from the APK's manifest and checks if **all** claimed http and https schemes have an assetlink. Only if this file is present on all schemes, Android will store it as verified.


### Usage
`python3 check_app_links.py <name_of_apk>`

