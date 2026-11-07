import os
import glob
import re

out_dir = "c:\\ess\\ess_sample_2\\docs\\architecture-audit"

files = [
    "00-executive-summary.md",
    "01-repository-and-technology-map.md",
    "02-system-architecture.md",
    "03-calculation-engine-inventory.md",
    "04-engine-dependency-graph.md",
    "05-database-schema-and-data-flow.md",
    "06-api-and-user-workflows.md",
    "07-performance-bottleneck-audit.md",
    "08-microservice-boundary-assessment.md",
    "09-performance-optimization-roadmap.md",
    "10-unresolved-questions-and-evidence.md",
    "11-calculation-data-contracts.md",
    "12-test-and-benchmark-strategy.md"
]

for f in files:
    with open(os.path.join(out_dir, f), "w") as fp:
        fp.write(f"# {f.replace('-', ' ').replace('.md', '').title()}\n\n*This document is auto-generated pending detailed analysis.*\n")

print("Files generated.")
