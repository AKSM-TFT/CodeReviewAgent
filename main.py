from agent.nodes.classify import classify

state = {
    "pr_url": "",
    "raw_diff": """
+def login(user, password):
+    query = f"SELECT * FROM users WHERE user='{user}' AND pass='{password}'"
+    return conn.execute(query)
""",
    "chunks": [],
    "categories": [],
    "security_comments": [],
    "logic_comments": [],
    "final_comments": "",
    "error": None
}

result = classify(state)
print(result)