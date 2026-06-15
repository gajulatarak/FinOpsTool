from __future__ import annotations

import json

from finops_tool.api import SAMPLE_COSTS, allocator, classifier


def main() -> None:
    results = [allocator.allocate(classifier.classify(item)) for item in SAMPLE_COSTS]
    payload = {
        "summary_by_category": [row.model_dump() for row in allocator.summarize_by_category(results)],
        "summary_by_owner": [row.model_dump() for row in allocator.summarize_by_owner(results)],
        "items": [item.model_dump() for item in results],
    }
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
