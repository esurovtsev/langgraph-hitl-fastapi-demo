import React, { useState, useRef, useEffect } from "react";
import AssistantService from "./AssistantService";
import ReactMarkdown from "react-markdown";

const App = () => {
  // UI states: idle, waiting, user_feedback, finished
  const [uiState, setUiState] = useState("idle");
  const [question, setQuestion] = useState("");
  const [assistantResponse, setAssistantResponse] = useState("");
  const [feedback, setFeedback] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [history, setHistory] = useState([]);

  const feedbackInputRef = useRef(null);
  useEffect(() => {
    if (uiState === "feedback_form" && feedbackInputRef.current) {
      feedbackInputRef.current.focus();
    }
  }, [uiState]);
  
  // Placeholder submit handlers
  const handleStart = async () => {
  // Show user message and pending spinner immediately
  setUiState("waiting");
  setHistory([
    { role: "user", content: question },
    { role: "assistant", content: null } // null means pending/spinner
  ]);
  try {
    const data = await AssistantService.startConversation(question);
    setAssistantResponse(data.assistant_response);
    setUiState("idle"); // Always set to idle to show review buttons first
    setThreadId(data.thread_id);
    setHistory([
      { role: "user", content: question },
      { role: "assistant", content: data.assistant_response }
    ]);
  } catch (err) {
    setAssistantResponse("");
    setUiState("idle");
    alert("Failed to contact backend: " + err.message);
  }
};

  const handleApprove = async () => {
  setUiState("waiting");
  setHistory([...history, { role: "assistant", content: null }]); // Show spinner
  try {
    const data = await AssistantService.submitReview({
      thread_id: threadId,
      review_action: "approved"
    });
    setAssistantResponse(data.assistant_response);
    setUiState("finished"); // Transition to finished state after approval
    // Replace last assistant (spinner) with real response
    setHistory(prev => [
      ...prev.slice(0, -1),
      { role: "assistant", content: data.assistant_response }
    ]);
  } catch (err) {
    setUiState("idle");
    alert("Failed to contact backend: " + err.message);
  }
};

  const handleFeedback = async () => {
  setUiState("waiting");
  setHistory([
    ...history,
    { role: "user", content: feedback },
    { role: "assistant", content: null }
  ]); // Show spinner after feedback
  try {
    const data = await AssistantService.submitReview({
      thread_id: threadId,
      review_action: "feedback",
      human_comment: feedback
    });
    setAssistantResponse(data.assistant_response);
    setUiState("idle"); // Return to review state after feedback
    // Replace last assistant (spinner) with real response
    setHistory(prev => [
      ...prev.slice(0, -1),
      { role: "assistant", content: data.assistant_response }
    ]);
    setFeedback("");
  } catch (err) {
    setUiState("idle");
    alert("Failed to contact backend: " + err.message);
  }
};

  // Render
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', margin: '40px auto', fontFamily: 'sans-serif' }}>
      <div style={{ flex: '0 0 320px', maxWidth: 320, marginRight: 32, background: '#fafbfc', borderRadius: 8, border: '1px solid #eee', padding: 16, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <img src="/hitl-assistent.png" alt="HITL Graph" style={{ width: '75%', height: 'auto', borderRadius: 6, boxShadow: '0 2px 12px #0001', marginBottom: 16 }} />
        <div style={{ fontSize: 16, color: '#444', textAlign: 'center' }}>HITL Assistant Graph</div>
      </div>
      <div style={{ maxWidth: 600, width: '95%', padding: 24, border: '1px solid #eee', borderRadius: 8, position: 'relative', background: '#fff' }}>
        <button
          onClick={() => {
            setUiState("idle");
            setQuestion("");
            setAssistantResponse("");
            setFeedback("");
            setThreadId(null);
            setHistory([]);
          }}
          style={{ position: "absolute", top: 24, right: 24, padding: "8px 18px", fontSize: 16, borderRadius: 6, background: "#f5f5f5", border: "1px solid #ddd", cursor: "pointer" }}
        >
          New Session
        </button>
        <h2>Human-in-the-Loop Assistant</h2>
        {uiState === "idle" && history.length === 0 && (
          <div>
            <input
              type="text"
              placeholder="Ask a question..."
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") handleStart(); }}
              style={{ width: "70%", padding: 12, fontSize: 18, borderRadius: 6, border: '1px solid #bbb', marginRight: 8 }}
            />
            <button onClick={handleStart} style={{ padding: '12px 32px', fontSize: 20, borderRadius: 6, border: '1px solid #bbb', background: '#f5f5f5', cursor: 'pointer', height: 48 }}>Send</button>
          </div>
        )}

        {history.length > 0 && (
          <div style={{ margin: "24px 0" }}>
            {history.map((msg, idx) => {
              // Hide the last assistant message if in finished state (it's shown in Final Version block)
              if (uiState === "finished" && msg.role === "assistant" && idx === history.length - 1) {
                return null;
              }
              // Determine hint for each message
              let hint = null;
              if (msg.role === "user") {
                hint = idx === 0 ? "Initial request" : "Feedback";
              } else if (msg.role === "assistant" && idx === history.length - 1 && uiState === "finished") {
                hint = "You approved";
              }
              return (
                <div key={idx} style={{ textAlign: msg.role === "user" ? "right" : "left", margin: "8px 0" }}>
                  {hint && (
                    <div style={{ fontSize: 12, color: "#888", marginBottom: 2 }}>{hint}</div>
                  )}
                  <span style={{
                    fontWeight: msg.role === "user" ? 600 : 700,
                    color: msg.role === "assistant" ? '#1976d2' : undefined,
                    background: msg.role === "assistant" ? 'rgba(25, 118, 210, 0.08)' : undefined,
                    padding: msg.role === "assistant" ? '2px 8px' : undefined,
                    borderRadius: msg.role === "assistant" ? 4 : undefined
                  }}>
                    {msg.role === "user" ? "You: " : "Assistant: "}
                  </span>
                  {msg.role === "assistant" && msg.content === null ? (
                    <div style={{ display: "inline-block", verticalAlign: "middle", marginLeft: 6 }}>
                      <div style={{
                        border: "4px solid #eee",
                        borderTop: "4px solid #333",
                        borderRadius: "50%",
                        width: 24,
                        height: 24,
                        animation: "spin 1s linear infinite",
                        display: "inline-block"
                      }} />
                      <style>{`
                        @keyframes spin {
                          0% { transform: rotate(0deg); }
                          100% { transform: rotate(360deg); }
                        }
                      `}</style>
                    </div>
                  ) : msg.role === "assistant" ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              );
            })}
          </div>
        )}
        {uiState === "user_feedback" && (
          <div style={{ marginTop: 24, background: '#f8fafd', border: '1px solid #e3eaf2', borderRadius: 6, padding: 18 }}>
            <div style={{ marginBottom: 8, fontWeight: 600 }}>Please provide feedback to improve the assistant's answer:</div>
            <textarea
              ref={feedbackInputRef}
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              rows={3}
              style={{ width: '95%', padding: 12, fontSize: 18, borderRadius: 6, border: '1px solid #bbb', resize: 'vertical' }}
              placeholder="Your feedback..."
            />
            <div style={{ marginTop: 8 }}>
              <button
                onClick={handleFeedback}
                style={{ marginRight: 8, padding: "8px 24px", height: 48, fontSize: 20 }}
              >
                Submit Feedback
              </button>
              <button
                onClick={() => {
                  setUiState("idle");
                  setFeedback("");
                }}
                style={{ padding: "8px 24px", height: 48, fontSize: 20 }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
        {uiState === "waiting" && null}
        {uiState === "idle" && (
          // Only show review buttons if there is an assistant response
          (assistantResponse || (history.length > 0 && history[history.length - 1].role === "assistant" && history[history.length - 1].content)) && (
            <div style={{ marginTop: 24, textAlign: 'right' }}>
              <button
                onClick={handleApprove}
                style={{ marginRight: 8, padding: "8px 24px", height: 48, fontSize: 20 }}
              >
                Approve
              </button>
              <button
                onClick={() => setUiState("user_feedback")}
                style={{ padding: "8px 24px", height: 48, fontSize: 20 }}
              >
                Send Feedback
              </button>
            </div>
          )
        )}
        {uiState === "finished" && (
          <div>
            <div style={{ textAlign: "right", margin: "8px 0" }}>
              <div style={{ fontSize: 12, color: "#888", marginBottom: 2 }}>You approved</div>
              <span style={{ fontWeight: 600 }}>You: </span>approved the answer
            </div>
            <div style={{ marginTop: 24, padding: 12, background: "#f6f6f6", borderRadius: 6 }}>
              <span style={{
                fontWeight: 700,
                color: '#1976d2',
                background: 'rgba(25, 118, 210, 0.08)',
                padding: '2px 8px',
                borderRadius: 4,
                marginBottom: 8,
                display: 'inline-block'
              }}>
                Assistant:
              </span>
              <strong style={{ marginLeft: 8 }}>Final version:</strong>
              <ReactMarkdown>{assistantResponse}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
