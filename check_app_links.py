import subprocess
import sys
import shlex
import os
import xml.etree.ElementTree as ET
import requests

APKANALYZER_LOCATION = "Android/Sdk/tools/bin/apkanalyzer"


def print_help():
    print("Usage: \ncheck_app_links [App_to_check_manifest]")


def get_intent_filters(node):
    nodes = []
    if node.tag == "intent-filter":
        nodes.append(node)
    if node.getchildren() is not None:
        for child in node.getchildren():
            nodes += get_intent_filters(child)
    return nodes


def main(location: str):
    cmd = location + " manifest print " + str(sys.argv[1])
    manifest = None
    try:
        manifest = subprocess.check_output(shlex.split(cmd)).decode()
    except OSError:
        print("Did you set the location for apkanalyzer correctly?\nIt comes preinstalled "
              "with Android Studio and it is usually in here: ~/Android/Sdk/tools/bin/apkanalyzer")
        sys.exit()
    if manifest is None:
        print("Manifest is empty. Exiting...")
        sys.exit()
    if "android:autoVerify=\"true\"" not in manifest:
        print("NOT VALID: Manifest has no AppLinks")
        sys.exit()
    root = ET.fromstring(manifest)
    filters = get_intent_filters(root)
    hosts = []
    for filter in filters:
        datas = filter.findall("data")
        scheme_http = False
        scheme_https = False
        res_hosts = []
        for data in datas:
            try:
                scheme = data.attrib["{http://schemas.android.com/apk/res/android}scheme"]
                if scheme == "http":
                    scheme_http = True
                elif scheme == "https":
                    scheme_https = True
            except KeyError:
                pass
            try:
                res_hosts.append(data.attrib["{http://schemas.android.com/apk/res/android}host"])
            except KeyError:
                pass
        if scheme_http:
            for host in res_hosts:
                hosts.append("http://" + host)
        if scheme_https:
            for host in res_hosts:
                hosts.append("https://" + host)
    hosts = list(set(hosts))
    print("App is responsible for the following URLS:", hosts)
    all_hosts_valid = True
    for host in hosts:
        r = requests.get(host + "/.well-known/assetlinks.json")
        if r.status_code != 200:
            all_hosts_valid = False
            print("Not valid for: " + host)
            break;
    if all_hosts_valid:
        print("VALID: Assetlinks file on all hosts")
    else:
        print("NOT VALID")
    

if __name__ == '__main__':
    location = os.path.join(os.path.expanduser("~"), APKANALYZER_LOCATION)
    if len(sys.argv) != 2:
        print_help()
    else:
        main(location)
