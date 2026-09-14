#!/usr/bin/env python3
"""Emit app/data.js — the bank the dashboard ships with, plus experience metadata.
Canonical experience values come from the Sept 14 2026 CV (her current format)."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
B = json.loads((ROOT/"data"/"bullets.json").read_text(encoding="utf-8"))

EXPERIENCES = [
 {"id":"walmart","org":"Walmart Marketplace","role":"Senior Product Manager – Global Shopping Experiences",
  "loc":"Bay Area","dates":"2024 – August 2026","section":"EXPERIENCE","order":1,
  "descriptor":"AI/ML marketplace platform surfacing the fastest, cheapest offer so shoppers keep coming back; ~400M daily impressions"},
 {"id":"siemens","org":"Siemens eMobility","role":"MBA Intern – Global Product Management and Strategy",
  "loc":"Remote","dates":"2023","section":"EXPERIENCE","order":2,
  "descriptor":"New venture incubating SaaS product for electric vehicle charging"},
 {"id":"uprising","org":"Uprising VC","role":"Director of Platform (Product) (2021-2022); Chief of Staff (2019-2021)",
  "loc":"San Francisco, CA","dates":"2019 – 2022","section":"EXPERIENCE","order":3,
  "descriptor":"First hire at a tech-focused VC managing $750M+ across a portfolio of 30 startups and 300+ investors"},
 {"id":"accenture","org":"Accenture","role":"Senior Consulting Analyst (2018-2019); Consulting Analyst (2017-2018)",
  "loc":"San Francisco, CA","dates":"2017 – 2019","section":"EXPERIENCE","order":4,
  "descriptor":"Management, operations, and strategy for marketplace tech clients in Silicon Valley"},
 {"id":"muse","org":"Muse Shopping","role":"Founder","loc":"muse.shopping","dates":"2026 – Present",
  "section":"AI PROJECTS & VENTURES","order":5,
  "descriptor":"Agentic shopping platform unifying 13K+ products across 264 brands and 10 retailers, enabling shoppers to build one cart"},
 {"id":"aiprojects","org":"Applied AI Project Portfolio","role":"","loc":"schlacter.me","dates":"2026 – Present",
  "section":"AI PROJECTS & VENTURES","order":6,
  "descriptor":"20+ AI products coded, tested, and shipped E2E on full-stack toolkit: Claude Code, Codex, Vercel, Docker, API integrations"},
 {"id":"coherent","org":"Coherent Finance","role":"Co-founder","loc":"","dates":"2021 – 2022",
  "section":"AI PROJECTS & VENTURES","order":7,
  "descriptor":"Consumer investing product enabling retail investors to map their investment portfolio to their ethics and values"},
 {"id":"edu_berkeley","org":"University of California, Berkeley, Haas School of Business","role":"Master of Business Administration",
  "loc":"Berkeley, CA","dates":"May 2024","section":"EDUCATION, SKILLS, & INTERESTS","order":8,
  "descriptor":"Merit Scholarship, Beyond Yourself Fellowship"},
 {"id":"edu_illinois","org":"University of Illinois at Urbana-Champaign, Gies College of Business",
  "role":"Bachelor of Science in Marketing and Management","loc":"Champaign, IL","dates":"May 2017",
  "section":"EDUCATION, SKILLS, & INTERESTS","order":9,
  "descriptor":"Graduated High Honors, Gies Scholars, Merit Scholarship"},
 {"id":"community","org":"Community Impact","role":"","loc":"","dates":"","section":"EDUCATION, SKILLS, & INTERESTS","order":10,
  "descriptor":"National student advocacy; Congressional testimony; featured in CNN, Fox, Forbes"},
 {"id":"misc","org":"Unfiled","role":"","loc":"","dates":"","section":"EDUCATION, SKILLS, & INTERESTS","order":11,"descriptor":""},
]

# Base prototypes. Taglines are Hannah's real ones from resume.md + her live CVs.
PROFILES = [
 {"id":"ai-native","name":"Applied AI / AI-native","baseDoc":"1EKpnxTaPTSPVAelGQcFmvMo_u_1MirgzY8KRRqRweW8","baseName":"Owner-Applied AI Lead",
  "tagline":"Applied AI operator and 0-to-1 builder who maps where AI pays off across a business, then ships until the KPI moves",
  "archetypes":["ai-native","platform-ml"],
  "skills":"AI opportunity identification and sizing | LLM agents (structured output, evals, context engineering) | ML ranking feature design | Growth experimentation and A/B testing | SQL and Python analytics"},
 {"id":"ecomm-marketplace","name":"eComm / Marketplace","baseDoc":"13rjsdK48xh23ESC-6i9qHtfEWQlHtqqr7PUgXBwRIRc","baseName":"Google-ConsumerShopping",
  "tagline":"Product Manager shaping how ~400M daily shoppers discover, research, and buy, with ML ranking and agentic AI",
  "archetypes":["ecomm-marketplace","consumer-growth"],
  "skills":"AI prototyping with Claude Code and Cursor | Growth experimentation and A/B testing | Monetization and pricing models | Conversion and funnel optimization | SQL and Python analytics"},
 {"id":"enterprise-b2b","name":"Enterprise / B2B AI","baseDoc":"1cjq2582rYFCc-_YURg1aKLx-cfnsdQgYnnBDUSwYOcw","baseName":"Front-SeniorPM-AI",
  "tagline":"Product Manager focused on growth and adoption of AI-powered products with experience running experimentation and conversion optimization at scale",
  "archetypes":["enterprise-b2b","ai-native"],
  "skills":"AI product prototyping | Agentic AI and multi-agent systems | ML-powered product systems | Enterprise adoption and enablement | Cross-functional product leadership"},
 {"id":"platform-ml","name":"Platform / ML systems","baseDoc":"1rqzBZm0QdaLtUHj0svrDjEawQImT9WMPGFIuq0A-bhY","baseName":"Scale-SPL-GenAI",
  "tagline":"Product Manager focused on growth and adoption of AI-powered products with experience running experimentation on ML-driven products at scale",
  "archetypes":["platform-ml","ai-native"],
  "skills":"ML ranking systems | Agentic AI and evals | API and data contract design | Growth experimentation | Product analytics (SQL, Python)"},
 {"id":"ops-generalist","name":"Ops / Chief of Staff","baseDoc":"1wyV199o9eyc9cJlBVADpe7vu-YYR5DyGE1KDyXAC3VY","baseName":"Constellation-OpsGeneralist",
  "tagline":"Forward-deployed operator shipping the durable mechanisms — playbooks, automation, dashboards, feedback loops — that scale delivery",
  "archetypes":["ops-generalist","enterprise-b2b"],
  "skills":"Operating cadence and playbooks | Workflow automation | Stakeholder and executive management | Product analytics (SQL, Python) | AI prototyping with Claude Code"},
 {"id":"consumer-growth","name":"Consumer / Growth","baseDoc":"1vWGRD6SIIS9a_0fha7TVMEnGL984AmGkt71D6Cq-BI8","baseName":"Babylist-PM",
  "tagline":"Product Manager building AI-powered products with experience operating ML systems used by millions",
  "archetypes":["consumer-growth","ecomm-marketplace"],
  "skills":"AI product prototyping | Growth experimentation and A/B testing | Conversion optimization | Personalization systems | Product analytics (SQL, Python)"},
]

HEADER = {"name":"Hannah Schlacter",
          "contact":"847-404-8501 | hbschlac@gmail.com | linkedin.com/in/hannahschlacter | schlacter.me",
          "interests":"Hosting dinner parties; online shopping; baking; skiing; painting; travel; historical fiction; international relations"}

SECTION_ORDER = ["EXPERIENCE","AI PROJECTS & VENTURES","EDUCATION, SKILLS, & INTERESTS"]

out = {"bullets":B["bullets"],"anomalies":B["anomalies"],"experiences":EXPERIENCES,
       "profiles":PROFILES,"header":HEADER,"sectionOrder":SECTION_ORDER}
js = "window.BANK=" + json.dumps(out, ensure_ascii=False, separators=(",",":")) + ";"
(ROOT/"app").mkdir(exist_ok=True)
(ROOT/"app"/"data.js").write_text(js, encoding="utf-8")
print(f"wrote app/data.js  {len(js):,} bytes  bullets={len(B['bullets'])}")
