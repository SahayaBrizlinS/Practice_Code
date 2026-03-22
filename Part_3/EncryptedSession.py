import asyncio
import time
from agents import Agent, Runner
from agents.extensions.memory import EncryptedSession, SQLAlchemySession
from dotenv import load_dotenv

load_dotenv(override=True)
# =========================================================
# 🔹 CONFIG (PRODUCTION STYLE)
# =========================================================
DATABASE_URL = "sqlite+aiosqlite:///secure_conversations.db"

SESSION_ID = "user_123"
ENCRYPTION_KEY = "super-secret-key"   # In production → use ENV variable
TTL_SECONDS = 10                     # Short TTL for demo (10 seconds)


# =========================================================
# 🔹 CREATE UNDERLYING SESSION
# =========================================================
underlying_session = SQLAlchemySession.from_url(
    SESSION_ID,
    url=DATABASE_URL,
    create_tables=True
)

# =========================================================
# 🔹 WRAP WITH ENCRYPTION
# =========================================================
session = EncryptedSession(
    session_id=SESSION_ID,
    underlying_session=underlying_session,
    encryption_key=ENCRYPTION_KEY,
    ttl=TTL_SECONDS
)

# =========================================================
# 🔹 AGENT
# =========================================================
agent = Agent(
    name="SecureAssistant",
    instructions="You are a secure assistant. Keep responses short."
)

# =========================================================
# 🔹 HELPER FUNCTION
# =========================================================
async def chat(message: str):
    print(f"\n🧑 USER: {message}")

    result = await Runner.run(agent, message, session=session)

    print(f"🤖 AI: {result.final_output}")

    return result


# =========================================================
# 🔹 MAIN DEMO
# =========================================================
async def main():

    print("\n================= ENCRYPTED SESSION DEMO =================")

    # -----------------------------------------------------
    # 1. NORMAL CONVERSATION (DATA STORED ENCRYPTED)
    # -----------------------------------------------------
    print("\n🔐 STEP 1: Initial conversation (data will be encrypted)")

    await chat("Hi, my name is Arjun")
    await chat("What is my name?")  # Should remember

    # -----------------------------------------------------
    # 2. SHOW RAW DB DATA (ENCRYPTED)
    # -----------------------------------------------------
    print("\n🔐 STEP 2: Check DB manually → you will see encrypted text")
    print("👉 Open 'secure_conversations.db' in SQLite viewer")
    print("👉 Messages will NOT be readable (encrypted)")

    # -----------------------------------------------------
    # 3. TTL DEMO (WAIT FOR EXPIRY)
    # -----------------------------------------------------
    print(f"\n⏱️ STEP 3: Waiting {TTL_SECONDS} seconds for TTL expiry...")
    time.sleep(TTL_SECONDS + 2)

    # -----------------------------------------------------
    # 4. AFTER TTL EXPIRY
    # -----------------------------------------------------
    print("\n⏱️ STEP 4: After TTL expiry (memory should be gone)")

    await chat("Do you remember my name?")  # Should NOT remember

    # -----------------------------------------------------
    # 5. NEW MEMORY STARTS
    # -----------------------------------------------------
    print("\n🔄 STEP 5: New conversation after expiry")

    await chat("My name is Rahul")
    await chat("What is my name?")  # Should remember Rahul

    print("\n================= DEMO COMPLETE =================")


# =========================================================
# 🔹 RUN
# =========================================================
if __name__ == "__main__":
    asyncio.run(main())
# =========================================================
# ENCRYPTED SESSION - COMPLETE UNDERSTANDING
# =========================================================
# This implementation adds a security layer on top of any
# session (SQLite, SQLAlchemy, etc.) by encrypting all data
# before storing it in the database.
#
# Key Idea:
#   - Underlying session handles storage
#   - EncryptedSession adds protection (encryption layer)
#
# Flow:
#   User Input → EncryptedSession → Underlying Session → Database
#
# Data stored in DB:
#   - NOT readable (encrypted bytes)
#   - Only accessible with correct encryption key
#
# Benefits:
#   - Protects sensitive user data
#   - Prevents data leaks from exposing conversations
#
# Trade-off:
#   - Cannot perform text-based search on encrypted content
#
# =========================================================
# =========================================================
# WRAPPING SESSION WITH ENCRYPTION
# =========================================================
# EncryptedSession acts as a wrapper around an existing session.
#
# It does NOT replace the session.
# It simply intercepts data:
#
#   On store:
#       plain text → encrypted → saved in DB
#
#   On retrieve:
#       encrypted → decrypted → returned to agent
#
# This is completely transparent to the rest of the code.
# No changes required in agent logic.
#
# Analogy:
#   - Underlying session = drawer
#   - EncryptedSession = lock on the drawer
# =========================================================
# ENCRYPTION KEY
# =========================================================
# encryption_key is used to encrypt and decrypt data.
#
# Requirements:
#   - Can be any string
#   - Should be kept SECRET
#
# Internally:
#   - A secure key is derived using HKDF
#   - Each session_id generates a unique encryption key
#
# This ensures:
#   - Same key + different session_id → different encryption output
#
# Production Best Practice:
#   - NEVER hardcode keys
#   - Use environment variables or secret managers
#
# Example:
#   os.getenv("ENCRYPTION_KEY")
# =========================================================
# TTL (TIME-TO-LIVE)
# =========================================================
# TTL defines how long stored messages remain "valid"
#
# After TTL expires:
#   - Messages are NOT returned during retrieval
#   - They are effectively ignored by the system
#
# IMPORTANT:
#   - Data is NOT deleted from database
#   - It is only filtered out during retrieval
#
# Example:
#   ttl = 3600  → messages older than 1 hour are ignored
#
# Internal logic:
#   if (current_time - message_time) > ttl:
#       skip message
#
# Use Cases:
#   - Auto-expiring conversations
#   - Privacy compliance (GDPR)
#   - Reducing context size
#
# Mental Model:
#   Database stores everything
#   TTL decides what is "visible"
# =========================================================
# ENCRYPTION FLOW
# =========================================================
# When storing data:
#   User message → ENCRYPT → stored in DB
#
# When retrieving data:
#   Encrypted data → DECRYPT → returned to agent
#
# This process is automatic and transparent.
#
# Result:
#   - Database contains unreadable encrypted data
#   - Application still works normally
# =========================================================
# LIMITATION: CONTENT SEARCH DOES NOT WORK
# =========================================================
# Methods like:
#   find_turns_by_content("weather")
#
# will NOT work with encrypted sessions.
#
# Reason:
#   - Data in DB is encrypted (not plain text)
#   - Search operates on raw stored data
#   - Encrypted data does not match readable text
#
# Example:
#   "weather" ≠ "gAAAAABkX..."
#
# Impact:
#   - No keyword search
#   - No text-based analytics
#
# Trade-off:
#   Security ↑  →  Searchability ↓
# =========================================================
# PRODUCTION ARCHITECTURE
# =========================================================
# EncryptedSession sits as a security layer:
#
#        Agent
#          ↓
#   EncryptedSession  🔒
#          ↓
#   Underlying Session (SQLAlchemy / SQLite)
#          ↓
#       Database
#
# Responsibilities:
#   - Underlying session → storage & retrieval
#   - EncryptedSession → security & privacy
#
# This separation allows:
#   - Reuse of existing session logic
#   - Plug-and-play encryption
# =========================================================
# TRADE-OFF: SECURITY vs ANALYTICS
# =========================================================
# Without encryption:
#   ✅ Searchable data
#   ✅ Easy analytics
#   ❌ Less secure
#
# With encryption:
#   ✅ Secure data
#   ❌ No content search
#   ❌ Limited analytics
#
# Production systems often use hybrid approach:
#   - Sensitive data → encrypted
#   - Metadata → stored in plain text
# =========================================================
# TTL vs DATA DELETION
# =========================================================
# TTL:
#   - Data remains in database
#   - Ignored during retrieval
#   - Reversible (change TTL)
#
# Deletion:
#   - Data removed permanently
#   - Cannot be recovered
#
# EncryptedSession uses TTL filtering, NOT deletion
# =========================================================
# REAL-WORLD USE CASES
# =========================================================
# Encrypted sessions are used in:
#
# 🔐 Secure chat applications
#   - Protect user conversations
#
# 🏥 Healthcare systems
#   - Store sensitive patient interactions
#
# 💳 Financial applications
#   - Protect transactional discussions
#
# 📜 Compliance-driven systems
#   - GDPR, HIPAA requirements
#
# Key requirement:
#   Data must not be readable even if database is compromised
# =========================================================
# FINAL MENTAL MODEL
# =========================================================
# Think of EncryptedSession as:
#
#   "A transparent security layer over your memory system"
#
# It provides:
#   - Data encryption (security)
#   - TTL filtering (controlled visibility)
#
# But restricts:
#   - Direct content access
#   - Text-based querying
#
# Core Idea:
#   Secure storage with controlled access
# =========================================================
