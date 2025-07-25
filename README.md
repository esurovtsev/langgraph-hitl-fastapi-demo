# Human-in-the-Loop LangGraph Demo (FastAPI + React)

This project demonstrates a realistic Human-in-the-Loop (HITL) workflow using [LangGraph](https://github.com/langchain-ai/langgraph), embedded inside a Python FastAPI backend, with a React frontend. It is designed as a learning resource for developers interested in building interactive AI agent flows that pause for human input and then resume execution.

## What is Human-in-the-Loop (HITL)?

HITL systems combine automated AI workflows with critical points where human feedback or decisions are required. In this demo, a LangGraph node can pause execution, request user input via the frontend, and then continue processing once the input is received.

## Architecture Overview

- **Backend:** Python FastAPI server running an embedded LangGraph agent.
- **Frontend:** React app for interacting with the agent (sending messages, providing input when requested, viewing results).
- **Communication:** 
  - **Basic Version**: REST API endpoints with blocking request/response pattern.
  - **Advanced Version**: Server-Sent Events (SSE) for real-time streaming of LangGraph outputs.
- **State Management:** The backend manages the graph's state, including pausing and resuming at human input nodes.

## Implementation Versions

This project has two implementations available as a learning progression:

1. **Basic Version ([`basic-blocking-api`](https://github.com/esurovtsev/langgraph-hitl-fastapi-demo/tree/basic-blocking-api))**: Uses traditional blocking RESTful API calls, where the frontend waits for complete responses before updating. This is simpler to understand and implement.

2. **Advanced Version ([`advanced-streaming-sse`](https://github.com/esurovtsev/langgraph-hitl-fastapi-demo/tree/advanced-streaming-sse))**: Uses Server-Sent Events (SSE) for streaming responses from LangGraph to the frontend, providing real-time updates as the AI generates content.

To switch between versions:
```bash
# For basic implementation with blocking calls
git checkout basic-blocking-api

# For advanced implementation with streaming (default)
git checkout advanced-streaming-sse
```

## Testing the Extended HITL Scenario (SSE/Streaming)

This section demonstrates how to test a full Human-in-the-Loop (HITL) scenario using the advanced streaming server endpoints. The following curl commands walk through starting a run, streaming the response, providing feedback, streaming again, approving the answer, and finalizing the run.

1) **Create a new run**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"human_request": "Explain what is HITL"}' http://localhost:8000/graph/stream/create
```

2) **Stream the result**
```bash
curl --no-buffer http://localhost:8000/graph/stream/{thread_id}
```

3) **Provide feedback**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "thread_id": "{thread_id}",
  "review_action": "feedback",
  "human_comment": "Make your answer only one sentence short."
}' http://localhost:8000/graph/stream/resume
```

4) **Stream the revised result**
```bash
curl --no-buffer http://localhost:8000/graph/stream/{thread_id}
```

5) **Approve the answer**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "thread_id": "{thread_id}",
  "review_action": "approved"
}' http://localhost:8000/graph/stream/resume
```

6) **Stream the final result**
```bash
curl --no-buffer http://localhost:8000/graph/stream/{thread_id}
```

Replace `{thread_id}` with the actual thread_id you receive from the creation endpoint. You can also use the interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to experiment with these endpoints.

## Learning Goals

- Understand how to embed LangGraph in a real backend application.
- See how to implement HITL workflows that pause for human input and resume programmatically.
- Learn how to connect a Python backend to a modern React frontend.
- Explore practical patterns for managing agent state and user interaction.
- Compare blocking vs streaming implementations for AI-powered applications.


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
