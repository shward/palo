#!/home/....../.virtualenvs/palo-cdl/bin/python

# ==============================================
#  Welcome to the Tool Palo Should Have Written™
# ==============================================
#
# Usage:
#   ./palo-edl-find.py -s 150.171.22.0/24,150.171.23.0/24,...
#
# Recommended Setup:
#   python3 -m venv ~/.virtualenvs/palo-cdl
#   source ~/.virtualenvs/palo-cdl/bin/activate
#   pip install requests beautifulsoup4
#   chmod +x palo-edl-find.py
#
# Make sure the shebang (first line) points to your venv’s python binary.
#

import requests
from bs4 import BeautifulSoup
import ipaddress
import os
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up CLI args
parser = argparse.ArgumentParser(description="Scan Palo EDLs for target subnets.")
parser.add_argument("-f", "--force", action="store_true", help="Force re-download of EDLs")
parser.add_argument("-4", "--ipv4-only", action="store_true", help="Only scan IPv4 EDLs")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
parser.add_argument("-s", "--subnets", required=True, help="Comma-separated list of CIDRs to search for")
args = parser.parse_args()

# Parse target subnets
try:
    target_subnets = [ipaddress.ip_network(s.strip()) for s in args.subnets.split(",") if s.strip()]
except ValueError as e:
    print(f"[ERROR] Invalid subnet in list: {e}")
    exit(1)

# Create a cache directory so we don’t DOS Palo’s fragile EDL servers (which probably run on the same box as their XML API)
os.makedirs("edls", exist_ok=True)

if args.verbose:
    print("[INFO] Downloading list of EDLs from Palo Alto’s documentation site. Because apparently this isn't automated.")
url = "https://docs.paloaltonetworks.com/resources/edl-hosting-service"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Gather all EDL URLs
edl_urls = sorted({
    a["href"] for a in soup.find_all("a", href=True)
    if "paloaltonetworks.com/feeds/" in a["href"]
})

if args.ipv4_only:
    edl_urls = [u for u in edl_urls if u.endswith("/ipv4")]
    print(f"[INFO] Found {len(edl_urls)} IPv4-only EDLs to scan. Because narrowing it down ourselves is our job now.")
else:
    print(f"[INFO] Found {len(edl_urls)} total EDLs to scan. Sit tight, this might take a bit.")

results = []

# Main workhorse: fetches and checks each EDL ... because apparently that’s our job now, not Palo’s
def process_edl(edl_url):
    filename = os.path.join("edls", edl_url.replace("https://", "").replace("/", "_"))
    fetch_new = args.force or not os.path.exists(filename) or (time.time() - os.path.getmtime(filename)) > 86400
    matched_subnets = set()

    try:
        if fetch_new:
            if args.verbose:
                print(f"[FETCH] {edl_url} (fresh from the internet ... you're welcome, Palo Alto)")
            edl_resp = requests.get(edl_url, timeout=10)
            if edl_resp.status_code == 200:
                with open(filename, "w") as f:
                    f.write(edl_resp.text)
            else:
                if args.verbose:
                    print(f"[WARN] Failed to fetch {edl_url} (HTTP {edl_resp.status_code})")
                return None
        else:
            if args.verbose:
                print(f"[FETCH] {edl_url} (using cached copy, because we’re efficient like that)")

        with open(filename, "r") as f:
            lines = f.read().splitlines()

        for line in lines:
            try:
                entry_net = ipaddress.ip_network(line.strip())
                for target in target_subnets:
                    if target.version == entry_net.version:
                        if target.subnet_of(entry_net) or entry_net.subnet_of(target):
                            matched_subnets.add(str(target))
            except ValueError:
                continue

        match_type = None
        if len(matched_subnets) == len(target_subnets):
            match_type = "FULL"
        elif matched_subnets:
            match_type = "PARTIAL"

        if match_type:
            return {
                "url": edl_url,
                "match_type": match_type,
                "matched_subnets": sorted(matched_subnets),
                "source": "fresh" if fetch_new else "cached"
            }

    except Exception as e:
        if args.verbose:
            print(f"[ERROR] Exception while processing {edl_url}: {e}")

    return None

# Let’s parallelize this ... 8 threads, because life’s too short to wait on Palo’s CDN
with ThreadPoolExecutor(max_workers=8) as executor:
    future_to_url = {executor.submit(process_edl, url): url for url in edl_urls}
    for future in as_completed(future_to_url):
        result = future.result()
        if result:
            results.append(result)

# Print a cheerful summary, or a depressing realization that you’re on your own
print("\n====== MATCH SUMMARY ======")
if results:
    for r in results:
        print(f"  [{r['match_type']}] {r['url']}  ({r['source']})")
        if args.verbose:
            print(f"    Matched: {', '.join(r['matched_subnets'])}")
else:
    print("No matches found. It's almost like Palo Alto should provide an easier way to answer this question.")

