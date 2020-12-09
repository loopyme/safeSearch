from typing import List, Dict, Union

from safeSearch.query import (
    split_site_filter,
    merge_results,
    query, load_preset_sites,
)


def search(word: str, sites: Union[List, Dict] = None, multi_page: bool = True):
    """Split site filter conditions, query separately, then merge results
    to avoid long queries"""

    if isinstance(sites, dict):
        sites = list(sites.keys())
    query_words = split_site_filter(word, sites)

    res = []
    for i, query_word in enumerate(query_words):
        try:
            print(f"Querying({i}/{len(query_words)})")
            res.append(query(query_words[i]))
            if multi_page:
                for j in range(1, min(res[-1]["total"], 3)):
                    res.append(query(query_words[i], pn=j))

        except Exception as _:
            pass
    print(f"Merging results")
    query_result = merge_results(res)

    return query_result


if __name__ == '__main__':
    all_sites = load_preset_sites('./sites.yaml')
    sites = {}
    sites.update(all_sites["china_gov"])
    sites.update(all_sites["china_media"])

    wd = input("输入查询内容，然后回车\n>>> ")
    print(search(wd, sites))
