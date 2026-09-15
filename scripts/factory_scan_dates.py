#!/usr/bin/env python3
"""Scan SOFT THINGS chapters for weekday/relative-date contradictions."""
import os, re

D = "/root/novels/soft-things/chapters"
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
for f in sorted(os.listdir(D)):
    if not f.endswith(".md"):
        continue
    text = open(os.path.join(D, f), encoding="utf-8").read().lower()
    found = [d for d in days if re.search(r"\b" + d + r"\b", text)]
    rel = re.findall(r"\b(?:in )?(one|two|three|four|five|six|seven|a few|a couple) (days?|weeks?)\b", text)
    if found or rel:
        print(f, "weekdays:", found, "| relative:", rel)
