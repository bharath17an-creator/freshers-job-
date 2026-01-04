
from flask import Flask, render_template, request, redirect, session, url_for
import os, re
import PyPDF2
import docx

app = Flask(__name__)
app.secret_key = "skill_first_platform"

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS = {"student@gmail.com": "student123"}

SKILLS = ["python","java","sql","html","css","javascript","flask","django","react","data analysis","machine learning"]

COMPANY_CAREERS = {
    "Google": "https://careers.google.com/jobs",
    "Microsoft": "https://careers.microsoft.com",
    "Infosys": "https://www.infosys.com/careers",
    "TCS": "https://www.tcs.com/careers"
}

COMPANY_SKILLS = {
    "Google": ["python","sql","data analysis"],
    "Microsoft": ["python","javascript","sql"],
    "Infosys": ["java","sql","html","css"],
    "TCS": ["python","java","sql"]
}

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if USERS.get(request.form["email"]) == request.form["password"]:
            session["user"] = request.form["email"]
            return redirect("/dashboard")
        return "Invalid Credentials"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session:
        return redirect("/")
    if request.method == "POST":
        file = request.files["resume"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        return redirect(url_for("analyze", filename=file.filename))
    return render_template("upload.html")

def read_resume(path):
    text = ""
    if path.endswith(".pdf"):
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    elif path.endswith(".docx"):
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text + " "
    return text.lower()

def extract_skills(text):
    return [s for s in SKILLS if re.search(rf"\b{s}\b", text)]

def match_companies(user_skills):
    matched = []
    for company, skills in COMPANY_SKILLS.items():
        percent = len(set(user_skills) & set(skills)) / len(skills) * 100
        if percent >= 85:
            matched.append({
                "company": company,
                "match": round(percent),
                "url": COMPANY_CAREERS[company]
            })
    return matched

@app.route("/analyze/<filename>")
def analyze(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    text = read_resume(path)
    skills = extract_skills(text)
    companies = match_companies(skills)
    return render_template("results.html", skills=skills, companies=companies)

@app.route("/internships")
def internships():
    internships = [
        {"company":"StartupHub","role":"Python Intern","stipend":"₹10,000","duration":"3 Months","process":"Skill Task"},
        {"company":"TechLabs","role":"Web Intern","stipend":"₹8,000","duration":"2 Months","process":"Mini Project"}
    ]
    return render_template("internships.html", internships=internships)

@app.route("/projects")
def projects():
    projects = [
        {"company":"FinTech","task":"Flask API","skills":"Python, Flask","selection":"Best performer hired"},
        {"company":"EdTech","task":"Landing Page","skills":"HTML, CSS","selection":"UI based hiring"}
    ]
    return render_template("projects.html", projects=projects)

if __name__ == "__main__":
    app.run(debug=True)
