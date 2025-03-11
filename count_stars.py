import yaml

import os


def main():
    with open(os.path.join(os.path.dirname(__file__), "data.yml")) as f:
        data = yaml.safe_load(f)

    personal_stars = 0
    org_stars = {}

    for name, stats in data["repositories"].items():
        if "/" not in name:
            personal_stars += stats["stars"]
        else:
            org = name.split("/")[0]
            if org not in org_stars:
                org_stars[org] = 0
            org_stars[org] += stats["stars"]

    print(f"{data['user']['name']}: {personal_stars:d}")
    print()
    for org, stars in sorted(org_stars.items(), key=lambda x: x[0]):
        print(f"{org}: {stars:d}")
    print()
    print(f"(total): {personal_stars + sum(org_stars.values()):d}")


if __name__ == "__main__":
    main()
