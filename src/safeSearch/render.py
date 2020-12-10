def format_by_time(result):
    result_sorted = {}
    pre_date, pre_position = "", ""
    for i, r in enumerate(result):

        # handle date
        if not r["time"]:
            year = "未知"
            r["date"] = "未知"
        elif "小时" in r["time"]:
            year = "一天内"
            r["date"] = r["time"]
        elif "天" in r["time"]:
            year = "一周内"
            r["date"] = r["time"]
        elif "分钟" in r["time"]:
            year = "一小时内"
            r["date"] = r["time"]
        else:
            year = r["time"][:4]
            r["date"] = r["time"][5:]

        # website in same day shares the same position
        if r["date"] != pre_date:
            pre_date = r["date"]
            pre_position = "right" if pre_position == "left" else "left"
            r["position"] = pre_position
        else:
            r["position"] = pre_position

        # add to timeline
        if year in result_sorted.keys():
            result_sorted[year].append(r)
        else:
            result_sorted[year] = [r]
    return result_sorted
