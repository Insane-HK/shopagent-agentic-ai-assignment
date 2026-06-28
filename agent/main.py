from agent.agent import run_agent

questions = [
    "Where is my order ORD-1002?",
    "Do you have any headphones? What's cheaper than Sony?",
    "What happened to order ORD-1003? Also show me bags you have.",
    "Tell me more about PROD-006",
]

if __name__ == "__main__":
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        res = run_agent(q)
        print(f"A: {res['answer']}")
        if res['trace']:
            print(f"   [tools used: {', '.join(t['tool'] for t in res['trace'])}]")
