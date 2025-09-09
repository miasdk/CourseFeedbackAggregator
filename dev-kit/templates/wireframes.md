# Course Feedback Intelligence - Wireframe Specifications

## Main Dashboard (1440px x 900px)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HEADER (80px height)                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ [🎓 Course Feedback Intelligence]  [Dashboard][My Courses][Reports]  [⚙️][👤] │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ FILTER BAR (60px height)                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [All Courses ▼] [Fall 2024 ▼] [All Priorities ▼]              [Export Report]│
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ MAIN CONTENT AREA                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Priority Queue                                                               │
│ Issues ranked by student impact and urgency                                 │
│                                                                              │
│ ┌─ 🔴 CRITICAL ISSUES (3) ──────────────────────────────────────────────────┐│
│ │                                                                            ││
│ │ ┌─ ISSUE CARD ─────────────────────────────────────────────────────────┐  ││
│ │ │ IT Leadership Module 3: Video Content Inconsistency             │🔴│  ││
│ │ │                                                                  │  │  ││
│ │ │ Impact: 9.2  │  Students: 23  │  Sources: Canvas + Zoho         │  │  ││
│ │ │                                                                  │  │  ││
│ │ │ 💬 "Video 1 and Video 2 talk about different attributes -       │  │  ││
│ │ │     this offers inconsistency and confuses the concepts"        │  │  ││
│ │ │                                                                  │  │  ││
│ │ │ [Why This Priority?] [View Details] [Mark Reviewed]             │  │  ││
│ │ └──────────────────────────────────────────────────────────────────────┘  ││
│ │                                                                            ││
│ │ ┌─ ISSUE CARD ─────────────────────────────────────────────────────────┐  ││
│ │ │ Customer Experience: Missing Implementation Examples         │🔴│  ││
│ │ │ Impact: 8.7  │  Students: 19  │  Last reported: 1 day ago      │  │  ││
│ │ │ 💬 "Need concrete examples of how to apply these frameworks"    │  │  ││
│ │ │ [Why This Priority?] [View Details] [Mark Reviewed]             │  │  ││
│ │ └──────────────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│ ┌─ 🟠 HIGH PRIORITY (7) ────────────────────────────────────────────────────┐│
│ │                                                                            ││
│ │ ┌─ ISSUE CARD ─────────────────────────────────────────────────────────┐  ││
│ │ │ Strategic Leadership: Assignment Instructions Unclear           │🟠│  ││
│ │ │ Impact: 6.8  │  Students: 15  │  Effort: Low (< 1 hour)         │  │  ││
│ │ │ 💬 "Assignment requirements are vague and confusing"            │  │  ││
│ │ │ [Why This Priority?] [View Details] [Mark Reviewed]             │  │  ││
│ │ └──────────────────────────────────────────────────────────────────────┘  ││
│ └────────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│ ┌─ 🟡 MEDIUM PRIORITY (12) ─────────────────────────────────────────────────┐│
│ │ [Show More ▼]                                                              ││
│ └────────────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
```

## Score Breakdown Modal (400px x 500px)

```
┌──────────────────────────────────────────────────────────────┐
│ Why is this Priority Score 8.7?                         [×] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ FACTOR BREAKDOWN                                             │
│                                                              │
│ Impact                                               9.2/10  │
│ ████████████████████████████████████████████████████░░      │
│ 23 students affected (48% of enrolled class)                │
│                                                              │
│ Urgency                                              8.5/10  │
│ ██████████████████████████████████████████████████░░░░      │
│ Blocking current week progress, mentioned 5x this week      │
│                                                              │
│ Effort                                               6.0/10  │
│ ██████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░      │
│ Estimated 2-4 hours to re-record videos                     │
│                                                              │
│ Strategic                                            7.0/10  │
│ ██████████████████████████████████████░░░░░░░░░░░░░░░░      │
│ Core concept, affects downstream modules                    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ STUDENT EVIDENCE (5 reports)                                │
│                                                              │
│ 📍 Canvas Discussion - Sept 5, 2024                         │
│ "I'm confused by the contradicting information in videos    │
│  1 and 2. Which approach should we use for the project?"    │
│                                                              │
│ 📍 Zoho Survey - Module 3 Feedback                          │
│ "Videos don't match the reading material. Very confusing."  │
│                                                              │
│ 📍 Canvas Assignment Comments - Sept 6, 2024                │
│ "Can you clarify which video is correct? Getting mixed      │
│  signals on the implementation approach."                    │
│                                                              │
│ [View All Evidence] [View Original Sources]                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Course Detail View

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ IT Leadership in Digital Transformation                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ 📊 Overall Health: 7.2/10    👥 47 Students    📅 Week 6 of 12    🎯 87% Active│
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ MODULE HEALTH OVERVIEW                                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ ┌─ Module 1: Introduction ────────┐ ┌─ Module 2: Strategic Planning ─────┐   │
│ │ Health: ✅ 8.9                   │ │ Health: ⚠️ 6.2                     │   │
│ │ 47 students completed            │ │ 45 students completed              │   │
│ │ No major issues reported         │ │ 3 issues reported                  │   │
│ └──────────────────────────────────┘ └─────────────────────────────────────┘   │
│                                                                              │
│ ┌─ Module 3: Implementation ──────┐ ┌─ Module 4: Leadership & Change ────┐   │
│ │ Health: 🔴 4.1                   │ │ Health: ✅ 8.5                     │   │
│ │ 41 students completed            │ │ 38 students completed              │   │
│ │ 5 critical issues (VIDEO PROB)  │ │ Generally positive feedback        │   │
│ └──────────────────────────────────┘ └─────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ IMMEDIATE ACTIONS NEEDED                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 🔥 CRITICAL (Fix This Week)                                                  │
│ • Fix Module 3 video inconsistency → 23 students affected                   │
│ • Add implementation examples to Module 3 readings → 19 requests            │
│                                                                              │
│ ⚡ QUICK WINS (< 30 minutes)                                                 │
│ • Clarify Assignment 2 requirements → 12 confused students                  │
│ • Add FAQ entry for common Module 2 question → 8 similar questions          │
│                                                                              │
│ 📅 PLAN FOR NEXT SEMESTER                                                    │
│ • Consider splitting Module 3 into two parts → pacing issues reported       │
│ • Update Module 2 sequence based on feedback patterns                       │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Configuration Panel (350px width, slide-out)

```
┌─────────────────────────────────────────────────┐
│ Configure Priority Scoring                [×]  │
├─────────────────────────────────────────────────┤
│                                                 │
│ SCORING WEIGHTS                                 │
│                                                 │
│ Impact Weight                            35%    │
│ ●────●────────────────── [        ]            │
│ How much student impact affects priority        │
│                                                 │
│ Urgency Weight                           25%    │
│ ●──●──────────────────── [        ]            │
│ Time sensitivity of the issue                   │
│                                                 │
│ Effort Weight                            20%    │
│ ●─●───────────────────── [        ]            │
│ Implementation difficulty (inverse)             │
│                                                 │
│ Strategic Weight                         15%    │
│ ●─────────────────────── [        ]            │
│ Alignment with course goals                     │
│                                                 │
│ Trend Weight                             5%     │
│ ●────────────────────── [        ]             │
│ Getting worse vs. improving                     │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ LIVE PREVIEW                                    │
│ Current top issue score: 8.7 → 8.2             │
│                                                 │
│ [Apply Changes] [Reset to Defaults]             │
│                                                 │
└─────────────────────────────────────────────────┘
```