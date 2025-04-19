# MCP ResultAgentX 🧠🤖

This project is a powerful backend service that *fetches academic results* from a university web portal. It leverages the *Model Context Protocol (MCP)* to structure how data is retrieved and interacted with claude AI, and uses Python libraries like *BeautifulSoup* for scraping and *FastMCP* for rapid deployment.

> ⚡ Built using Claude Desktop + webscrap for real-time student data access.

---

## 🌐 Project Overview

*Scrape results* from the university portal using BeautifulSoup  
*FastMCP server* to handle client requests (MCP-compliant)  
*Parse raw HTML table* into clean, structured tabular data  
*Send results to Claude AI* for analysis (performance trends, grade predictions, etc.)  

---

## 📸 Demo Preview

🎬 [Click here to watch demo video](#) (upload link later)

---

## 📦 Technologies Used

- 🐍 Python
- 🍲 BeautifulSoup – for parsing HTML result tables
- ⚡ FastMCP – for efficient, lightweight server setup
- ☁ Cloud AI – for high-level insights (e.g., grade prediction, performance heatmap)
- 🧠 MCP – to bridge LLMs and data sources in a structured way


## Setup

1. Clone this repository

bash
git clone [https://github.com/Ayush-Gajera/MCP-ResultAgentX.git](https://github.com/Ayush-Gajera/MCP-ResultAgentX)
cd mcp-result-fetcher 


2. Copy config context
- Open the file claude_desktop_config.json located in the repo and copy its entire content.

3. Install Claude Desktop
- If you haven't already, download and install Claude Desktop.

4. Configure Claude Desktop

- Open Claude Desktop
- Go to: File > Settings > Developer
- Paste the copied config into claude_desktop_config.json
- Save the settings

5. Restart Claude Desktop

- Uninstall Claude Desktop
- Reinstall it again (yes, this step is required)

6. Open Claude Desktop again
- You will now see the MCP Tool integrated just below the AI text box in Claude Desktop. Use it to fetch and analyze student results directly.

## 🔥 Sample Prompts

text
1. Get semester 4 result of enrollment number 22DCS018
2. Compare result of 22DCS018 and 22DCS03
3. Predict SGPA for next semester
