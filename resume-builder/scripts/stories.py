#!/usr/bin/env python3
"""Story layer: collapse ~1000 bullet variants into the handful of things that actually happened.

Hannah, 2026-09-15: "you are showing me 290 bullets to sort through? are these all unique?
what are the overall takeaways? the idea is that we can use whatever verbs we want to tell a
story but the baseline story should really only be like 5-10 max."

She is right, and the cause is mechanical: enrich.py dedupes by NORMALISED STRING. Two bullets
that describe the same launch in different words are different strings, so both survive. The
bank was therefore a bank of *phrasings*, with no layer for the thing being phrased.

This file adds that layer. A STORY is one real accomplishment. A bullet is one telling of it.
The table below is hand-written on purpose -- these are facts about Hannah's career, not
clusters to be discovered, and they belong somewhere she can read and edit them.

Assignment is scored, not first-match: every anchor a bullet hits adds its weight, and the
highest-scoring story wins. Specific proper nouns ("secondary buy box") carry heavy weight;
generic terms ("ranking") carry ~1 so they only break ties. `veto` terms subtract, for the
cases where two stories share vocabulary (the GenAI agent and the dependency map both say
"10+ upstream systems" -- the agent is the one that says "agent").

Anything scoring below MIN_SCORE lands in the experience's `-other` story rather than being
forced into a wrong one. Coverage is printed by enrich.py; a growing `-other` bucket means
this table needs a new entry, not a lower threshold.
"""
from __future__ import annotations

# weight, term  -- term is matched as a lowercase substring
W_NAME, W_STRONG, W_MED, W_WEAK = 10, 5, 2, 1

STORIES = {
 "walmart": [
  {"id": "wm-charter", "title": "Owned the ML ranking charter behind the Buy Box",
   "gist": "The scope bullet: ~30% of Walmart Marketplace, ~400M daily product page views, a $400M+ revenue charter. This is the one that establishes how big the job was.",
   "anchors": [(W_NAME,"buy box winner"),(W_NAME,"buybox winner"),(W_STRONG,"400m daily"),
               (W_STRONG,"$400m"),(W_STRONG,"revenue charter"),(W_STRONG,"~30% of"),
               (W_MED,"charter"),(W_MED,"opportunity map"),(W_MED,"roadmap"),
               (W_MED,"which seller"),(W_MED,"which offer"),(W_STRONG,"eligibility standard"),
               (W_STRONG,"winning path"),(W_STRONG,"local marketplace"),(W_STRONG,"localmarketplace"),
               (W_STRONG,"preowned"),(W_WEAK,"ranking system"),
               (W_WEAK,"owned"),(W_WEAK,"marketplace")],
   "veto":    [(W_STRONG,"secondary buy"),(W_STRONG,"buybox engineer"),(W_STRONG,"genai"),
               (W_MED,"initiatives/q"),(W_MED,"investigation time")]},

  {"id": "wm-secondary", "title": "Launched the Secondary Buy Box 0-to-1",
   "gist": "New item-page module that surfaced a previously invisible second offer. ~45M daily impressions, +0.46% multi-offer add-to-cart. The 0-to-1 launch story.",
   "anchors": [(W_NAME,"secondary buy box"),(W_NAME,"secondary buybox"),(W_STRONG,"45m"),
               (W_STRONG,"0.46%"),(W_STRONG,"previously unseen"),(W_STRONG,"second seller"),
               (W_STRONG,"item page module"),(W_STRONG,"multi-offer"),(W_MED,"new item page"),
               (W_MED,"daily impressions"),(W_WEAK,"0-to-1"),(W_WEAK,"0→1")],
   "veto":    [(W_STRONG,"buybox engineer"),(W_STRONG,"genai agent")]},

  {"id": "wm-agent", "title": "Built BuyBox Engineer, a GenAI diagnostic agent",
   "gist": "Side prototype nobody asked for that became an internal agent answering diagnostic questions across 10+ upstream systems, adopted across a 200+ person org. The AI-native story.",
   "anchors": [(W_NAME,"buybox engineer"),(W_NAME,"buy box engineer"),(W_STRONG,"genai"),
               (W_STRONG,"llm assistant"),(W_STRONG,"gen ai"),(W_STRONG,"ai agent"),
               (W_STRONG,"diagnostic agent"),(W_MED,"agent"),(W_MED,"assistant"),
               (W_MED,"200+ person"),(W_MED,"eval"),(W_MED,"prd"),(W_MED,"diagnostic question"),
               (W_WEAK,"prototype"),(W_WEAK,"self-serve")],
   "veto":    [(W_STRONG,"secondary buy")]},

  {"id": "wm-deps", "title": "Made 10+ upstream systems legible",
   "gist": "The SQL dependency map that cut engineering investigation time ~80%, and the deterministic ranking and monetization contracts that pinned down how intent, sponsorship and eligibility signals decide a winner. Same work, two framings: diagnosis and definition.",
   "anchors": [(W_STRONG,"investigation time"),(W_STRONG,"dependenc"),(W_STRONG,"80%"),
               (W_STRONG,"api contract"),(W_STRONG,"data model"),(W_STRONG,"signal contract"),
               (W_STRONG,"ranking contract"),(W_STRONG,"monetization contract"),
               (W_STRONG,"deterministic"),(W_MED,"mapped"),(W_MED,"sponsorship"),
               (W_MED,"upstream"),(W_MED,"sql"),(W_MED,"incident"),(W_MED,"eligibility"),
               (W_WEAK,"production issue")],
   "veto":    [(W_NAME,"buybox engineer"),(W_STRONG,"genai"),(W_MED,"agent")]},

  {"id": "wm-experiments", "title": "Shipped the flagship ranking experiments",
   "gist": "Popularity Signal and Data Refresh: ~$107M-$137M in GMV, +0.66% item-page add-to-cart, +7% YoY, rolled to 100% across web, mobile and app. The experimentation story.",
   "anchors": [(W_NAME,"popularity signal"),(W_NAME,"data refresh"),(W_STRONG,"0.66%"),
               (W_STRONG,"$107m"),(W_STRONG,"$137m"),(W_STRONG,"0.87%"),(W_STRONG,"a/b"),
               (W_STRONG,"+7%"),(W_STRONG,"1.51%"),(W_STRONG,"ship-speed"),
               (W_STRONG,"l1 category"),(W_STRONG,"badge runtime"),(W_STRONG,"ship-price"),
               (W_MED,"experiment"),(W_MED,"guardrail"),(W_MED,"lift"),
               (W_MED,"data-signal"),(W_MED,"3p conversion"),
               (W_MED,"add-to-cart"),(W_WEAK,"rollout")],
   "veto":    [(W_NAME,"secondary buy box"),(W_NAME,"buybox engineer")]},

  {"id": "wm-opsystem", "title": "Built the operating system for 30+ initiatives a quarter",
   "gist": "Prioritization framework plus an AI-enabled tracking dashboard sequencing ~30 initiatives/quarter across 20+ partner teams. The ops / program-management story.",
   "anchors": [(W_STRONG,"initiatives/q"),(W_STRONG,"initiatives per quarter"),
               (W_STRONG,"prioritization framework"),(W_STRONG,"governance model"),
               (W_STRONG,"operating platform"),(W_STRONG,"operating system"),
               (W_MED,"30+ "),(W_MED,"dashboard"),(W_MED,"prioriti"),(W_MED,"sequenc"),
               (W_MED,"partner teams"),(W_STRONG,"quarterly business review"),(W_STRONG,"qbr"),
               (W_STRONG,"holiday peak"),(W_STRONG,"launch readiness"),(W_MED,"intake"),
               (W_WEAK,"initiative")],
   "veto":    [(W_NAME,"secondary buy box"),(W_NAME,"buybox engineer"),(W_STRONG,"genai")]},

  {"id": "wm-trust", "title": "Held the line on customer trust against seller pressure",
   "gist": "Paused a launch to fix broken image rendering; set guardrails that favoured shoppers over seller interests; +0.28% offer relevancy. The judgment / principles story.",
   "anchors": [(W_STRONG,"image render"),(W_STRONG,"customer trust"),(W_STRONG,"0.28%"),
               (W_STRONG,"seller interest"),(W_STRONG,"pause"),(W_MED,"championed"),
               (W_MED,"trust"),(W_MED,"shopper"),(W_MED,"buy-in"),(W_WEAK,"guardrail")],
   "veto":    [(W_NAME,"secondary buy box"),(W_NAME,"buybox engineer")]},

  {"id": "wm-runops", "title": "Ran the live ranking system day to day",
   "gist": "Triaged model output for false positives and negatives, drove production incidents to root cause with on-call engineering, and monitored live model behaviour across Search to PDP. The operate-it story, not the launch-it story.",
   "anchors": [(W_STRONG,"false positive"),(W_STRONG,"on-call"),(W_STRONG,"root-cause"),
               (W_STRONG,"live model"),(W_STRONG,"model performance"),(W_STRONG,"triaged"),
               (W_STRONG,"production ranking incident"),(W_STRONG,"winning-offer"),
               (W_MED,"monitor"),(W_MED,"diagnose"),(W_MED,"discrepanc"),(W_MED,"daily"),
               (W_MED,"search →"),(W_WEAK,"incident")],
   "veto":    [(W_NAME,"buybox engineer"),(W_STRONG,"genai")]},

  {"id": "wm-availability", "title": "Wired live availability and delivery speed into ranking",
   "gist": "System integration feeding real availability and delivery-promise data into the ranking model so surfaced offers were actually buyable; cut out-of-stock exposure.",
   "anchors": [(W_STRONG,"out-of-stock"),(W_STRONG,"delivery speed"),(W_STRONG,"availability"),
               (W_STRONG,"delivery promise"),(W_MED,"system integration"),(W_MED,"shoppable")]},
 ],

 "uprising": [
  {"id": "up-kpi", "title": "Built KPI reporting across 30 portfolio startups",
   "gist": "Set strategy for a product collecting performance data from 30 startups (churn, ARR); evangelised rollout and got it adopted. The 0-to-1 internal product story.",
   "anchors": [(W_STRONG,"30 startups"),(W_STRONG,"kpi report"),(W_STRONG,"arr"),
               (W_STRONG,"churn"),(W_MED,"kpi"),(W_MED,"portfolio"),(W_MED,"performance data"),
               (W_MED,"evangeliz"),(W_MED,"evangelis"),(W_STRONG,"portfolio tracker"),
               (W_STRONG,"performance dashboard"),(W_MED,"data collection"),
               (W_WEAK,"reporting")]},

  {"id": "up-prorata", "title": "Shipped the self-serve pro-rata tool",
   "gist": "Mapped pain points across five customer segments, built the calculator that showed investors what they could put into the next round; ~95% adoption, $100M+ moved in two months.",
   "anchors": [(W_STRONG,"pro rata"),(W_STRONG,"pro-rata"),(W_STRONG,"five customer segment"),
               (W_STRONG,"$100m"),(W_STRONG,"95%"),(W_STRONG,"calculator"),
               (W_MED,"self-serve"),(W_MED,"segment"),(W_MED,"pain point"),
               (W_MED,"conversion"),(W_WEAK,"adoption")]},

  {"id": "up-governance", "title": "Designed access governance for investor-facing products",
   "gist": "Permission and information-access model across every investor-facing investment product. The enterprise / trust-and-safety-adjacent story.",
   "anchors": [(W_STRONG,"access governance"),(W_STRONG,"information access"),
               (W_STRONG,"permission"),(W_MED,"governance"),(W_MED,"investor-facing"),
               (W_MED,"compliance"),(W_WEAK,"access")]},

  {"id": "up-fundraises", "title": "Ran seven fundraises into $400M+ raised",
   "gist": "Prioritisation and resource allocation across seven concurrent fundraises; phased roadmaps with real dependencies. The scale-of-capital story -- the charter, not the GMV.",
   "anchors": [(W_STRONG,"seven fundrais"),(W_STRONG,"seven investment"),(W_STRONG,"$400m"),
               (W_STRONG,"capital raised"),(W_STRONG,"fundrais"),(W_MED,"phased roadmap"),
               (W_MED,"resource allocation"),(W_MED,"investment sprint"),(W_WEAK,"partnership")]},

  {"id": "up-research", "title": "Turned user research into shipped platform improvements",
   "gist": "Customer interviews folded straight into technical requirements and prototypes. The discovery-to-delivery story.",
   "anchors": [(W_STRONG,"user research interview"),(W_STRONG,"three user research"),
               (W_STRONG,"technical requirement"),(W_MED,"prototype"),(W_MED,"interview"),
               (W_MED,"platform efficiency"),(W_WEAK,"user research")]},

  {"id": "up-execops", "title": "Owned the executive cadence and everything investors read",
   "gist": "The bi-weekly executive meeting and the prioritisation feeding it, plus every investor-facing product and piece of collateral -- the 50-page quarterly report, the LP Annual Meeting, the reporting systems the managing partners ran on. Cut reporting cycle time 80%.",
   "anchors": [(W_STRONG,"executive team meeting"),(W_STRONG,"bi-weekly"),
               (W_STRONG,"leadership decision"),(W_STRONG,"quarterly report"),
               (W_STRONG,"annual meeting"),(W_STRONG,"reporting cycle"),
               (W_STRONG,"investor-facing"),(W_STRONG,"marketing collateral"),
               (W_STRONG,"executive reporting"),(W_STRONG,"read-rate"),
               (W_MED,"managing partner"),(W_MED,"50-page"),(W_MED,"executive"),
               (W_STRONG,"quarterly investor report"),(W_STRONG,"75%"),(W_STRONG,"quarterly project"),
               (W_MED,"cadence"),(W_MED,"digital design tool"),(W_MED,"template"),
               (W_MED,"workflow"),(W_WEAK,"decision making")]},

  {"id": "up-dashboard", "title": "Built the planning dashboard the firm ran on",
   "gist": "The single most-reused bullet in the whole archive (101 CVs). Collaboration and planning dashboard tracking investment operations and cross-team resource allocation across legal, marketing and finance; secured buy-in from the CFO and three managing partners; 3x organizational capacity.",
   "anchors": [(W_STRONG,"planning dashboard"),(W_STRONG,"collaboration/planning"),
               (W_STRONG,"resource management"),(W_STRONG,"organizational capacity"),
               (W_STRONG,"3x"),(W_STRONG,"cfo"),(W_STRONG,"investment operations"),
               (W_MED,"excel"),(W_MED,"managing partner"),(W_MED,"deal flow"),
               (W_MED,"program management"),(W_WEAK,"dashboard")]},

  {"id": "up-founders", "title": "Advised portfolio founders",
   "gist": "Product, ops and GTM advice to portfolio CEOs -- marketing funnel strategy, prototype testing, national partnerships. The outward-facing half of the role.",
   "anchors": [(W_STRONG,"advised founders"),(W_STRONG,"portfolio ceo"),
               (W_STRONG,"marketing funnel"),(W_STRONG,"30 portfolio"),
               (W_MED,"founders"),(W_MED,"value proposition"),(W_MED,"partnership")]},

  {"id": "up-investorops", "title": "Built investor operations from nothing",
   "gist": "Outreach to 500+ investors, the vendor ops playbook, the investment artifacts. The build-the-function story.",
   "anchors": [(W_STRONG,"500+ investors"),(W_STRONG,"vendor ops"),(W_STRONG,"playbook"),
               (W_STRONG,"investment artifact"),(W_STRONG,"tech vendor"),
               (W_STRONG,"deal flow"),(W_STRONG,"firm liaison"),(W_STRONG,"community infrastructure"),
               (W_STRONG,"legal process"),(W_STRONG,"vc pipeline"),
               (W_MED,"outreach"),(W_MED,"fund admin"),(W_MED,"vendor"),(W_MED,"legal"),
               (W_WEAK,"operations")]},

  {"id": "up-chiefofstaff", "title": "First-ever Chief of Staff; built the firm's operating system",
   "gist": "No prior tech-operations foundation existed. Built internal workflow tools and customer-facing investor products that enabled 2x capital deployment. The framing bullet for the whole role.",
   "anchors": [(W_STRONG,"first-ever chief of staff"),(W_STRONG,"chief of staff"),
               (W_STRONG,"internal operating system"),(W_STRONG,"no prior"),
               (W_STRONG,"2x capital"),(W_MED,"internal workflow"),(W_MED,"first")]},
 ],

 "siemens": [
  {"id": "si-gtm", "title": "Created the 0-to-1 GTM strategy for EV charging software",
   "gist": "Go-to-market and expansion plan for a new SaaS offering; the executive recommendation informed how they scaled adoption.",
   "anchors": [(W_STRONG,"go-to-market"),(W_STRONG,"expansion strategy"),(W_STRONG,"gtm"),
               (W_STRONG,"g2m"),(W_STRONG,"launch plan"),(W_MED,"ev charging"),(W_MED,"scale customer adoption"),
               (W_MED,"commercial"),(W_WEAK,"strategy")]},
  {"id": "si-research", "title": "Ran the market and competitive analysis",
   "gist": "Interviewed industry experts to map the value chain and build the business case from scratch in an unfamiliar domain.",
   "anchors": [(W_STRONG,"competitive analysis"),(W_STRONG,"value chain"),
               (W_STRONG,"industry expert"),(W_STRONG,"market analysis"),(W_MED,"business case"),
               (W_MED,"domain expertise"),(W_WEAK,"market")]},
  {"id": "si-xfn", "title": "Led a 10-person cross-functional team to requirements",
   "gist": "Data science, engineering and design in one room; turned customer needs into the requirement set they built against.",
   "anchors": [(W_STRONG,"cross-functional team of 10"),(W_STRONG,"10-person"),
               (W_STRONG,"user requirement"),(W_MED,"data science, engineering"),
               (W_MED,"customer needs"),(W_WEAK,"cross-functional")]},
  {"id": "si-roadmap", "title": "Defined the product roadmap and pitched execs on new revenue",
   "gist": "15+ stakeholder interviews into a roadmap, plus an unprompted pitch to executives on revenue streams beyond the original scope. Projected ~6x lifetime-value growth.",
   "anchors": [(W_STRONG,"6x"),(W_STRONG,"lifetime customer value"),(W_STRONG,"lifetime-value"),
               (W_STRONG,"revenue stream"),(W_STRONG,"15+ "),(W_MED,"roadmap"),
               (W_MED,"monetization"),(W_MED,"pitched exec")]},
  {"id": "si-pricing", "title": "Built the SaaS costing and pricing models",
   "gist": "Data-driven pricing work that fed the executive go-to-market decision.",
   "anchors": [(W_STRONG,"pricing model"),(W_STRONG,"costing"),(W_STRONG,"roi"),
               (W_MED,"pricing"),(W_MED,"saas"),(W_MED,"business case"),(W_MED,"model")]},
 ],

 "accenture": [
  {"id": "ac-assets", "title": "Shipped the asset production planning tool",
   "gist": "Product enhancement requirements for a cross-functional team of engineers, marketers and designers; adopted by 50+ stakeholders across 5+ teams.",
   "anchors": [(W_STRONG,"asset production"),(W_STRONG,"50+ stakeholder"),
               (W_MED,"production planning"),(W_STRONG,"enhancement requirement"),
               (W_MED,"organizational effectiveness"),(W_MED,"organizational efficiency"),
               (W_WEAK,"designers")]},
  {"id": "ac-staffing", "title": "Built the staffing model calculator for a VP",
   "gist": "Technical requirements plus 15 user interviews behind a calculator the VP used on national 100-person headcount and per-market productivity ratios.",
   "anchors": [(W_STRONG,"staffing model"),(W_STRONG,"100-person headcount"),
               (W_STRONG,"productivity per worker"),(W_STRONG,"calculator"),
               (W_STRONG,"capacity model"),(W_STRONG,"demand forecast"),(W_STRONG,"cost categories"),
               (W_MED,"headcount"),(W_MED,"15 user interview"),(W_MED,"capacity")]},
  {"id": "ac-allocation", "title": "Doubled team productivity through resource allocation",
   "gist": "Resource allocation optimisation that took team productivity to 2x and pulled in delivery dates.",
   "anchors": [(W_STRONG,"resource allocation"),(W_STRONG,"2x"),(W_STRONG,"doubled"),
               (W_MED,"productivity"),(W_WEAK,"optimization")]},
  {"id": "ac-vp", "title": "Embedded as day-to-day advisor to a VP",
   "gist": "Translated ambiguous executive requirements into internal products that actually got used. The ambiguity / exec-partnership story.",
   "anchors": [(W_STRONG,"day-to-day advisor"),(W_STRONG,"ambiguous"),(W_STRONG,"embedded"),
               (W_MED,"vp"),(W_WEAK,"advisor")]},
  {"id": "ac-labeling", "title": "Ran human-in-the-loop labeling for an image model",
   "gist": "Matched, labeled and triaged image training data end to end for a client's image-recognition model. The rare hands-on-ML-data story.",
   "anchors": [(W_STRONG,"labeling"),(W_STRONG,"labelling"),(W_STRONG,"human-in-the-loop"),
               (W_STRONG,"image-recognition"),(W_MED,"training data"),(W_MED,"annotat")]},
  {"id": "ac-cmo", "title": "Re-modeled the digital marketing budget for an e-commerce CMO",
   "gist": "Consolidated a 6-week campaign process and rebuilt how the budget was allocated.",
   "anchors": [(W_STRONG,"marketing budget"),(W_STRONG,"cmo"),(W_STRONG,"campaign process"),
               (W_STRONG,"campaign performance"),(W_STRONG,"six weeks"),
               (W_MED,"6-week"),(W_MED,"digital marketing")]},
 ],

 "muse": [
  {"id": "mu-platform", "title": "Architected the agentic checkout platform",
   "gist": "Single-cart checkout routed across 264 brands and 10 retailers via Stripe -- kills the re-auth drop-off that breaks multi-retailer conversion.",
   "anchors": [(W_STRONG,"agentic checkout"),(W_STRONG,"stripe"),(W_STRONG,"re-auth"),
               (W_STRONG,"264 brands"),(W_STRONG,"shopping agent"),(W_STRONG,"agentic shopping workflow"),(W_STRONG,"intent capture"),
               (W_STRONG,"multi-step reasoning"),(W_STRONG,"error-recovery"),
               (W_MED,"single-cart"),(W_MED,"10 retailers"),
               (W_MED,"checkout"),(W_WEAK,"agentic")]},
  {"id": "mu-personalization", "title": "Built the personalization engine on real purchase history",
   "gist": "Content-based recommendations over style, price tier and brand affinity, fed by Gmail receipt parsing so every past purchase sharpens the feed. 100+ attributes.",
   "anchors": [(W_STRONG,"receipt pars"),(W_STRONG,"gmail api"),(W_STRONG,"100-dimension"),
               (W_STRONG,"100+ attribute"),(W_STRONG,"brand affinity"),
               (W_STRONG,"purchase history"),(W_STRONG,"content-based recommendation"),
               (W_STRONG,"preference learning"),(W_STRONG,"persona-driven"),
               (W_MED,"recommendation"),(W_MED,"personaliz"),(W_MED,"price tier")]},
  {"id": "mu-solo", "title": "Shipped it solo as a non-engineer",
   "gist": "120 API endpoints, 43 automated tests, 20+ live deploys, production-grade from day one, built with Claude Code. The proof-of-range story.",
   "anchors": [(W_STRONG,"120 api"),(W_STRONG,"43 automated"),(W_STRONG,"non-engineer"),
               (W_STRONG,"20+ live deploy"),(W_STRONG,"no engineering support"),(W_STRONG,"gen-ai development tool"),
               (W_MED,"claude code"),(W_MED,"solo"),(W_WEAK,"production-grade")]},
  {"id": "mu-launch", "title": "Launched app.muse.shopping live",
   "gist": "13,000+ catalogued products across 264 brands and 10 retailers, in production. The it-is-real-and-you-can-open-it story.",
   "anchors": [(W_STRONG,"app.muse.shopping"),(W_STRONG,"13,000+"),(W_STRONG,"13k+"),
               (W_MED,"launched"),(W_MED,"cataloged"),(W_MED,"catalogued"),(W_WEAK,"live")]},
 ],

 "aiprojects": [
  {"id": "ai-range", "title": "Range across consumer, enterprise and automation",
   "gist": "The umbrella bullet: what she has built, spanning consumer shopping, internal productivity and automation tooling.",
   "anchors": [(W_STRONG,"consumer, enterprise"),(W_STRONG,"highlight project"),
               (W_STRONG,"spanning consumer"),(W_MED,"interior-design"),(W_MED,"e-reader"),
               (W_STRONG,"other builds"),(W_STRONG,"reddit agent"),(W_STRONG,"non-engineers"),
               (W_STRONG,"case studies"),(W_STRONG,"personal ai tool"),(W_STRONG,"explainer"),
               (W_MED,"across consumer"),(W_WEAK,"enterprise productivity")]},
  {"id": "ai-kindle", "title": "Built the Kindle/Libby e-book agent",
   "gist": "Bridges two APIs to automate discovery, borrowing and file conversion. The API-integration story.",
   "anchors": [(W_STRONG,"kindle"),(W_STRONG,"libby"),(W_STRONG,"e-book agent"),
               (W_STRONG,"e-reader"),(W_STRONG,"reading agent"),(W_MED,"borrowing"),(W_MED,"file conversion"),(W_MED,"111 prs")]},
  {"id": "ai-stack", "title": "Ships end-to-end on a real production toolkit",
   "gist": "Claude Code, Codex, Vercel, Docker, Puppeteer and direct model APIs; LLMs wired to structured data. The how-she-works story.",
   "anchors": [(W_STRONG,"codex"),(W_STRONG,"puppeteer"),(W_STRONG,"docker"),
               (W_STRONG,"vercel"),(W_MED,"model api"),(W_MED,"full-stack"),
               (W_MED,"claude code"),(W_WEAK,"toolkit")]},
  {"id": "ai-volume", "title": "20+ tools, 500+ build hours, 12+ repos in six months",
   "gist": "The volume bullet -- evidence of rate, not just of one project.",
   "anchors": [(W_STRONG,"500+ build hour"),(W_STRONG,"12+ repos"),(W_STRONG,"20+ vibe"),
               (W_STRONG,"20+ ai tool"),(W_MED,"6 mos"),(W_MED,"six months")]},
 ],

 "misc": [
  {"id": "mi-interior", "title": "Built the interior-design platform",
   "gist": "Full-stack app with gallery, roadmap, kanban, contractor sharing and journal, plus an AI room advisor and a real permission model.",
   "anchors": [(W_STRONG,"interior design"),(W_STRONG,"interior-design"),(W_STRONG,"room advisor"),
               (W_STRONG,"kanban"),(W_STRONG,"contractor"),(W_STRONG,"permission model"),
               (W_STRONG,"role-based"),(W_STRONG,"phone auth"),(W_MED,"gallery"),
               (W_MED,"api layer"),(W_MED,"authentication")]},
  {"id": "mi-capture", "title": "Shipped the visual-inspiration capture tool",
   "gist": "Chrome extension plus iOS shortcut that pulls inspiration from anywhere into one tagged, searchable gallery.",
   "anchors": [(W_STRONG,"chrome extension"),(W_STRONG,"ios shortcut"),
               (W_MED,"visual inspiration"),(W_MED,"searchable")]},
  {"id": "mi-llmcourse", "title": "Designed the 'Intro to LLM' learning tool",
   "gist": "Interactive modules and a user-facing interface for a course on LLMs.",
   "anchors": [(W_STRONG,"intro to llm"),(W_STRONG,"learning tool"),(W_MED,"interactive module")]},
  {"id": "mi-feedback", "title": "Built the real-time product feedback feed",
   "gist": "Curated and published 1,096 labeled pieces of feedback after an AI lab shipped a new product suite.",
   "anchors": [(W_STRONG,"feedback feed"),(W_STRONG,"1,096"),(W_MED,"labeled"),
               (W_MED,"ai lab")]},
  {"id": "mi-events", "title": "Ran 175+ cultural events for 2,400+ young professionals",
   "gist": "Community building at real scale in San Francisco.",
   "anchors": [(W_STRONG,"175+"),(W_STRONG,"2,400+"),(W_STRONG,"young professional"),
               (W_STRONG,"1,000+ person"),(W_MED,"cultural event"),(W_MED,"membership")]},
  {"id": "mi-honors", "title": "Selective fellowships and leadership programs",
   "gist": "Schusterman ROI, Conscious Leadership Group and similar -- signal, not achievement.",
   "anchors": [(W_STRONG,"schusterman"),(W_STRONG,"conscious leadership"),(W_STRONG,"roi"),
               (W_MED,"fellow"),(W_MED,"selected for")]},
 ],

 "community": [
  {"id": "co-founded", "title": "Co-founded a student safety org across 20+ campuses",
   "gist": "0-to-1 nonprofit: the organizing playbook every chapter launched from, 20+ universities, $30K raised in two weeks for the national summit.",
   "anchors": [(W_STRONG,"20+ campus"),(W_STRONG,"20+ universit"),(W_STRONG,"$30k"),
               (W_STRONG,"co-founded"),(W_MED,"playbook"),(W_MED,"chapter"),
               (W_MED,"student safety"),(W_MED,"advocacy"),(W_WEAK,"nonprofit")]},
  {"id": "co-congress", "title": "Testified before Congress",
   "gist": "Invited to testify on campus safety policy. Rare, verifiable, and it needs no adjective.",
   "anchors": [(W_STRONG,"congress"),(W_STRONG,"testif")]},
  {"id": "co-press", "title": "National press on the work",
   "gist": "CNN, Fox, Forbes. Third-party validation of the same organizing story.",
   "anchors": [(W_STRONG,"cnn"),(W_STRONG,"forbes"),(W_STRONG,"fox"),(W_MED,"interviewed on")]},
  {"id": "co-heritage", "title": "Grew a cultural heritage community to ~1,000 members",
   "gist": "Four months to ~1,000 members, with a written governance model.",
   "anchors": [(W_STRONG,"cultural heritage"),(W_STRONG,"1,000 member"),
               (W_MED,"governance model"),(W_MED,"four months")]},
 ],

 "edu_berkeley": [
  {"id": "eb-coursework", "title": "Coursework",
   "gist": "Education metadata, not an achievement. One line, and only when the JD gives a reason for it.",
   "anchors": [(W_NAME,"coursework")]},
  {"id": "eb-ldor", "title": "L'dor: built a marketplace as an independent study",
   "gist": "Cultural homegoods marketplace with 100+ user discovery interviews and 500+ wholesalers evaluated; used GenAI for rapid prototyping.",
   "anchors": [(W_STRONG,"l'dor"),(W_STRONG,"ldor"),(W_STRONG,"homegoods"),
               (W_STRONG,"wholesale"),(W_STRONG,"independent study"),(W_MED,"d2c"),
               (W_MED,"jewish lifestyle"),(W_MED,"100+ user")]},
  {"id": "eb-honors", "title": "Scholarships and fellowships",
   "gist": "FWSF Scholarship, Mosaic Taiwan Fellowship. Signal line.",
   "anchors": [(W_STRONG,"fwsf"),(W_STRONG,"scholarship"),(W_STRONG,"mosaic"),
               (W_MED,"fellowship"),(W_MED,"recipient")]},
 ],

 "edu_illinois": [
  {"id": "ei-nutrition", "title": "Built a nutrition product for T2 diabetes in rural India",
   "gist": "Led designers and engineers, set prototype requirements and ran the user-testing strategy. The earliest real product story.",
   "anchors": [(W_STRONG,"diabetes"),(W_STRONG,"rural india"),(W_STRONG,"nutrition"),
               (W_MED,"user testing"),(W_MED,"prototype requirement")]},
  {"id": "ei-orgs", "title": "Co-founded four social-impact organizations",
   "gist": "Campus to global scale, recognized by the Clinton Global Initiative; Lean In chapter to 45 students.",
   "anchors": [(W_STRONG,"clinton global"),(W_STRONG,"lean in"),(W_STRONG,"hillel"),
               (W_STRONG,"4 social impact"),(W_STRONG,"four social"),(W_MED,"co-founded")]},
  {"id": "ei-honors", "title": "Selective programs",
   "gist": "1 of 25 selected for the Silicon Valley Entrepreneurship Workshop.",
   "anchors": [(W_STRONG,"silicon valley entrepreneurship"),(W_STRONG,"1 of 25"),
               (W_MED,"selected")]},
 ],

 "coherent": [
  {"id": "ch-prototype", "title": "Prototyped automatic portfolio aggregation",
   "gist": "Pulled customers' investments automatically and broke down their portfolios; Plaid integration across institutions. Appears on no recent CV.",
   "anchors": [(W_STRONG,"plaid"),(W_STRONG,"portfolio"),(W_STRONG,"prototype"),
               (W_MED,"investments"),(W_MED,"holdings")]},
  {"id": "ch-pmf", "title": "Ran user research toward product-market fit",
   "gist": "Grew the community to 100+ while testing what people would actually pay for; priced it freemium-to-subscription off a dozen interviews.",
   "anchors": [(W_STRONG,"product-market fit"),(W_STRONG,"freemium"),(W_STRONG,"100+"),
               (W_MED,"user research"),(W_MED,"pricing"),(W_MED,"interview")]},
 ],
}

MIN_SCORE = 5


def assign(text: str, experience_id: str):
    """Return (story_id, score). Falls back to '<experience>-other' below MIN_SCORE."""
    low = text.lower()
    best, best_score = None, 0
    for st in STORIES.get(experience_id, []):
        score = sum(w for w, term in st["anchors"] if term in low)
        score -= sum(w for w, term in st.get("veto", []) if term in low)
        if score > best_score:
            best, best_score = st["id"], score
    if best is None or best_score < MIN_SCORE:
        return f"{experience_id}-other", best_score
    return best, best_score


def catalog():
    """Flat {storyId: {...}} including the per-experience 'other' buckets."""
    out = {}
    for exp, sts in STORIES.items():
        for st in sts:
            out[st["id"]] = {**st, "experienceId": exp}
        out[f"{exp}-other"] = {
            "id": f"{exp}-other", "experienceId": exp, "title": "Everything else",
            "gist": "Variants that do not match a named story yet. If this bucket is large, "
                    "the story table needs a new entry -- not a lower threshold.",
            "anchors": [],
        }
    return out


# --------------------------------------------------------------------------
# Editorial layer. `proof` is the metric set this story is entitled to claim;
# `drift` records where her own CVs disagree with each other about that story --
# real findings from reading the archive, not lint. Merged 2026-09-15 from the
# parallel build that was live on the artifact, remapped onto the ids above and
# split where that build had merged two different claims into one story.
# Anything not listed falls back to metrics derived from the bullets themselves.
# --------------------------------------------------------------------------
EDITORIAL = {
 "wm-charter": {
   "proof": ["~400M daily page views", "~30% of marketplace", "$400M+ charter"],
   "drift": "The charter is $400M+ in some versions, a ~$400M GMV mandate in others, and "
            "~$400M validated impact in others. Lead with the charter, not GMV."},
 "wm-experiments": {
   "proof": ["greater than $137M GMV banked", "~$107M Popularity Signal", "+0.66% ATC"],
   "drift": "Data Refresh is $30M in some versions and $33M in others. Also seen: +7% YoY ATC, "
            "+0.87% with $58M, and +1.51% 3P conversion. Settle one set."},
 "wm-secondary": {
   "proof": ["~45M daily impressions", "+0.46% multi-offer add-to-cart", "4 teams"],
   "drift": "Some versions drop the tilde (45M vs ~45M) or call it a search surface."},
 "wm-agent": {
   "proof": ["200+ person org", "10+ upstream systems", "3x"],
   "drift": "The tool is called BuyBox Engineer, Team Engineer and AI Engineer in different "
            "versions. Users are a 200+ org in some and a 15-person team in others; systems are "
            "10+ in some and 15+ in others. Pick one. The 15-person version also trips the "
            "aislop honesty rule by claiming daily usage."},
 "wm-opsystem": {
   "proof": ["30+ initiatives/qtr", "20 stakeholders", "2x"],
   "drift": "Scope varies a lot: 30 vs 50+ teams, 30 vs 100 initiatives, 20 vs 5+ orgs, 2x vs "
            "80%. The 50/100 versions are the outliers."},
 "wm-deps": {
   "proof": ["10+ upstream systems", "~80% less investigation time"],
   "drift": "Some versions tell this as SQL analysis and others as architecting API and signal "
            "contracts. Those are different claims about what she did -- pick the one the JD "
            "is asking for and do not blend them."},
 "wm-trust":        {"proof": ["+0.28% relevance"]},
 "wm-availability": {"proof": ["~8% fewer out-of-stock recommendations"]},
 "wm-runops":       {"proof": ["Search to PDP", "on-call with engineering"]},

 "up-chiefofstaff": {"proof": ["2x capital deployed over 3 yrs", "5 functions"]},
 "up-kpi":          {"proof": ["30 startups", "90% adoption", "50% less collection time"]},
 "up-prorata":      {"proof": ["~95% adoption", "$100M+ in 2 months", "5 customer segments"]},
 "up-fundraises": {
   "proof": ["7 fundraises", "$400M+ raised"],
   "drift": "Several versions are truncated to \"$400\" with no M, and one says $475M+. Some say "
            "$200M closed, others $100M+ from 50+ investors."},
 "up-execops": {
   "proof": ["80% shorter reporting cycle", "50-page quarterly report"],
   "drift": "The 30%, 75% and 80% figures all describe similar workflow wins. Pick one."},
 "up-dashboard":    {"proof": ["3x organizational capacity", "CFO and 3 managing partners"]},
 "up-governance":   {"proof": ["2x engagement"]},
 "up-investorops":  {"proof": ["500+ investors", "$200M closed"]},
 "up-founders":     {"proof": ["30 portfolio companies"]},
 "up-research":     {"proof": ["80% efficiency"]},

 "si-gtm":      {"proof": ["15+ interviews", "5x adoption plan"]},
 "si-roadmap":  {"proof": ["~6x lifetime customer value", "15+ stakeholder interviews"]},
 "si-research": {"proof": ["value-chain analysis", "industry expert interviews"]},
 "si-xfn":      {"proof": ["10-person cross-functional team"],
                 "drift": "Almost every wording of this one opens with \"Partnered with\", which is "
                          "on the aislop corporate-filler kill list. 2 of 31 are clean."},
 "si-pricing":  {"proof": ["SaaS costing and pricing models"]},

 "ac-assets":     {"proof": ["50+ stakeholders", "5+ teams"]},
 "ac-cmo":        {"proof": ["6 weeks to 2 days"]},
 "ac-staffing":   {"proof": ["15 user interviews", "100-person org"]},
 "ac-allocation": {"proof": ["2x productivity"]},
 "ac-labeling":   {"proof": ["human-in-the-loop image labeling"]},

 "mu-solo":            {"proof": ["120 API endpoints", "43 tests", "20+ deploys"]},
 "mu-platform":        {"proof": ["264 brands", "10 retailers", "Stripe single-cart"]},
 "mu-launch":          {"proof": ["13K+ products", "live at app.muse.shopping"]},
 "mu-personalization": {"proof": ["100+ attributes", "Gmail receipt parsing"]},

 "ai-volume": {"proof": ["20+ tools", "500+ build hours", "12+ repos"]},
 "ai-range":  {"proof": ["consumer, enterprise and automation"]},
 "ai-kindle": {"proof": ["Kindle and Libby APIs bridged"]},
 "ai-stack":  {"proof": ["Claude Code, Codex, Vercel, Docker"]},

 "ch-prototype": {"proof": ["Plaid across institutions"]},
 "ch-pmf":       {"proof": ["100+ community"]},
 "co-founded":   {"proof": ["20+ campuses", "$30K in 2 weeks"]},
 "co-congress":  {"proof": ["testified before Congress"]},
 "eb-ldor":      {"proof": ["100+ discovery users", "500+ wholesalers evaluated"]},
 "ei-nutrition": {"proof": ["50+ user interviews"]},
 "mi-interior":  {"proof": ["role-based permissions", "50+ API routes"]},
 "mi-events":    {"proof": ["175+ events", "2,400+ professionals"]},
 "mi-feedback":  {"proof": ["1,096 labeled items"]},
}

# The cross-resume baseline: the things EVERY version of her resume should say, whatever the
# JD. Distinct from the per-role story lists -- those answer "which 5-10 stories for this job",
# this answers "what must never be missing". Ported from the parallel build, remapped.
BASELINE = [
 ("wm-charter",      "Owned the ML ranking system that picks the Buy Box winner on Walmart.com: "
                     "~400M daily views, $400M+ charter"),
 ("wm-experiments",  "Ran the ranking experiments that banked >$137M in GMV"),
 ("wm-secondary",    "Launched the Secondary Buy Box 0→1 for shoppers: ~45M daily impressions, "
                     "+0.46% add-to-cart"),
 ("wm-agent",        "Built BuyBox Engineer, a GenAI agent nobody asked for, adopted across a "
                     "200+ person org"),
 ("wm-opsystem",     "Ran the operating system for 30+ cross-functional initiatives a quarter"),
 ("up-chiefofstaff", "First Chief of Staff at Uprising: built the firm's operating system and "
                     "investor tools ($100M+ in 2 months, 7 fundraises)"),
 ("si-gtm",          "Defined 0→1 GTM and a 6x LTV case for Siemens' new EV-charging SaaS"),
 ("mu-solo",         "Ships AI products solo: Muse (13K+ products, 264 brands) and 20+ tools "
                     "built with Claude Code"),
]
