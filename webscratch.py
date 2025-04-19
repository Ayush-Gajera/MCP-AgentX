import requests
from bs4 import BeautifulSoup

# === CONFIGURATION ===
url = "https://charusat.edu.in:912/UniExamResult/frmUniversityResult.aspx"
session = requests.Session()

# === USER INPUT ===
institute_value = "21"        # DEPSTAR
enrollment_no = "22DCS018"    # Your Enrollment No
degree_value = "134"          # BTECH(CS)
semester_value = "5"          # Semester 5
exam_value = "7148"           # NOVEMBER 2024

# === HELPER ===
def extract_hidden_fields(soup):
    fields = {}
    for tag in soup.find_all("input", {"type": "hidden"}):
        fields[tag.get("name")] = tag.get("value", "")
    return fields

def postback(event_target, extra_data={}):
    """Helper to perform a __doPostBack-style request"""
    data = extract_hidden_fields(soup)
    data.update({
        "__EVENTTARGET": event_target,
        "__EVENTARGUMENT": "",
    })
    data.update(extra_data)
    return session.post(url, data=data)

# === STEP 1: Load main page ===
res = session.get(url)
soup = BeautifulSoup(res.text, "lxml")

# === STEP 2: Select Institute ===
res = postback("ddlInst", {"ddlInst": institute_value})
soup = BeautifulSoup(res.text, "lxml")

# === STEP 3: Select Degree ===
res = postback("ddlDegree", {
    "ddlInst": institute_value,
    "ddlDegree": degree_value
})
soup = BeautifulSoup(res.text, "lxml")

# === STEP 4: Select Semester ===
res = postback("ddlSem", {
    "ddlInst": institute_value,
    "ddlDegree": degree_value,
    "ddlSem": semester_value
})
soup = BeautifulSoup(res.text, "lxml")

# === STEP 5: Select Exam Schedule ===
res = postback("ddlScheduleExam", {
    "ddlInst": institute_value,
    "ddlDegree": degree_value,
    "ddlSem": semester_value,
    "ddlScheduleExam": exam_value
})
soup = BeautifulSoup(res.text, "lxml")

# === STEP 6: Submit Enrollment Number and Get Result ===
final_data = extract_hidden_fields(soup)
final_data.update({
    "ddlInst": institute_value,
    "ddlDegree": degree_value,
    "ddlSem": semester_value,
    "ddlScheduleExam": exam_value,
    "txtEnrNo": enrollment_no,
    "btnSearch": "Show Marksheet",
    "__EVENTTARGET": "btnSearch",
    "__EVENTARGUMENT": ""
})

res = session.post(url, data=final_data)
soup = BeautifulSoup(res.text, "lxml")
print(soup)
# === STEP 7: Parse Result Table ===
result_table = soup.find("table", {"id": "uclGrd1_grdResult"})

if result_table:
    print("\n✅ Result Found:\n")
    for row in result_table.find_all("tr"):
        cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
        print(" | ".join(cols))
else:
    error_msg = soup.find("span", {"id": "lblmsg"})
    if error_msg:
        print("❌", error_msg.text.strip())
    else:
        print("❌ Result not found. Try again later or verify the details.")
