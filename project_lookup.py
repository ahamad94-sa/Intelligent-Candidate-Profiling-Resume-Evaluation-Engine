import json
import difflib

# Load domain-to-project mapping
with open("domains.json", "r", encoding="utf-8") as f:
    DOMAIN_DATA = json.load(f)

def find_best_domain_match(user_input):
    """Find closest matching domain from partial input."""
    user_input = user_input.lower().strip()

    all_domains = list(DOMAIN_DATA.keys())
    matches = difflib.get_close_matches(user_input, all_domains, n=1, cutoff=0.3)

    if matches:
        return matches[0]

    # fallback: substring match
    for d in all_domains:
        if user_input in d:
            return d

    return None


def get_projects_for_domain(user_input):
    """Return list of 3 projects for matched domain."""
    best = find_best_domain_match(user_input)
    if not best:
        return None, []

    return best, DOMAIN_DATA[best]


# -----------------------------------------
# Test (only when run directly — not inside Streamlit)
# -----------------------------------------
if __name__ == "__main__":
    print("Enter job domain:")
    q = input("> ")

    domain, projects = get_projects_for_domain(q)

    if not projects:
        print("❌ No matching domain found.")
    else:
        print(f"\n✅ Showing project ideas for: {domain.upper()}\n")
        for i, p in enumerate(projects, 1):
            print(f"{i}. {p['title']}\n{p['desc']}\n")
