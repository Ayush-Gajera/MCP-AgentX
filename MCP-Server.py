import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ResultScraper:
    def __init__(self):
        self.url = "https://charusat.edu.in:912/UniExamResult/frmUniversityResult.aspx"
        self.session = requests.Session()
        
        # Configure the session with timeouts
        self.timeout = (5, 30)  # (connect timeout, read timeout) in seconds
        
        # Optional: Increase DNS cache time
        # This can help with DNS resolution issues
        socket.setdefaulttimeout(10)
    
    def extract_hidden_fields(self, soup):
        fields = {}
        for tag in soup.find_all("input", {"type": "hidden"}):
            fields[tag.get("name")] = tag.get("value", "")
        return fields
    
    def postback(self, soup, event_target, extra_data={}):
        """Helper to perform a __doPostBack-style request"""
        data = self.extract_hidden_fields(soup)
        data.update({
            "__EVENTTARGET": event_target,
            "__EVENTARGUMENT": "",
        })
        data.update(extra_data)
        
        try:
            return self.session.post(self.url, data=data, timeout=self.timeout)
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while performing postback to {event_target}")
            raise TimeoutError(f"Connection to the university server timed out during {event_target} request")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during postback to {event_target}: {str(e)}")
            if "NameResolutionError" in str(e):
                raise ConnectionError(f"Cannot resolve the university server address. Check your internet connection or DNS settings.")
            else:
                raise ConnectionError(f"Connection error: {str(e)}")
    
    def extract_student_info(self, soup):
        """Extract all student information from the result page"""
        student_info = {}
        
        # Find all span elements that might contain student info
        info_fields = {
            "uclGrd1_lblStudentName": "name",
            "lblEnrNo": "enrollment",
            "lblRegNo": "registration_number",
            "lblExamSchedule": "exam_schedule",
            "lblSGPA": "sgpa",  
            "lblCGPA": "cgpa",
            "lblTotalCredits": "total_credits",
            "lblProgram": "program",
            "lblSem": "semester",
            "lblInstitute": "institute"
        }
        
        for span_id, info_key in info_fields.items():
            span_element = soup.find("span", {"id": span_id})
            if span_element and span_element.text.strip():
                student_info[info_key] = span_element.text.strip()
        
        return student_info
    
    def get_result(self, institute_value, enrollment_no, degree_value, semester_value, exam_value):
        try:
            logger.info(f"Fetching result for enrollment: {enrollment_no}")
            
            # STEP 1: Load main page
            try:
                logger.info("Loading main page...")
                res = self.session.get(self.url, timeout=self.timeout)
                soup = BeautifulSoup(res.text, "html.parser")
            except requests.exceptions.Timeout:
                logger.error("Timeout while loading main page")
                return {
                    "success": False,
                    "error": "Connection to the university server timed out. Please try again later."
                }
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error while loading main page: {str(e)}")
                if "NameResolutionError" in str(e):
                    return {
                        "success": False,
                        "error": "Cannot resolve the university server address. Please check your internet connection and DNS settings."
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Connection error: {str(e)}"
                    }
            
            # STEP 2: Select Institute
            try:
                logger.info(f"Selecting institute: {institute_value}")
                res = self.postback(soup, "ddlInst", {"ddlInst": institute_value})
                soup = BeautifulSoup(res.text, "html.parser")
            except (TimeoutError, ConnectionError) as e:
                return {"success": False, "error": str(e)}
            
            # STEP 3: Select Degree
            try:
                logger.info(f"Selecting degree: {degree_value}")
                res = self.postback(soup, "ddlDegree", {
                    "ddlInst": institute_value,
                    "ddlDegree": degree_value
                })
                soup = BeautifulSoup(res.text, "html.parser")
            except (TimeoutError, ConnectionError) as e:
                return {"success": False, "error": str(e)}
            
            # STEP 4: Select Semester
            try:
                logger.info(f"Selecting semester: {semester_value}")
                res = self.postback(soup, "ddlSem", {
                    "ddlInst": institute_value,
                    "ddlDegree": degree_value,
                    "ddlSem": semester_value
                })
                soup = BeautifulSoup(res.text, "html.parser")
            except (TimeoutError, ConnectionError) as e:
                return {"success": False, "error": str(e)}
            
            # STEP 5: Select Exam Schedule
            try:
                logger.info(f"Selecting exam: {exam_value}")
                res = self.postback(soup, "ddlScheduleExam", {
                    "ddlInst": institute_value,
                    "ddlDegree": degree_value,
                    "ddlSem": semester_value,
                    "ddlScheduleExam": exam_value
                })
                soup = BeautifulSoup(res.text, "html.parser")
            except (TimeoutError, ConnectionError) as e:
                return {"success": False, "error": str(e)}
            
            # STEP 6: Submit Enrollment Number and Get Result
            try:
                logger.info(f"Submitting enrollment number: {enrollment_no}")
                final_data = self.extract_hidden_fields(soup)
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
                
                res = self.session.post(self.url, data=final_data, timeout=self.timeout)
                soup = BeautifulSoup(res.text, "html.parser")
            except requests.exceptions.Timeout:
                logger.error("Timeout while submitting enrollment number")
                return {
                    "success": False,
                    "error": "Connection to the university server timed out during result retrieval."
                }
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error during result retrieval: {str(e)}")
                return {
                    "success": False,
                    "error": f"Connection error during result retrieval: {str(e)}"
                }
            
            # STEP 7: Parse Result Table
            table = soup.find("table", {"id": "uclGrd1_grdResult"})
            table=str(table)

            student_info = self.extract_student_info(soup)
            if table:
                return {
                    "success": True,
                    "student_info": student_info,
                    "results": table
                }
            else:
                error_msg = soup.find("span", {"id": "lblmsg"})
                error_text = error_msg.text.strip() if error_msg and error_msg.text.strip() else "Result not found. Try again later or verify the details."
                logger.warning(f"Error fetching result: {error_text}")
                return {
                    "success": False,
                    "error": error_text
                }
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }

# Create a singleton instance
scraper = ResultScraper()

@app.route('/api/get_result', methods=['POST'])
def get_result():
    """API endpoint to fetch student results"""
    try:
        data = request.json
        
        # Validate required parameters
        required_params = ['institute', 'enrollment', 'degree', 'semester', 'exam']
        if not all(param in data for param in required_params):
            missing = [param for param in required_params if param not in data]
            return jsonify({
                "success": False,
                "error": f"Missing required parameters: {', '.join(missing)}"
            }), 400
        
        # Extract parameters
        institute = data['institute']
        enrollment = data['enrollment']
        degree = data['degree']
        semester = data['semester']
        exam = data['exam']
        
        # Get result
        result = scraper.get_result(institute, enrollment, degree, semester, exam)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"API error: {str(e)}"
        }), 500

@app.route('/api/test_connection', methods=['GET'])
def test_connection():
    """Test the connection to the university website"""
    try:
        response = requests.get("https://charusat.edu.in:912", timeout=5)
        return jsonify({
            "success": True,
            "status_code": response.status_code,
            "message": "Successfully connected to CHARUSAT server"
        })
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Connection timed out. The server might be slow or not responding."
        })
    except requests.exceptions.ConnectionError as e:
        if "NameResolutionError" in str(e):
            return jsonify({
                "success": False,
                "error": "Cannot resolve the university server address. Check your internet connection and DNS settings."
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Connection error: {str(e)}"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error: {str(e)}"
        })

@app.route('/api/info', methods=['GET'])
def get_info():
    """Return information about the API"""
    return jsonify({
        "name": "CHARUSAT University Result Scraper API",
        "version": "1.0.0",
        "description": "API for fetching student results from CHARUSAT University portal",
        "endpoints": [
            {
                "path": "/api/get_result",
                "method": "POST",
                "description": "Fetch student results",
                "params": {
                    "institute": "Institute code (e.g., '21' for DEPSTAR)",
                    "enrollment": "Student enrollment number (e.g., '22DCS018')",
                    "degree": "Degree code (e.g., '134' for BTECH(CS))",
                    "semester": "Semester number (e.g., '5')",
                    "exam": "Exam code (e.g., '7148' for NOVEMBER 2024)"
                }
            },
            {
                "path": "/api/test_connection",
                "method": "GET", 
                "description": "Test connection to the university server"
            }
        ]
    })

@app.route('/', methods=['GET'])
def home():
    """Basic homepage with instructions"""
    return """
    <html>
        <head>
            <title>CHARUSAT Result API</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
                .alert { padding: 15px; margin-bottom: 20px; border: 1px solid transparent; border-radius: 4px; }
                .alert-info { color: #31708f; background-color: #d9edf7; border-color: #bce8f1; }
            </style>
        </head>
        <body>
            <h1>CHARUSAT University Result API</h1>
            <p>This API allows you to fetch student results from the CHARUSAT University result portal.</p>
            
            <div class="alert alert-info">
                <strong>Connection Troubleshooting</strong>: If you're experiencing connection issues, 
                try the <code>/api/test_connection</code> endpoint first to verify connectivity to the university server.
            </div>
            
            <h2>Available Endpoints</h2>
            <ul>
                <li><code>/api/info</code> - Get API information</li>
                <li><code>/api/get_result</code> - Fetch student results (POST request)</li>
                <li><code>/api/test_connection</code> - Test connection to the university server</li>
            </ul>
            
            <h2>Example Usage</h2>
            <pre>
curl -X POST http://localhost:5000/api/get_result \\
     -H "Content-Type: application/json" \\
     -d '{
       "institute": "21",
       "enrollment": "22DCS018", 
       "degree": "134",
       "semester": "5",
       "exam": "7148"
     }'
            </pre>
        </body>
    </html>
    """

if __name__ == '__main__':
    logger.info("Starting MCP Server for Student Result Scraping")
    app.run(host='0.0.0.0', port=5000, debug=True)