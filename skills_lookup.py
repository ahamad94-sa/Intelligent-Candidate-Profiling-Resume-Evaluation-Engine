import json
import difflib

with open("skills.json", "r", encoding="utf-8") as f:
    SKILL_DATA = json.load(f)


def find_best_domain_match(user_input):
    user_input = user_input.lower().strip()
    all_domains = list(SKILL_DATA.keys())
    matches = difflib.get_close_matches(user_input, all_domains, n=1, cutoff=0.3)
    if matches:
        return matches[0]
    for d in all_domains:
        if user_input in d:
            return d
    return None


def get_skills_for_domain(user_input):
    best = find_best_domain_match(user_input)
    if not best:
        return None, []
    return best, SKILL_DATA[best]


if __name__ == "__main__":
    q = input("Enter job role/domain: ")
    domain, skills = get_skills_for_domain(q)
    if not skills:
        print("❌ No domain found.")
    else:
        print(f"\n=== Skills required for {domain.upper()} ===")
        for s in skills:
            print(f"\n✔ {s['skill']}\n{s['description']}\n")
