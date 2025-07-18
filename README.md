# Human-in-the-Loop LangGraph Demo (FastAPI + React)

This project demonstrates a realistic Human-in-the-Loop (HITL) workflow using [LangGraph](https://github.com/langchain-ai/langgraph), embedded inside a Python FastAPI backend, with a React frontend. It is designed as a learning resource for developers interested in building interactive AI agent flows that pause for human input and then resume execution.

## What is Human-in-the-Loop (HITL)?

HITL systems combine automated AI workflows with critical points where human feedback or decisions are required. In this demo, a LangGraph node can pause execution, request user input via the frontend, and then continue processing once the input is received.

## Architecture Overview

- **Backend:** Python FastAPI server running an embedded LangGraph agent.
- **Frontend:** React app for interacting with the agent (sending messages, providing input when requested, viewing results).
- **Communication:** REST API endpoints connect the frontend and backend. The backend manages the graph’s state, including pausing and resuming at human input nodes.

## Learning Goals

- Understand how to embed LangGraph in a real backend application.
- See how to implement HITL workflows that pause for human input and resume programmatically.
- Learn how to connect a Python backend to a modern React frontend.
- Explore practical patterns for managing agent state and user interaction.


## How to Run Locally

1. **Backend:**  
   - **Important:** Run all backend commands from the `backend` directory.
   - Install Python dependencies (see `requirements.txt`).
   - Run the FastAPI server:
     ```sh
     uvicorn app.main:app --reload
     ```

2. **Frontend:**  
   - Run `npm install` in the `frontend` directory.
   - Start the React app with:
     ```sh
     npm start
     ```

3. **Usage:**  
   - Open [http://localhost:3000](http://localhost:3000) for the frontend.
   - The frontend will communicate with the backend at [http://localhost:8000](http://localhost:8000).
