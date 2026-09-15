#!/usr/bin/env python3
"""Print a <=200-char intro (word-boundary truncated) for the upload command."""
premise = ("Jane Marlow is the 3.2, the most mocked leaked face-score in America, working as an "
           "invisible data-labeler inside the beauty-tech empire that ranked her ugly. What nobody "
           "knows: she runs the viral anti-beauty movement as the anonymous Last Duck, and she "
           "secretly owns 51 percent of the company through her dead mother's trust. Sent to the "
           "coast to collect a signature from the exiled founder who was framed for the leak that "
           "made her a meme, she refuses every cage and returns as the swan.")
limit = 200
if len(premise) <= limit:
    print(premise)
else:
    cut = premise[:limit]
    cut = cut[: cut.rfind(" ")]
    print(cut)
