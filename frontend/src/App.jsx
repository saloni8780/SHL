import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'
import RecommendationCard from './components/RecommendationCard'
import TypingIndicator from './components/TypingIndicator'

const MAX_TURNS = 8
const API_URL = '/chat'

const SUGGESTIONS = [
  'I\'m hiring a mid-level Java developer',
  'Need assessments for senior leadership',
  'Screening 200 customer service agents',
  'Hiring a data scientist for ML roles',
]

function SHLLogo({ size = 28 }) {
  return (
    <svg width={size} height={size * 0.42} viewBox="0 0 80 34" fill="none">
      <text x="0" y="28" fontFamily="Arial Black, sans-serif" fontWeight="900"
        fontSize="32" fill="#00a551" letterSpacing="-1">SHL.</text>
    </svg>
  )
}

function AgentAvatar() {
  return (
    <div className="avatar agent">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
      </svg>
    </div>
  )
}

function UserAvatar() {
  return (
    <div className="avatar user">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
        <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
      </svg>
    </div>
  )
}

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`message-row ${isUser ? 'user' : 'agent'}`}>
      {isUser ? <UserAvatar /> : <AgentAvatar />}
      <div className="message-body">
        <div className={`bubble ${isUser ? 'user' : 'agent'}`}>
          {msg.content}
        </div>
        {msg.recommendations?.length > 0 && (
          <div className="recommendations">
            <span className="recs-label">{msg.recommendations.length} Assessment{msg.recommendations.length > 1 ? 's' : ''} recommended</span>
            <div className="recs-grid">
              {msg.recommendations.map((rec, i) => (
                <RecommendationCard key={i} rec={rec} />
              ))}
            </div>
          </div>
        )}
        {msg.endOfConversation && (
          <div className="eoc-banner">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Assessment selection complete
          </div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])   // {role, content, recommendations?, endOfConversation?}
  const [history, setHistory] = useState([])     // API-format: [{role, content}]
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)
  const turnCount = Math.ceil(history.length / 2)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || loading || done) return
    setError(null)

    const userMsg = { role: 'user', content: text.trim() }
    const newHistory = [...history, userMsg]

    setMessages(prev => [...prev, { role: 'user', content: text.trim() }])
    setHistory(newHistory)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newHistory }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Server error ${res.status}`)
      }
      const data = await res.json()

      const assistantEntry = { role: 'assistant', content: data.reply }
      setHistory(prev => [...prev, assistantEntry])
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.reply,
        recommendations: data.recommendations,
        endOfConversation: data.end_of_conversation,
      }])
      if (data.end_of_conversation) setDone(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }, [history, loading, done])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const resetChat = () => {
    setMessages([])
    setHistory([])
    setInput('')
    setError(null)
    setDone(false)
    inputRef.current?.focus()
  }

  const remaining = MAX_TURNS - turnCount

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <SHLLogo size={34} />
          <div>
            <div className="header-title">Assessment Recommender</div>
            <div className="header-subtitle">Powered by SHL catalog · {377} assessments</div>
          </div>
        </div>
        <div className="header-spacer" />
        {messages.length > 0 && (
          <div className="turn-badge">
            {done ? 'Complete' : `${remaining} turn${remaining !== 1 ? 's' : ''} left`}
          </div>
        )}
        <button className="new-chat-btn" onClick={resetChat}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.45"/>
          </svg>
          New chat
        </button>
      </header>

      {/* Chat window */}
      <div className="chat-window">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="logo-large">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00a551" strokeWidth="1.8">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h2>Find the right SHL assessments</h2>
            <p>Describe the role you're hiring for and I'll recommend a tailored assessment battery from SHL's catalog.</p>
            <div className="suggestion-chips">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="chip" onClick={() => sendMessage(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)
        )}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="input-area">
        {error && <div className="error-toast">⚠ {error}</div>}
        <div className="input-row">
          <textarea
            ref={inputRef}
            className="input-box"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={done ? 'Conversation ended — click New chat to start again' : 'Describe the role or ask about assessments…'}
            disabled={loading || done}
            rows={1}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading || done}
            title="Send"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
        <div className="input-hint">Enter to send · Shift+Enter for new line</div>
      </div>
    </>
  )
}
