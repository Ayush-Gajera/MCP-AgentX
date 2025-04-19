from mcp.server.fastmcp import FastMCP
import time
import signal
import sys
import requests
# import requests
from bs4 import BeautifulSoup

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    print("Shutting down server gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create an MCP server with increased timeout
mcp = FastMCP(
    name="find_result",
    host="127.0.0.1",
    port=5000,
    # Add this to make the server more resilient
    timeout=30  # Increase timeout to 30 seconds
)

# Define our tool
@mcp.tool() 
def fetch_result(enrollment_no)-> str:
    url = "https://charusat.edu.in:912/UniExamResult/frmUniversityResult.aspx"
    session = requests.Session()
    institute_value = "21"        # DEPSTAR    # Your Enrollment No
    degree_value = "134"          # BTECH(CS)
    semester_value = "5"          # Semester 5
    exam_value = "7148"  
    def extract_hidden_fields(soup):
        return {tag.get("name"): tag.get("value", "") for tag in soup.find_all("input", {"type": "hidden"})}

    def postback(event_target, extra_data={}):
        data = extract_hidden_fields(soup)
        data.update({
            "__EVENTTARGET": event_target,
            "__EVENTARGUMENT": "",
        })
        data.update(extra_data)
        return session.post(url, data=data)

    # Load main page
    res = session.get(url)
    soup = BeautifulSoup(res.text, "lxml")

    # Select Institute
    res = postback("ddlInst", {"ddlInst": institute_value})
    soup = BeautifulSoup(res.text, "lxml")

    # Select Degree
    res = postback("ddlDegree", {
        "ddlInst": institute_value,
        "ddlDegree": degree_value
    })
    soup = BeautifulSoup(res.text, "lxml")

    # Select Semester
    res = postback("ddlSem", {
        "ddlInst": institute_value,
        "ddlDegree": degree_value,
        "ddlSem": semester_value
    })
    soup = BeautifulSoup(res.text, "lxml")

    # Select Exam Schedule
    res = postback("ddlScheduleExam", {
        "ddlInst": institute_value,
        "ddlDegree": degree_value,
        "ddlSem": semester_value,
        "ddlScheduleExam": exam_value
    })
    soup = BeautifulSoup(res.text, "lxml")

    # Submit Enrollment Number
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

    # Parse result
    result_table = soup.find("table", {"id": "uclGrd1_grdResult"})
    if result_table:
        return result_table     
    else:
        error_msg = soup.find("span", {"id": "lblmsg"})
        return f"❌ {error_msg.text.strip()}" if error_msg else "❌ Result not found."

    # Example usage
    result = fetch_charusat_result("21", "22DCS018", "134", "5", "7148")
    if isinstance(result, list):
        for row in result:
            print(" | ".join(row))
    else:
        print(result)


if __name__ == "__main__":
    try:
        print("Starting MCP server 'count-r' on 127.0.0.1:5000")
        # Use this approach to keep the server running
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
        # Sleep before exiting to give time for error logs
        time.sleep(5)