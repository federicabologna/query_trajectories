import os

token_map = {
    'S2_API_KEY': 'S2_TOKEN',
    'ANTHROPIC_API_KEY': 'ANTHROPIC_TOKEN',
    'OPENAI_API_KEY': 'OPEN_AI_TOKEN',
    'GEMINI_API_KEY': 'GEMINI_TOKEN',
}

export_lines = []
missing = []

for target, source in token_map.items():
    token = os.getenv(source)
    if token:
        export_lines.append(f"export {target}='{token}'")
        print(f"✅ Will export {target} from {source}")
    else:
        missing.append(source)
        print(f"⚠️  {source} not found; skipping {target}")

export_lines.append('python -m model.response.generate_response')

# Write to shell script
with open("scripts/export_tokens.sh", "w") as f:
    f.write("#!/bin/bash\n")
    f.write("# Auto-generated export script\n\n")
    for line in export_lines:
        f.write(f"{line}\n")

print("\n📄 Wrote export_tokens.sh")
if missing:
    print("⚠️  Missing the following source env vars:")
    for m in missing:
        print(f"   - {m}")
print("\n👉 Run this to apply the exports in your shell:")
print("   source scripts/export_tokens.sh")