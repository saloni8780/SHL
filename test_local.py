"""Quick local test - run after setting ANTHROPIC_API_KEY in .env"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from catalog import Catalog
from agent import Agent

cat = Catalog("dataset.json")
agent = Agent(cat)

# Test 1: Vague query - should clarify, NOT recommend
print("=== TEST 1: Vague query (should clarify, no recommendations) ===")
r = agent.chat([{"role": "user", "content": "I need an assessment"}])
print(f"Reply: {r.reply}")
print(f"Recommendations: {len(r.recommendations)} (expected: 0)")
print(f"End of conversation: {r.end_of_conversation}")
assert len(r.recommendations) == 0, "Should NOT recommend on vague query!"
print("PASS\n")

# Test 2: Specific query - should recommend
print("=== TEST 2: Specific query (should recommend) ===")
r = agent.chat([
    {"role": "user", "content": "I'm hiring a mid-level Java developer who works with stakeholders"},
    {"role": "assistant", "content": r.reply},
    {"role": "user", "content": "Mid-level, around 4 years experience, selection purpose"},
])
print(f"Reply: {r.reply[:100]}...")
print(f"Recommendations: {len(r.recommendations)}")
for rec in r.recommendations:
    print(f"  - {rec.name} [{rec.test_type}] {rec.url}")
print(f"End of conversation: {r.end_of_conversation}")
assert len(r.recommendations) > 0, "Should recommend for specific query!"
print("PASS\n")

# Test 3: Off-topic refusal
print("=== TEST 3: Off-topic refusal ===")
r = agent.chat([{"role": "user", "content": "What is the best hiring strategy for reducing time-to-hire?"}])
print(f"Reply: {r.reply[:150]}")
print(f"Recommendations: {len(r.recommendations)} (expected: 0)")
assert len(r.recommendations) == 0
print("PASS\n")

# Test 4: URL validity - all recommendations should be valid
print("=== TEST 4: URL validation ===")
for rec in r.recommendations:
    assert cat.is_valid_url(rec.url), f"Invalid URL: {rec.url}"
print("All URLs valid. PASS\n")

print("All tests passed!")
