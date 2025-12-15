import json
import os

INPUT_FILE = "data/olemiss_data.jsonl"
OUTPUT_FILE = "data/data_preview.md"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        
        f_out.write("# Ole Miss Data Preview\n\n")
        f_out.write(f"Generated from `{INPUT_FILE}` for easier verification.\n\n")
        
        lines = f_in.readlines()
        f_out.write(f"**Total Records:** {len(lines)}\n\n")
        f_out.write("---\n\n")

        for i, line in enumerate(lines):
            try:
                record = json.loads(line)
                
                # Header
                f_out.write(f"## {i+1}. {record.get('title', 'No Title')}\n")
                f_out.write(f"- **URL**: {record.get('url')}\n")
                f_out.write(f"- **Type**: `{record.get('page_type')}`\n")
                f_out.write(f"- **Fetched At**: {record.get('fetched_at')}\n\n")
                
                # Content Preview (Truncated if too long, or full?)
                # Let's show full content but in a quote block or code block if it's markdown
                f_out.write("### Content Preview:\n")
                content = record.get('text_clean', '')
                
                # Add a visual separator for the content
                f_out.write("> " + content.replace("\n", "\n> ") + "\n\n")
                
                f_out.write("---\n\n")
                
            except json.JSONDecodeError:
                f_out.write(f"## Error reading line {i+1}\n\n---\n\n")

    print(f"Preview generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
