import json, urllib.parse, urllib.request

API = "https://api.publicrecords.copyright.gov/search_service_external/"

def get(path, **q):  # the API refuses Python's default User-Agent
    req = urllib.request.Request(API + path + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "curl/8.0"})
    return json.load(urllib.request.urlopen(req))

hit = get("simple_search_dsl", query="TX0009613741", field_type="keyword", records_per_page=1, page_number=1)
rec = get("search_unique_record", query=hit["data"][0]["hit"]["public_records_id"])["data"][0]
rec = rec.get("hit", rec)
print(rec["title_concatenated"], "|", rec["material_excluded_statement"])
