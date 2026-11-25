# SalesPilot AI -- Autonomous AI Sales Voice Agent

## Implementation Plan

**Project type:** Individual functional MVP / prototype\
**Purpose:** Demonstrate an AI-powered sales assistant that can conduct
a customer conversation, answer company-related questions, qualify
leads, request appointments, and save the interaction in a simple CRM.

------------------------------------------------------------------------

## 1. Project Overview

### 1.1 Problem Statement

Businesses receive many sales enquiries and spend time understanding
customer requirements, answering repeated questions, qualifying
potential customers, arranging meetings, and maintaining customer
records. Handling these activities manually can be time-consuming and
inconsistent.

### 1.2 Proposed Solution

**SalesPilot AI** is a browser-based AI sales assistant. A customer can
speak to it or type a message. The system converts speech into text,
processes the conversation using an AI model, retrieves relevant company
information, identifies customer requirements, classifies the lead, and
records appointment requests.

The prototype will demonstrate one complete business workflow. It will
use browser-based voice capabilities rather than connecting to a real
telephone network. Telephony integration can be described as a future
enhancement.

### 1.3 Main Demonstration Goal

Demonstrate the following end-to-end workflow:

1.  A customer starts a conversation using voice or text.
2.  The AI greets the customer and asks about their requirements.
3.  The customer asks a question about the company or its services.
4.  The system retrieves relevant information from a company knowledge
    document.
5.  The AI collects relevant lead details such as name, business type,
    requirement, and budget.
6.  The system classifies the lead as Hot, Warm, or Cold and identifies
    sentiment.
7.  The customer requests an appointment.
8.  The appointment request and lead details are saved in the database.
9.  The system generates a conversation summary.
10. The CRM dashboard displays the saved lead and appointment
    information.

------------------------------------------------------------------------

## 2. Scope and Features

The project should remain simple and focused. Implement the core
features below instead of attempting to build a complete commercial
calling platform.

  -----------------------------------------------------------------------
  Feature                             MVP implementation
  ----------------------------------- -----------------------------------
  Speech-to-Text (STT)                Browser Web Speech API converts the
                                      customer's speech into text.

  Text-to-Speech (TTS)                Browser SpeechSynthesis API reads
                                      the AI response aloud.

  Contextual conversation             Keep the messages from the current
                                      conversation and send relevant
                                      history to the AI model.

  Multilingual communication          Allow the customer to select a
                                      supported language and instruct the
                                      AI to respond in that language.

  RAG knowledge retrieval             Retrieve relevant passages from a
                                      company knowledge document and
                                      provide them to the AI as context.

  Lead qualification                  Extract customer details and
                                      classify the lead as Hot, Warm, or
                                      Cold.

  Sentiment analysis                  Identify the customer's sentiment
                                      as Positive, Neutral, or Negative.

  Appointment booking                 Collect a preferred date and time
                                      and save an appointment request.

  CRM integration                     Save lead and appointment records
                                      in SQLite and display them in a
                                      dashboard.

  Call summary                        Generate a short summary of the
                                      conversation and key customer
                                      requirements.

  Business insights                   Display basic counts of leads, lead
                                      categories, sentiment, and
                                      appointment requests.
  -----------------------------------------------------------------------

**Scope clarification:** Browser voice interaction is a prototype of a
voice agent. It is not the same as inbound/outbound telephone calling.
Real telephony can be integrated later through a provider such as
Twilio, Vapi, or Retell.

------------------------------------------------------------------------

## 3. Technology Stack

  -----------------------------------------------------------------------
  Layer                   Recommended technology  Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                HTML, CSS, JavaScript   Chat interface,
                                                  microphone controls,
                                                  voice playback, and
                                                  dashboard

  Backend                 Python + FastAPI        API endpoints and
                                                  application workflow

  AI model                Gemini API              Conversation responses,
                                                  extraction,
                                                  classification, and
                                                  summaries

  Speech-to-Text          Browser Web Speech API  Convert spoken input
                                                  into text

  Text-to-Speech          Browser SpeechSynthesis Read AI responses aloud
                          API                     

  RAG                     Sentence Transformers + Find relevant company
                          FAISS                   information

  Database                SQLite                  Store leads,
                                                  appointments, and
                                                  conversation summaries

  Charts                  Chart.js                Display basic business
                                                  insights

  Version control         Git + GitHub            Source code and project
                                                  submission
  -----------------------------------------------------------------------

Use free or open-source components where possible. API free-tier
availability and usage limits may change, so check the provider's
current limits before the demonstration. Keep a text-input fallback in
case browser speech recognition is unavailable.

------------------------------------------------------------------------

## 4. System Architecture

``` text
                  CUSTOMER
             (Voice or Text Input)
                       |
                       v
            FRONTEND: HTML/CSS/JS
          - Microphone and text input
          - Conversation display
          - Spoken AI response
                       |
                       v
                FASTAPI BACKEND
                       |
                       v
                 AI AGENT
                 (Gemini API)
                       |
          +------------+-------------+
          |            |             |
          v            v             v
     Conversation     RAG         Lead Analysis
       Memory       Retrieval     - Details
                    - Company     - Lead score
                      knowledge   - Sentiment
          |            |             |
          +------------+-------------+
                       |
                       v
                TOOL EXECUTION
            - Save/update lead
            - Create appointment request
            - Generate conversation summary
                       |
                       v
                SQLITE DATABASE
                       |
                       v
                CRM DASHBOARD
          - Leads and classifications
          - Appointment requests
          - Conversation summaries
          - Basic business insights
```

### 4.1 Component Responsibilities

-   **Frontend:** Captures customer input, displays the conversation,
    and speaks the AI response.
-   **FastAPI backend:** Receives requests, manages the workflow, calls
    the AI model, and communicates with the database.
-   **AI agent:** Understands the conversation, generates responses, and
    decides when information or an action is needed.
-   **Conversation memory:** Retains the current session's conversation
    history so the assistant can respond with context.
-   **RAG module:** Finds relevant information in the company knowledge
    document.
-   **Lead qualification module:** Extracts customer details and assigns
    a lead category.
-   **Booking module:** Validates and stores appointment requests.
-   **Database:** Stores leads, appointments, and summaries.
-   **Dashboard:** Displays the saved records and basic metrics.

------------------------------------------------------------------------

## 5. End-to-End Business Workflow

Use a fictional or clearly labelled demonstration company profile and
sample service information in `data/company_knowledge.txt`.

### Example interaction

**AI Agent:** Hello! Welcome. How can I help you today?

**Customer:** I am looking for an AI automation solution for my
business.

**AI Agent:** Certainly. What type of business do you operate, and which
process would you like to automate?

**Customer:** I run an e-commerce business. My budget is around ₹50,000.

**AI Agent:** Thank you. I can help you understand the available
automation solutions. Would you like to schedule a product
demonstration?

**Customer:** Yes, I would prefer tomorrow at 11 AM.

**AI Agent:** I have recorded your appointment request. The sales team
can confirm the meeting.

### Expected CRM record

  Field                 Example value
  --------------------- -------------------------------------------
  Customer name         Name provided during the conversation
  Business type         E-commerce
  Requirement           AI automation
  Budget                ₹50,000
  Lead category         Hot / Warm / Cold, based on defined rules
  Sentiment             Positive / Neutral / Negative
  Appointment request   Requested date and time
  Summary               Short summary of customer needs

The application must save the record in SQLite and display it in the
dashboard. Do not present an appointment as confirmed unless the
application actually checks availability and confirms it.

------------------------------------------------------------------------

## 6. Development Plan

Build the project in the following order. First make the backend
workflow work, then connect the frontend and add voice features.

### Phase 1 -- Project Setup

-   Create the project folder and Python virtual environment.
-   Install FastAPI and the required dependencies.
-   Create the frontend and backend folders.
-   Add configuration for the AI API key using environment variables.
-   Create `.gitignore` so secrets and local environment files are not
    uploaded.

**Deliverable:** Project runs locally and the FastAPI server starts
successfully.

### Phase 2 -- AI Conversation

-   Create an endpoint that accepts a customer message.
-   Connect the backend to the selected AI model.
-   Write a system prompt that defines the sales assistant's role.
-   Ask the assistant to collect customer requirements naturally.
-   Maintain conversation history for the current session.

**Deliverable:** A working text-based sales assistant with contextual
responses.

### Phase 3 -- Company Knowledge and RAG

-   Create `data/company_knowledge.txt`.
-   Add company overview, services, common questions, and relevant
    product information.
-   Split the document into manageable text chunks.
-   Generate embeddings using Sentence Transformers.
-   Store/search the embeddings using FAISS.
-   Retrieve relevant chunks for a customer question.
-   Pass retrieved content to the AI model as reference material.

**Deliverable:** The assistant can answer company-related questions
using the supplied knowledge document. If the answer is not in the
knowledge base, it should say that it does not have enough information
rather than inventing details.

### Phase 4 -- Lead Qualification and Sentiment

-   Extract available customer details from the conversation.
-   Capture name, business type, requirement, budget, and contact
    details when provided.
-   Define simple, explainable Hot/Warm/Cold qualification rules.
-   Ask the AI model to identify sentiment as Positive, Neutral, or
    Negative.
-   Validate the returned structured data before saving it.

**Deliverable:** Each conversation can produce a structured lead record
and sentiment label.

### Phase 5 -- Database and Appointment Booking

-   Create SQLite tables for leads and appointments.
-   Add backend functions to create and retrieve records.
-   Ask for a preferred appointment date and time.
-   Validate that required appointment details are present.
-   Save the appointment as a request.
-   Display its status in the CRM.

**Deliverable:** Lead and appointment information persists after the
application is restarted.

### Phase 6 -- Voice Interaction

-   Add browser microphone input using the Web Speech API.
-   Convert recognised speech into text and send it to the backend.
-   Display the recognised text in the conversation.
-   Read the AI response using SpeechSynthesis.
-   Add controls to start/stop listening and replay a response.
-   Keep a normal text input as a fallback.

**Deliverable:** A customer can complete the demonstration conversation
using browser voice or text.

### Phase 7 -- Summary and CRM Dashboard

-   Generate a short conversation summary.
-   Show customer details, requirement, lead category, sentiment, and
    appointment request.
-   Display all saved leads in a table.
-   Add simple counts or charts for lead categories and sentiment.
-   Provide a way to inspect an individual lead's summary.

**Deliverable:** A simple dashboard that demonstrates how the sales team
can use the information collected by the agent.

### Phase 8 -- Testing and GitHub Submission

-   Test the complete workflow from first message to saved CRM record.
-   Test missing or incomplete customer details.
-   Test a question that is not answered by the knowledge document.
-   Test invalid appointment input.
-   Test text input if microphone recognition fails.
-   Check that API keys are not present in source files or Git history.
-   Add screenshots, architecture diagram, setup instructions, and
    one-page report to GitHub.

**Deliverable:** A working MVP with a clear repository and
demonstration-ready workflow.

------------------------------------------------------------------------

## 7. Suggested Project Structure

``` text
SalesPilot-AI/
|
|-- backend/
|   |-- main.py
|   |-- agent.py
|   |-- rag.py
|   |-- lead_qualification.py
|   |-- booking.py
|   |-- database.py
|
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- script.js
|
|-- data/
|   |-- company_knowledge.txt
|
|-- docs/
|   |-- architecture.png
|
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- README.md
|-- PROJECT_REPORT.md
```

Keep each Python module responsible for one task. Avoid adding
frameworks or services that are not needed for the MVP.

------------------------------------------------------------------------

## 8. API and Module Responsibilities

A simple initial API design could be:

  -----------------------------------------------------------------------
  Endpoint                Method                  Responsibility
  ----------------------- ----------------------- -----------------------
  `/chat`                 POST                    Process a customer
                                                  message and return the
                                                  AI response

  `/leads`                GET                     Retrieve saved leads

  `/leads`                POST                    Save or update a lead

  `/appointments`         GET                     Retrieve appointment
                                                  requests

  `/appointments`         POST                    Create an appointment
                                                  request

  `/summary`              POST                    Generate a conversation
                                                  summary

  `/insights`             GET                     Return basic dashboard
                                                  metrics
  -----------------------------------------------------------------------

These are proposed endpoints for the implementation; adjust them if the
final code uses a simpler structure.

------------------------------------------------------------------------

## 9. Scalability Strategy for 1,00,000 Users

The MVP will run locally and use SQLite. Explain how it could evolve for
a larger production deployment.

1.  **Application layer:** Deploy multiple FastAPI instances behind a
    load balancer.
2.  **Database:** Move from SQLite to PostgreSQL and use connection
    pooling.
3.  **Session and cache layer:** Use Redis for temporary conversation
    state and caching.
4.  **RAG layer:** Use a scalable vector database when the knowledge
    base and traffic grow.
5.  **Background processing:** Use a task queue for summaries,
    analytics, and other longer-running work.
6.  **AI services:** Apply rate limits, retries, timeouts, and usage
    monitoring to model APIs.
7.  **Voice infrastructure:** Use a dedicated telephony/voice provider
    for real phone calls and scale based on concurrent calls.
8.  **Monitoring:** Track latency, failures, API usage, and resource
    consumption.

**Important distinction:** 1,00,000 registered users does not mean
1,00,000 simultaneous calls. Capacity planning should be based on peak
concurrent sessions, average call duration, request volume, and model
latency. Do not claim that the local MVP has already been load-tested
for 1,00,000 users.

------------------------------------------------------------------------

## 10. Data Security and Reliability

For the prototype and the proposed production design:

-   Store API keys in environment variables; never commit `.env`.
-   Validate and sanitise user input.
-   Do not collect personal information that is not needed for the
    demonstration.
-   Restrict access to lead and appointment records.
-   Use authentication and role-based access in a production CRM.
-   Use HTTPS for deployed application traffic.
-   Avoid logging API keys or unnecessary sensitive conversation
    content.
-   Add error handling for API failures and speech recognition failures.
-   Provide a text-input fallback if microphone support is unavailable.
-   Tell users when a conversation is being recorded or stored, where
    applicable.

------------------------------------------------------------------------

## 11. Infrastructure and Cost Considerations

The MVP should use local development and free/open-source components
wherever practical.

  -----------------------------------------------------------------------
  Component               MVP approach            Cost consideration
  ----------------------- ----------------------- -----------------------
  Frontend/backend        Run locally             No hosting cost during
                                                  local demo

  Database                SQLite                  Open source

  RAG                     Sentence Transformers + Open source; local
                          FAISS                   compute required

  Voice                   Browser speech APIs     Browser support and
                                                  usage limitations apply

  LLM                     Gemini API or another   Check current free-tier
                          available model API     limits; paid usage may
                                                  apply

  Dashboard               Chart.js                Open source

  Deployment              Optional free-tier      Free tiers have limits
                          hosting                 and may change
  -----------------------------------------------------------------------

Do not promise that production operation is free. A commercial
deployment will incur costs for hosting, databases, model/API usage,
voice minutes, monitoring, and storage. Estimate production costs only
after defining expected usage and concurrency.

------------------------------------------------------------------------

## 12. Commercial Feasibility

SalesPilot AI could be useful to businesses that receive repeated
enquiries and need a structured way to follow up with potential
customers.

Potential business value:

-   Reduces repetitive first-level enquiry handling.
-   Collects lead information in a consistent format.
-   Helps sales teams prioritise promising leads.
-   Keeps appointment requests and conversation summaries organised.
-   Can operate outside normal business hours if deployed with suitable
    infrastructure.

Potential limitations:

-   AI responses need monitoring to avoid incorrect claims.
-   Voice quality and latency depend on browser, network, and model
    performance.
-   Real phone calls require telephony integration.
-   Production use requires privacy, security, reliability, and cost
    controls.

Possible commercial models include a monthly subscription based on
usage, number of agents, or number of handled conversations. This is a
proposed business model, not a validated revenue forecast.

------------------------------------------------------------------------

## 13. Testing Checklist

Before the technical discussion, verify the following:

-   [ ] Backend starts without errors.
-   [ ] Customer can send a text message.
-   [ ] AI responds to the message.
-   [ ] AI remembers earlier messages in the same conversation.
-   [ ] Company-related questions use retrieved knowledge.
-   [ ] Unknown questions are not answered with invented company facts.
-   [ ] Customer details can be extracted.
-   [ ] Lead is classified as Hot, Warm, or Cold.
-   [ ] Sentiment is displayed.
-   [ ] Appointment request can be saved.
-   [ ] Lead and appointment records appear in the dashboard.
-   [ ] Conversation summary is generated.
-   [ ] Voice input works in the demonstration browser, or text fallback
    is available.
-   [ ] AI response can be spoken aloud.
-   [ ] API key is not committed to GitHub.
-   [ ] README contains setup and run instructions.
-   [ ] Architecture diagram and one-page report are in the repository.

------------------------------------------------------------------------

## 14. Technical Discussion Preparation

Be prepared to explain:

1.  Why did you choose FastAPI and Python?
2.  What is the role of the LLM in the sales workflow?
3.  How does the application retain conversation context?
4.  What is RAG, and why is it useful for company-specific answers?
5.  How are lead category and sentiment determined?
6.  How does the application save an appointment?
7.  What happens if the customer gives incomplete information?
8.  How would you connect the prototype to a real telephony provider?
9.  How would you scale the application for 1,00,000 registered users?
10. How would you protect customer data and API keys?
11. What are the main operating costs of a production system?
12. What would you improve next?

Keep the code modular and understand the purpose of every function. The
interview may include live coding, debugging, or a request to modify the
workflow.

------------------------------------------------------------------------

## 15. GitHub Submission Requirements

The repository should include:

-   Complete source code.
-   `README.md` with project overview, prerequisites, installation,
    configuration, and run instructions.
-   `PROJECT_REPORT.md` containing a concise one-page project report.
-   Architecture diagram in `docs/`.
-   Screenshots of the working application.
-   `requirements.txt`.
-   `.env.example` with placeholder variable names only.

Never upload the real API key or `.env` file.

### Suggested one-page report outline

1.  Project title and objective.
2.  Business problem.
3.  Proposed solution.
4.  Technology stack.
5.  Architecture and end-to-end workflow.
6.  Implemented features.
7.  Scalability and security approach.
8.  Commercial feasibility and future enhancements.

------------------------------------------------------------------------

## 16. Final Implementation Priority

If development time is limited, follow this priority:

**Must work in the demonstration:** 1. Text-based AI sales conversation.
2. Contextual memory. 3. RAG-based company question answering. 4. Lead
extraction and classification. 5. Appointment request saved in SQLite.
6. Conversation summary and visible CRM record.

**Add after the core workflow works:** 7. Browser speech-to-text and
text-to-speech. 8. Basic dashboard charts. 9. Language selection.

**Explain as future enhancements:** 10. Real inbound/outbound telephony.
11. Production CRM integrations. 12. Large-scale deployment and load
testing.

The strongest submission is a small, reliable, end-to-end prototype that
you can explain and modify confidently---not a large system with
features that only work partially.
