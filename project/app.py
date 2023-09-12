from flask import Flask, render_template, request, redirect, url_for
from cs50 import SQL
import languages

person_in_call = {
    "name":"",
    "lang1":"",
    "lang2":"",
    "instaPage":""
}

def person_already_exist(name, pro_lang, amateur_lang):
    people = db.execute("SELECT * FROM person")

    for person in people:
        if person["name"] == name and person["knownLanguage"] == pro_lang:
            if person["wantedLanguage"] == amateur_lang:
                return True
    
    return False


def person_already_matched(name, pro_lang, amateur_lang):
    people = db.execute("SELECT * FROM person WHERE name = ? AND knownLanguage = ? AND wantedLanguage = ?", name, pro_lang, amateur_lang)
    if people and people[0]["match"] == "notFound":  # Check if people list is not empty
        return False
    
    return True



def get_finded_dict(searcher_dict):
    people = db.execute("SELECT * FROM person WHERE name = ? AND knownLanguage = ? AND wantedLanguage = ?", person_in_call["name"], person_in_call["lang1"], person_in_call["lang2"])

    list_of_person = db.execute("SELECT * FROM person WHERE name = ? ", people[0]["findedPerson"])

    for person in list_of_person:
        if(person["knownLanguage"] == person_in_call["lang2"]):
            return person



db = SQL("sqlite:///database.db")
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("homepage.html")


@app.route("/register")
def register():    
    return render_template("register.html", languages=languages.common_languages)


@app.route("/personal", methods=["GET", "POST"])
def personalized():
    if request.method == "POST":
        name = request.form.get("name").strip().upper()
        person_in_call["name"] = name

        lang1 = request.form.get("lang1")
        person_in_call["lang1"] = lang1

        lang2 = request.form.get("lang2")
        person_in_call["lang2"] = lang2

        account_name = request.form.get("account_name")
        person_in_call["instaPage"] = account_name

        if len(name) == 0 or len(account_name) == 0:
            return redirect(url_for("register"))
        elif lang1 not in languages.common_languages or lang2 not in languages.common_languages:
            return redirect(url_for("register"))  # Redirect if either dropdown option is not selected
        
        if person_already_exist(name, lang1, lang2) == False:
            db.execute("INSERT INTO person (name, knownLanguage, wantedLanguage, match, instaPage, findedPerson) VALUES (?, ?, ?, ?, ?, ?)", name, lang1, lang2, "notFound", account_name, "none")

        person = db.execute("SELECT * FROM person WHERE name = ? AND knownLanguage = ? AND wantedLanguage = ?", name, lang1, lang2)

        if person_already_matched(name, lang1, lang2) == True:
            finded_match = get_finded_dict(person_in_call)
            return render_template("showMatch.html", search_owner=person, finded_match=finded_match)
        
        else :
            return render_template("personalSearch.html", info=person)
    
    # For GET requests, simply render the form
    return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
def find_match():
    person = db.execute("SELECT * FROM person WHERE knownLanguage = ? AND wantedLanguage = ?", person_in_call["lang2"], person_in_call["lang1"])
    last = 0

    if len(person) == 0:
        return render_template("notFound.html")
    else:
        for i in range(len(person)):
            if person[i]["match"] == "Found":
                pass
            elif person[i]["match"] == "notFound":
                last = i
                break

        if person[last]["match"] == "Found":
            return render_template("notFound.html")

        db.execute("UPDATE person SET findedPerson = ? WHERE name = ?", person[last]["name"], person_in_call["name"])
        db.execute("UPDATE person SET findedPerson = ? WHERE name = ?", person_in_call["name"], person[last]["name"])

        #Delete users from database
        db.execute("UPDATE person SET match = ? WHERE name = ? AND knownLanguage = ? AND wantedLanguage = ?", "Found", person_in_call["name"], person_in_call["lang1"], person_in_call["lang2"])
        db.execute("UPDATE person SET match = ? WHERE name = ? AND knownLanguage = ?", "Found", person[last]["name"], person[last]["knownLanguage"])

        return render_template("showMatch.html", search_owner=person_in_call, finded_match=person[last])        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)


#request.args for get method and request.form for post method

