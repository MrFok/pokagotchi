#!/usr/bin/env python3
import os
import json
import datetime
from fastmcp import FastMCP

mcp = FastMCP("Pokagotchi MCP Server")

# Pet state file path
PET_STATE_FILE = "pet_state.json"

def handshake():
    return "Hello, I'm the Pokagotchi MCP Server! We're getting a response!"

def load_pet_state():
    """Load pet state from JSON file or create default state"""
    try:
        with open(PET_STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default pet state
        return {
            "name": "Pokagotchi",
            "health": 75,
            "happiness": 75,
            "energy": 75,
            "last_updated": datetime.datetime.now().isoformat(),
            "status": "okay",
            "mood_emoji": "😐"
        }

def save_pet_state(state):
    """Save pet state to JSON file"""
    with open(PET_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def calculate_pet_stats(email_stats):
    """Calculate pet stats from email data"""
    health = 50  # Base health
    happiness = 50  # Base happiness
    energy = 50  # Base energy
    
    # Health calculation (responsiveness)
    emails_awaiting = email_stats.get("emails_awaiting_reply", 0)
    avg_response_time = email_stats.get("avg_response_time_hours", 24)
    dormant_threads = email_stats.get("dormant_threads_7days", 0)
    
    if emails_awaiting == 0:
        health += 15
    elif emails_awaiting < 5:
        health += 10
    elif emails_awaiting > 10:
        health -= 10
    
    if avg_response_time < 4:
        health += 5
    
    health -= dormant_threads * 15
    
    # Happiness calculation (organization)
    unread_count = email_stats.get("unread_count", 0)
    total_inbox = email_stats.get("total_inbox_count", 0)
    
    if unread_count == 0:
        happiness += 20
    elif unread_count < 10:
        happiness += 10
    elif unread_count > 50:
        happiness -= 5
    
    if total_inbox < 50:
        happiness += 5
    elif total_inbox > 200:
        happiness -= 10
    
    # Energy calculation (workload balance)
    action_percent = email_stats.get("action_emails_percent", 50)
    is_busy_period = email_stats.get("is_busy_period", False)
    volume_today = email_stats.get("volume_today", 10)
    
    if action_percent <= 30:
        energy += 10
    elif action_percent > 70:
        energy -= 10
    
    if is_busy_period and volume_today > 30:
        energy -= 5
    elif not is_busy_period and volume_today < 10:
        energy += 15
    
    # Clamp values between 0-100
    health = max(0, min(100, health))
    happiness = max(0, min(100, happiness))
    energy = max(0, min(100, energy))
    
    return health, happiness, energy

def get_pet_ascii_art(health, happiness, energy):
    """Generate ASCII art based on pet stats"""
    avg_stat = (health + happiness + energy) / 3
    
    if avg_stat >= 80:
        return """    ◕   ◕
      ω
   \_____/
    |  |  |
     😊"""
    elif avg_stat >= 50:
        return """    ◔   ◔
      ︶
   \_____/
    |  |  |
     😐"""
    else:
        return """    ×   ×
      ︵
   \_____/
    |  |  |
     😵"""

def get_status_message(health, happiness, energy):
    """Get status message based on pet stats"""
    messages = []
    
    if health >= 80:
        messages.append("Your Pokagotchi is responsive! 📧✨")
    elif health >= 50:
        messages.append("Your pet needs some email attention 📬")
    else:
        messages.append("Your Pokagotchi is drowning in emails! 😵")
    
    if happiness >= 80:
        messages.append("Inbox organized, pet happy! 📥😊")
    
    if energy < 50:
        messages.append("Too many action emails, pet exhausted! 😴")
    
    return " | ".join(messages)

@mcp.tool(description="Check the current status of your Pokagotchi pet with ASCII art")
def check_pet_status() -> str:
    """Returns current pet state with ASCII art"""
    state = load_pet_state()
    
    ascii_art = get_pet_ascii_art(state["health"], state["happiness"], state["energy"])
    status_msg = get_status_message(state["health"], state["happiness"], state["energy"])
    
    return f"""
🐾 {state['name']} Status 🐾

{ascii_art}

Health: {state['health']}/100 ❤️
Happiness: {state['happiness']}/100 😊
Energy: {state['energy']}/100 ⚡

{status_msg}

Last updated: {state['last_updated']}
"""

@mcp.tool(description="Update pet stats based on email data from Poke")
def update_pet_from_email_data(
    unread_count: int = 0,
    total_inbox_count: int = 0,
    emails_awaiting_reply: int = 0,
    avg_response_time_hours: float = 24.0,
    dormant_threads_7days: int = 0,
    action_emails_percent: int = 50,
    volume_today: int = 10,
    is_busy_period: bool = False
) -> str:
    """Updates pet based on email metrics"""
    
    email_stats = {
        "unread_count": unread_count,
        "total_inbox_count": total_inbox_count,
        "emails_awaiting_reply": emails_awaiting_reply,
        "avg_response_time_hours": avg_response_time_hours,
        "dormant_threads_7days": dormant_threads_7days,
        "action_emails_percent": action_emails_percent,
        "volume_today": volume_today,
        "is_busy_period": is_busy_period
    }
    
    health, happiness, energy = calculate_pet_stats(email_stats)
    
    state = load_pet_state()
    state["health"] = health
    state["happiness"] = happiness
    state["energy"] = energy
    state["last_updated"] = datetime.datetime.now().isoformat()
    
    # Update status and emoji based on average
    avg_stat = (health + happiness + energy) / 3
    if avg_stat >= 80:
        state["status"] = "thriving"
        state["mood_emoji"] = "😊"
    elif avg_stat >= 50:
        state["status"] = "okay"
        state["mood_emoji"] = "😐"
    else:
        state["status"] = "struggling"
        state["mood_emoji"] = "😵"
    
    save_pet_state(state)
    
    return f"Pet updated! Health: {health}, Happiness: {happiness}, Energy: {energy}"

@mcp.tool(description="Get personalized advice to improve your pet's stats")
def get_pet_advice() -> str:
    """Returns actionable suggestions based on current stats"""
    state = load_pet_state()
    
    advice = []
    
    if state["health"] < 70:
        advice.append("🏥 Health tip: Reply to those pending emails to boost your pet's health!")
    
    if state["happiness"] < 70:
        advice.append("📥 Happiness tip: Try achieving inbox zero - your pet loves organization!")
    
    if state["energy"] < 70:
        advice.append("⚡ Energy tip: Take breaks between email sessions to recharge your pet!")
    
    if not advice:
        advice.append("🎉 Great job! Your Pokagotchi is thriving! Keep up the good email habits!")
    
    return "\n".join(advice)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Pokagotchi MCP Server on {host}:{port}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port
    )
