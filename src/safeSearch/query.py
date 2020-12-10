import re
from time import time
from typing import List, Dict, Union, Iterator

import yaml
from baiduspider import BaiduSpider, ParseError

from safeSearch.error import QueryTooLongException

SPIDER = BaiduSpider()
LAST_QUERY_TIME = time()


# def build_baidu_url(word: str, sites: list = None) -> str:
#     base_url = "https://www.baidu.com/s?wd={wd}".format(wd=word)
#     site_filter = " site:(" + " | ".join(sites) + ")" if sites else ""
#
#     return base_url + site_filter


# def build_google_url(word: str, sites: list = None) -> str:
#     base_url = "https://www.google.com/search?q={q}".format(q=word)
#     site_filter = "+inurl:(+" + "+|+".join(sites) + ")" if sites else ""
#
#     return base_url + site_filter


def split_site_filter(word: str, site: list = None) -> List[str]:
    """Used to recursively split site filter conditions to avoid long query"""

    last_valid_query = ""
    for i in range(len(site)):
        if i == 0:
            site_filter = " site:{}".format(site[i])
        else:
            site_filter = " site:(" + " | ".join(site[:i]) + ")"

        if is_valid_query(word + site_filter):
            last_valid_query = word + site_filter
        else:
            if not last_valid_query:
                raise QueryTooLongException(word)
            else:
                return [last_valid_query] + split_site_filter(word, site[i:])
    return [last_valid_query]


def is_valid_query(s: str) -> bool:
    """Check string length to avoid Baidu's query length limit"""
    return len(s.encode("gbk")) / 2 < 39


def load_preset_sites(path: str = "./sites.yaml") -> Dict[str, List[str]]:
    """Load yaml file to get preset sites"""
    with open(path, encoding="utf-8") as f:
        sites = yaml.load(f, Loader=yaml.SafeLoader)
    return sites


def merge_results(
        query_results: Union[List[Dict], Iterator[Dict]],
        deduplicate: bool = True,
        sort_by_time: bool = True,
) -> List[Dict]:
    """Merge the query results from multiple queries, see query_results structure in `BaiduSpider` doc"""
    merged_result = [
        res for q in query_results for res in q["results"] if "url" in res.keys()
    ]

    if deduplicate:
        des_set = set()
        merged_result_deduplicate = []
        for res in merged_result:
            try:
                des = re.sub("[^\u4E00-\u9FA5]", "", res["des"])
            except TypeError as _:
                continue
            if des not in des_set:
                des_set.add(des)
                merged_result_deduplicate.append(res)
        merged_result = merged_result_deduplicate

    if sort_by_time:
        merged_result = sorted(
            merged_result, key=lambda res: date_to_num(res["time"]), reverse=True
        )
    return merged_result


def query(word: str, **kwargs) -> Dict:
    """Do query with SPIDER.search_web"""
    global LAST_QUERY_TIME
    try:
        result = SPIDER.search_web(word, **kwargs)
    except ParseError as _:
        return {"results": {}}
    print(word, kwargs)
    # if time() < LAST_QUERY_TIME + 3:
    #     LAST_QUERY_TIME = time()
    #     sleep(3)
    # else:
    #     LAST_QUERY_TIME = time()
    return result


def date_to_num(date: str) -> int:
    """In order to sort, make 2019年12月31日 -> 20191231"""
    try:
        if "天" in date:  # n天前
            num = 2222222222 - int(date[0]) * 10000
        elif "小时" in date:  # n小时前
            num = 2222222222 - int(date[:-3]) * 100
        elif "分钟" in date:  # n分钟
            num = 2222222222 - int(date[:-2])
        else:
            num = int("".join(map(lambda x: x.zfill(2), re.split(r"年|月|日", date))))
    except Exception as _:
        num = 0
    return num
