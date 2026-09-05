#!/usr/bin/env python3
"""Phase 3: scaffold /root/novels/sweet-little-idiot/ — project yaml, outline, state files."""
import os

ROOT = "/root/novels/sweet-little-idiot"

project_yaml = """meta:
  title: Sweet Little Idiot
  author: Apex Shaw
  genre: Contemporary Romance Suspense, Revenge, Influencer Drama
  language: english
  premise: After her influencer boyfriend's inner circle frames her for leaking their secrets and cancels her into nonexistence, Hazel Quinn returns as Nell, a doe-eyed, forgetful "airhead" PA in the orbit of the same people who destroyed her. Everyone confesses to her because she seems too dumb to matter. She remembers every word. One by one, she uses their own confessions to take them apart.
  logline: She plays the fool so well that nobody sees the knife.
  tagline: Nobody confesses to the dangerous ones.
  core_conflict: The sweetest girl in the room is collecting everyone's secrets - and she remembers the day they destroyed her.
  github_owner: andy-develop
  timeline_start: 2026-05-10
  timeline_end: 2026-06-20
"""

characters_yaml = """characters:
  - id: hazel
    name: Hazel Quinn
    aliases: [Nell Wren, Nell, H]
    status: alive
    location: Los Angeles
    role: Protagonist - cancelled influencer reborn as "airhead" PA
    key_traits: [patient, performs naivety, photographic memory for confessions, zero visible ambition, sharp interiority]
    speech_pattern: plays ditzy - "oh my god, I don't know ANYTHING" - pauses, tilts head, sweet smile; interior voice is clipped and precise
    abilities: [total recall of everyone's private admissions, master-level feigned innocence, reading body language]
    relationships:
      kai: ex-boyfriend who destroyed her - target
      sloane: secret orchestrator of her fall - primary target
      felix: younger brother - the one innocent person, she protects him
      iris: old friend who stayed loyal - her only ally
      marcus: entertainment lawyer - ally with his own grudge
      dara: manager who stole her brand - target
      cole: former friend who sold her out - target (later apologizes)
    inventory: [zero-view burner phone, wax-seal signet ring (family heirloom), evidence drive, fake PA lanyard]
    secrets: [is Hazel Quinn, not Nell Wren; has every confession on tape; plans to burn the Violet Room down]
    notes: Must protect Felix above all - she is Medea who chooses NOT to destroy the innocent
    last_appeared: null
  - id: kai
    name: Kai Voss
    aliases: [Kai, K]
    status: alive
    location: Los Angeles
    role: Antagonist - golden-boy influencer, Hazel's ex
    key_traits: [charming, cowardly, image-obsessed, charismatic on camera, hollow off it]
    speech_pattern: brand-safe platitudes, "bro", crowd-pleasing, panics in private
    abilities: [content charisma, algorithm luck, network of yes-men]
    relationships:
      hazel: ex-girlfriend he threw under the bus - target of revenge
      sloane: current "situationship", does what she says
      dara: manager who runs his business
      cole: best friend / yes-man
    inventory: [Hazel's old phone with the evidence]
    secrets: [he was the one who let the group chat leak her location; he still has her phone; he knows she is innocent]
    notes: Believes Hazel is dead. Panics when Nell reminds him of her.
    last_appeared: null
  - id: sloane
    name: Sloane Park
    aliases: [Sloane, S]
    status: alive
    location: Los Angeles
    role: Primary antagonist - "white lotus" fashion influencer, secret mastermind
    key_traits: [perfect on the surface, ruthless underneath, weaponizes sweetness, meticulous]
    speech_pattern: gentle, warm, supportive in public; icy commands in private; never raises voice
    abilities: [reputation management, planting stories, controlling Kai, reading rooms]
    relationships:
      hazel: rival she erased from the industry
      kai: puppet boyfriend
      dara: business partner in the takedown
      marcus: the one lawyer she failed to corrupt - mutual enemy
    inventory: [the edited apology video, Hazel's cancelled collab contracts]
    secrets: [she staged the leak, edited the video, owns the smear campaign; she keeps every enemy's secret in a vault]
    notes: The white lotus who unmasked. Must be publicly destroyed at the true climax.
    last_appeared: null
  - id: felix
    name: Felix Quinn
    aliases: [Felix, Fee]
    status: alive
    location: Pasadena
    role: Hazel's younger brother - the innocent
    key_traits: [quiet, kind, scared, loyal]
    speech_pattern: soft, anxious, understated
    abilities: [none special - that is the point]
    relationships:
      hazel: sister he thinks is dead - in on the secret by ch18
      rina: his high-school sweetheart
    inventory: [Hazel's childhood drawings]
    secrets: [none - he is the one truly innocent person in the story]
    notes: Story's conscience. Hazel protects him at any cost - her Medea moment inverted.
    last_appeared: null
  - id: iris
    name: Iris Chen
    aliases: [Iris]
    status: alive
    location: Los Angeles
    role: Ally - Hazel's only real friend
    key_traits: [fierce, loyal, pragmatic, street-smart]
    speech_pattern: direct, profane, warm
    abilities: [runs sound for events, hears everything, knows the industry's back alleys]
    relationships:
      hazel: best friend since college; knew the truth from day one
      marcus: work acquaintance turned co-conspirator
    inventory: [access to event AV systems, a van, a spare key to the Glasshouse]
    secrets: [helped Hazel vanish, runs the anonymous tip account]
    notes: The loyal friend archetype - proof Hazel's world still has love.
    last_appeared: null
  - id: marcus
    name: Marcus Vale
    aliases: [Marcus, Vale]
    status: alive
    location: Los Angeles
    role: Ally - entertainment lawyer with a grudge against Sloane
    key_traits: [precise, sardonic, burned by Sloane once, wants receipts]
    speech_pattern: dry, legal-minded, half-amused
    abilities: [contracts, NDAs, discovery, knowing where bodies are buried]
    relationships:
      hazel: client / ally
      sloane: enemy - she bankrupted his old client with the same playbook
      iris: partner in the operation
    inventory: [a vault of NDAs, the original unedited video files]
    secrets: [has been waiting years for someone to take Sloane down]
    notes: Supplies the procedural muscle; Hazel supplies the nerve.
    last_appeared: null
  - id: dara
    name: Dara King
    aliases: [Dara]
    status: alive
    location: Los Angeles
    role: Antagonist - ruthless talent manager who absorbed Hazel's brand
    key_traits: [hungry, transactional, disrespects softness, efficient]
    speech_pattern: deal-talk, "assets", "brand equity", dismissive of feeling
    abilities: [negotiation, repackaging talent, monetizing wreckage]
    relationships:
      hazel: took over her sponsorships after the cancellation
      kai: her main client now
      sloane: business partner
    inventory: [Hazel's old sponsorship contracts, the rebranded "Quinn" merch]
    secrets: [knows the whole frame-up, profits from it]
    notes: Falls first - the money she took becomes the leverage Hazel uses.
    last_appeared: null
  - id: cole
    name: Cole Mercer
    aliases: [Cole]
    status: alive
    location: Los Angeles
    role: Antagonist-turned-ally - Kai's best friend who sold Hazel out
    key_traits: [weak, people-pleasing, guilty, desperate to be liked]
    speech_pattern: nervous, over-explains, cracks under pressure
    abilities: [none - his weakness is the tool]
    relationships:
      hazel: former friend he betrayed - apologizes by ch19
      kai: best friend he enables
    inventory: [the group chat screenshots]
    secrets: [he leaked Hazel's location to the mob that night]
    notes: Gets a redemption beat, not a destruction - the story's mercy case.
    last_appeared: null
  - id: rina
    name: Rina Cho
    aliases: [Rina]
    status: alive
    location: Pasadena
    role: Supporting - Felix's girlfriend
    key_traits: [warm, steady, unimpressed by LA]
    speech_pattern: practical, kind
    abilities: [cooks, keeps secrets, strong moral compass]
    relationships:
      felix: girlfriend
      hazel: future sister-in-law
    notes: Grounds Felix's storyline.
    last_appeared: null
"""

world_yaml = """world:
  setting: Los Angeles, 2026 - the creator-economy ecosystem of influencers, agencies and brand deals
  geography:
    - id: violet-room
      name: The Violet Room
      type: private group chat / inner circle
      location: digital
      status: active
      notes: Kai, Sloane, Dara, Cole + hangers-on. Where the plot against Hazel was born.
    - id: voss-house
      name: Voss House
      type: hillside mansion, Kai's content house
      location: Hollywood Hills
      status: active
      notes: Where the humiliation happened. Kai still lives there with a rotating cast of creators.
    - id: glasshouse
      name: The Glasshouse
      type: cafe / neutral ground
      location: Silver Lake
      status: active
      notes: Where Nell "works" as a barista-adjacent PA. Neutral ground for confrontations.
    - id: factory
      name: The Factory
      type: content house / agency floor
      location: Arts District
      status: active
      notes: Dara King's agency. Hazel's old brand lives here as merchandise.
    - id: haven
      name: The Haven
      type: rooftop bar
      location: Downtown LA
      status: active
      notes: Scene of the public apology + several confrontations. Good view, bad acoustics.
    - id: elysian-fields
      name: Elysian Fields
      type: memorial site (Hazel's fake death spot)
      location: Elysian Park overlook
      status: active
      notes: Where Hazel's phone was "found". Fans leave flowers for a girl who isn't dead.
  factions:
    - id: violet-room
      name: The Violet Room inner circle
      members: [kai, sloane, dara, cole]
      goal: protect the brand at any cost
    - id: teamkay
      name: TeamKai street team
      members: [kai fans]
      goal: stan Kai, destroy his enemies
    - id: the-nells
      name: "The Nells" (in-story fan irony)
      members: [anonymous]
      goal: none yet - planted in ch15, pays off ch24
  power_system:
    - name: Clout
      ranks: [ghost, micro, nano, mid-tier, macro, household]
      rules: >
        Clout is the only currency that matters. Cancellation is the guillotine.
        A single well-timed leak can end a career overnight.
        Receipts beat vibes - a screenshot is worth more than an apology.
  key_objects:
    - id: zero-view-phone
      name: zero-view burner phone
      desc: a phone with no followers, no history - Nell's phone. Hazel's instrument.
    - id: signet-ring
      name: wax-seal signet ring
      desc: Hazel's grandmother's ring. Kai kept it after the breakup. Sloane wears it now. Its return is a turning point.
    - id: evidence-drive
      name: the evidence drive
      desc: every confession, every receipt, every unedited file Marcus and Iris assembled.
    - id: apology-video
      name: the apology video
      desc: a faked, edited apology from Hazel that "resurfaced" to ruin her. Actually manufactured by Sloane.
"""

threads_yaml = """threads:
  - id: t1
    description: Zero-view phone - Nell's burner with no followers becomes the quiet instrument of every takedown
    planted_chapter: 4
    resolved_chapter: 23
    how: The phone's final upload is the receipt that destroys Sloane
    importance: major
    related_characters: [hazel]
  - id: t2
    description: Wax-seal signet ring - Hazel's grandmother's ring, taken by Kai, worn by Sloane; its theft is the personal insult
    planted_chapter: 2
    resolved_chapter: 22
    how: Hazel takes it back from Sloane's wrist in front of witnesses - the "return"
    importance: major
    related_characters: [hazel, kai, sloane]
  - id: t3
    description: Who leaked the location that night - the group chat leak that sent the mob to Hazel's door
    planted_chapter: 1
    resolved_chapter: 19
    how: Cole confesses; his screenshots corroborate
    importance: major
    related_characters: [cole, kai, sloane]
  - id: t4
    description: Sloane orchestrated the entire frame-up (edited apology video, planted evidence, smear campaign)
    planted_chapter: 6
    resolved_chapter: 23
    how: Live broadcast at the Haven - receipts + the unedited video + Kai's confession on tape
    importance: major
    related_characters: [sloane, kai, dara]
  - id: t5
    description: Hazel's fake death - the Elysian Fields memorial
    planted_chapter: 3
    resolved_chapter: 21
    how: Hazel reveals she is alive on her own terms, one fan's letter as the trigger
    importance: major
    related_characters: [hazel, felix, iris]
  - id: t6
    description: Kai still has Hazel's old phone - the one piece of evidence everyone forgot
    planted_chapter: 5
    resolved_chapter: 22
    how: Iris lifts it from Voss House during the finale chaos
    importance: major
    related_characters: [kai, iris]
  - id: t7
    description: Cole's redemption - the betrayer apologizes and pays a small price
    planted_chapter: 9
    resolved_chapter: 24
    how: He testifies publicly with the group chat screenshots
    importance: minor
    related_characters: [cole]
  - id: t8
    description: "The Nells" - anonymous fans who notice Nell is always near the mess; internet subplot
    planted_chapter: 15
    resolved_chapter: 24
    how: They become Hazel's accidental army in the finale
    importance: minor
    related_characters: [hazel]
  - id: t9
    description: Felix's safety - Sloane threatens him to flush Hazel out
    planted_chapter: 17
    resolved_chapter: 21
    how: Hazel gets him out of LA before the finale; he is never used as leverage again
    importance: major
    related_characters: [felix, hazel, sloane]
  - id: t10
    description: Marcus's old grudge - Sloane bankrupted his client years ago with the same playbook
    planted_chapter: 8
    resolved_chapter: 23
    how: The old case files become the legal frame for the new one
    importance: minor
    related_characters: [marcus, sloane]
"""

timeline_yaml = """timeline:
  - chapter: 1
    date: 2026-05-10
    events: [Kai dumps Hazel on a livestream, the group chat leak sends a mob to her door, her world collapses in one night]
  - chapter: 2
    date: 2026-05-11
    events: [The fake apology video surfaces, sponsors drop her, Sloane's machine moves, Hazel's phone vanishes into Kai's pocket]
  - chapter: 3
    date: 2026-05-12
    events: [Hazel disappears; her phone is found at Elysian Fields; the internet mourns a girl who isn't dead]
  - chapter: 4
    date: 2026-05-14
    events: [Iris + Marcus hatch the plan; Hazel becomes Nell; the zero-view phone is born]
  - chapter: 5
    date: 2026-05-18
    events: [Nell "auditions" as a PA at the Glasshouse; Kai walks in; he feels something he can't name]
  - chapter: 6
    date: 2026-05-19
    events: [Nell overhears Sloane's real voice; the frame-up is confirmed; the ring is spotted on Sloane's wrist]
  - chapter: 7
    date: 2026-05-20
    events: [Nell saves the Glasshouse launch event; she is "hired" on the spot; invited closer]
  - chapter: 8
    date: 2026-05-21
    events: [Marcus's history with Sloane resurfaces; the plan gets teeth; first confession collected]
  - chapter: 9
    date: 2026-05-22
    events: [First takedown - Cole's side project collapses via his own leaked confession; Nell plants the fear]
  - chapter: 10
    date: 2026-05-24
    events: [Kai opens up to "sweet Nell"; on-camera charm, off-camera confession about the phone; the ring subplot tightens]
  - chapter: 11
    date: 2026-05-25
    events: [The White Lotus trap for the rival influencer backfires on Sloane - Nell steers it]
  - chapter: 12
    date: 2026-05-26
    events: [Dara's sponsor fraud exposed at the Factory; her empire cracks; Nell's first public recognition]
  - chapter: 13
    date: 2026-05-28
    events: [False win - TeamKai mobs Nell; Sloane cozies up; Hazel feels the pull of the old life]
  - chapter: 14
    date: 2026-05-30
    events: [Felix almost recognizes her; Hazel nearly breaks character; the two halves of her life touch]
  - chapter: 15
    date: 2026-06-01
    events: [The Nells begin; Hazel records the confession that will end Dara for good]
  - chapter: 16
    date: 2026-06-03
    events: [Dara's downfall lands; Sloane smells a rat; the hunt for the leaker begins]
  - chapter: 17
    date: 2026-06-05
    events: [Sloane threatens Felix to flush Hazel out; Hazel's Medea moment - the line she will not cross]
  - chapter: 18
    date: 2026-06-06
    events: [Felix learns the truth; brother and sister reunite in secret; he must leave LA]
  - chapter: 19
    date: 2026-06-08
    events: [Cole breaks - confesses the leak to Nell; his redemption begins]
  - chapter: 20
    date: 2026-06-10
    events: [Sloane discovers Nell is Hazel; the counterstrike - Hazel's new identity is exposed to the Violet Room]
  - chapter: 21
    date: 2026-06-12
    events: [Rock bottom - Hazel is outed as a fake; Felix targeted; everything seems lost; the letter from a stranger saves her nerve]
  - chapter: 22
    date: 2026-06-15
    events: [The gathering at Voss House; Iris lifts the phone; Hazel takes the ring back; the pieces align]
  - chapter: 23
    date: 2026-06-18
    events: [True climax - the Haven live broadcast; receipts drop; Sloane is unmasked on camera in real time]
  - chapter: 24
    date: 2026-06-20
    events: [Aftermath - the ring returns to its owner, the innocent are spared, Hazel chooses who she becomes; epilogue beats]
"""

rules_yaml = """rules:
  - id: r1
    description: The internet never forgets, but it moves on in 48 hours. Timing is everything.
    severity: hard
  - id: r2
    description: Receipts beat vibes. A screenshot or recording outranks any apology.
    severity: hard
  - id: r3
    description: Hazel never destroys an innocent person. Felix is untouchable - the Medea ending is inverted.
    severity: hard
  - id: r4
    description: Nell's cover breaks only when Hazel lets it break - never by accident.
    severity: hard
  - id: r5
    description: Nobody in the Violet Room knows Hazel is alive until ch20.
    severity: hard
"""

arc_tracker_yaml = """arc_tracker:
  current_volume: 1
  current_act: 1
  arc_phase: opening
  planned_chapters: 24
  written_chapters: 0
  total_words: 0
  notes: >
    Act 1 (ch1-8): The Fall + the mask. Act 2 (ch9-16): the slow takedown, false win.
    Act 3 (ch17-24): rock bottom, true climax, mercy.
"""

emotional_debts_yaml = """emotional_debts:
  - id: e1
    debt: Kai's public humiliation of Hazel on 05-10
    owed_by: kai
    owed_to: hazel
    paid_chapter: null
    payoff: Public confession + destroyed brand in the ch23 broadcast
    status: outstanding
  - id: e2
    debt: Sloane's manufactured frame-up and smear campaign
    owed_by: sloane
    owed_to: hazel
    paid_chapter: null
    payoff: Live unmasking at the Haven (ch23) - the white lotus peeled on camera
    status: outstanding
  - id: e3
    debt: Dara absorbing Hazel's sponsorships and merch
    owed_by: dara
    owed_to: hazel
    paid_chapter: null
    payoff: Sponsor fraud exposed (ch16), contracts clawed back
    status: outstanding
  - id: e4
    debt: Cole leaking Hazel's location to the mob
    owed_by: cole
    owed_to: hazel
    paid_chapter: null
    payoff: Public testimony (ch19-24) - mercy, not destruction
    status: outstanding
  - id: e5
    debt: The stolen signet ring
    owed_by: sloane
    owed_to: hazel
    paid_chapter: null
    payoff: Ring returned in front of witnesses (ch22)
    status: outstanding
"""

consistency_log_yaml = """consistency_log:
  entries: []
"""

files = {
    "novel-project.yaml": project_yaml,
    "state/characters.yaml": characters_yaml,
    "state/world.yaml": world_yaml,
    "state/threads.yaml": threads_yaml,
    "state/timeline.yaml": timeline_yaml,
    "state/rules.yaml": rules_yaml,
    "state/arc-tracker.yaml": arc_tracker_yaml,
    "state/emotional-debts.yaml": emotional_debts_yaml,
    "state/consistency-log.yaml": consistency_log_yaml,
}

for rel, content in files.items():
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path, len(content), "chars")
