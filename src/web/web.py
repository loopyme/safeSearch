from flask import Flask, render_template, request

from safeSearch.main import search
from safeSearch.query import load_preset_sites
from safeSearch.render import format_by_time

app = Flask(__name__)

preset_sites = r"--PATH-HERE--"


@app.route("/")
def index():
    all_sites = load_preset_sites(preset_sites)
    sites = {}
    sites.update(all_sites["china_gov"])
    sites.update(all_sites["china_media"])

    wd = request.args.get("search")
    pn = request.args.get("pn")
    if wd:
        return render_template(
            "result.html", all_result=format_by_time(search(wd, sites, pn))
        )
    else:
        return render_template("search.html", sites=sites)


if __name__ == "__main__":
    app.run(debug=True)
