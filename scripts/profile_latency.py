import time
from fastapi import BackgroundTasks
from app.database.session import SessionLocal
from app.services.chat_service import ChatService, _SESSION_CACHE
from app.retrieval.retriever import HybridRetriever
from app.nlp.intent import IntentClassifier

print("--- Step 1: In-memory HybridRetriever ---")
retriever = HybridRetriever()
t0 = time.perf_counter()
top_chunks, evidence = retriever.retrieve("what is the maximum deposit insurance coverage by dicgc?")
t1 = time.perf_counter()
print(f"HybridRetriever.retrieve: {(t1 - t0)*1000:.2f}ms")

print("\n--- Step 2: In-memory IntentClassifier ---")
classifier = IntentClassifier()
t0 = time.perf_counter()
intent, conf, meta = classifier.classify_intent("what is the maximum deposit insurance coverage by dicgc?")
t1 = time.perf_counter()
print(f"IntentClassifier classify: {(t1 - t0)*1000:.2f}ms")

print("\n--- Step 3: Fast API Mode with BackgroundTasks (Production Chat Endpoint) ---")
db = SessionLocal()
svc = ChatService(db)
bg = BackgroundTasks()

t0 = time.perf_counter()
resp = svc.process_chat(
    message="what is the maximum deposit insurance coverage by dicgc?",
    session_id="test_fast_session_1",
    background_tasks=bg,
)
t1 = time.perf_counter()
print(f"User-perceived Chat Response Latency: {(t1 - t0)*1000:.2f}ms")
print(f"Answer snippet: {resp.answer[:80]}...")
print(f"Number of citations: {len(resp.sources)}")

# Now execute background tasks (which runs async in the background after sending HTTP response)
t_bg_start = time.perf_counter()
for task in bg.tasks:
    task()
t_bg_end = time.perf_counter()
print(f"Background DB persistence (non-blocking): {(t_bg_end - t_bg_start)*1000:.2f}ms")

db.close()
