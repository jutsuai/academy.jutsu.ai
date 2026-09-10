"""
Seed the Jutsu Ambassador Program (White Belt) as a full LMS course.

This is disposable demo content built from Jutsu_Master_Content_Document.pdf,
meant for looking at a populated LMS locally rather than for production. Run it,
look around, then run teardown() to remove every row it created:

    bench --site localhost execute lms.demo.jutsu_seed.seed
    bench --site localhost execute lms.demo.jutsu_seed.teardown

seed() is idempotent: it reuses anything already carrying the same title, so a
second run edits rather than duplicates.

Media is hot-linked, not uploaded. Images come from Wikimedia Commons (mostly
CC BY-SA, one public domain) and videos are YouTube embeds from third-party
channels. Every URL was checked live when this file was written. That is fine
for a local demo; a real course needs its own assets and its own attribution.
"""

import json

import frappe

COURSE_TITLE = "Jutsu Ambassador Program — White Belt"
CATEGORY = "Cybersecurity"
INSTRUCTOR_EMAIL = "sensei@jutsu.example.com"

# Graduates, so the certificate and the Certified Participants directory have
# something in them. example.com is reserved by RFC 2606 and cannot receive
# mail, so nothing here can reach a real person even with SendGrid configured.
CERTIFICATE_TEMPLATE = "Certificate"
LEARNERS = [
	{
		"email": "rin.tanaka@example.com",
		"first_name": "Rin",
		"last_name": "Tanaka",
		"issued_days_ago": 2,
	},
	{
		"email": "marcus.hale@example.com",
		"first_name": "Marcus",
		"last_name": "Hale",
		"issued_days_ago": 9,
	},
	{
		"email": "amara.okafor@example.com",
		"first_name": "Amara",
		"last_name": "Okafor",
		"issued_days_ago": 21,
	},
]

# ---------------------------------------------------------------------------
# Media. Kept in one place so a dead link is a one-line fix.
# ---------------------------------------------------------------------------

WIKI = "https://upload.wikimedia.org/wikipedia/commons"

IMG = {
	# Apollo 9 mission control: the closest public-domain thing to a SOC floor.
	"soc": f"{WIKI}/thumb/8/87/Mission_Operations_Control_Room_during_Apollo_9.jpg/1920px-Mission_Operations_Control_Room_during_Apollo_9.jpg",
	"monitors": f"{WIKI}/thumb/1/12/Diagnostic_monitors_in_the_control_room_of_Wendelstein_7-X.jpg/1920px-Diagnostic_monitors_in_the_control_room_of_Wendelstein_7-X.jpg",
	"ai": f"{WIKI}/thumb/e/ee/Artificial_Neural_Network_with_Chip.jpg/1920px-Artificial_Neural_Network_with_Chip.jpg",
	"terminal": f"{WIKI}/thumb/4/4e/Arch_Linux_system_update_via_pacman_on_an_Acer_laptop.jpg/1920px-Arch_Linux_system_update_via_pacman_on_an_Acer_laptop.jpg",
	"rack": f"{WIKI}/7/70/Computer_rack_with_switches_and_cables.jpg",
	"fiber": f"{WIKI}/d/d2/Optical_fiber_cable-06ASD.jpg",
	"switch": f"{WIKI}/thumb/e/e9/Switch-and-nest.jpg/1920px-Switch-and-nest.jpg",
	"desk": f"{WIKI}/thumb/d/d7/Micha%C5%82_Fr%C4%85ckowiak_-_Office_computers.jpg/1920px-Micha%C5%82_Fr%C4%85ckowiak_-_Office_computers.jpg",
	"control2": f"{WIKI}/thumb/5/58/Mission_Control_Room_2.jpg/1920px-Mission_Control_Room_2.jpg",
	"cloud": f"{WIKI}/thumb/9/95/Google_data_center.jpg/1920px-Google_data_center.jpg",
	"records": f"{WIKI}/2/25/Thirty-six_File_U._S._Document_Cabinet%2C_with_sliding_shelf_in_center.jpg",
	"robot": f"{WIKI}/thumb/f/f2/A_telepresence_robot_made_from_scrap.jpg/1920px-A_telepresence_robot_made_from_scrap.jpg",
	"datacenter": f"{WIKI}/thumb/5/5d/BalticServers_data_center.jpg/1920px-BalticServers_data_center.jpg",
}

VID = {
	"soc": "OHkWXFheSKM",  # IBM Technology — Security Operations Center (SOC) Explained
	"agents": "FwOTs4UxQS4",  # Jeff Su — AI Agents, Clearly Explained
	"lab": "S3CZyu6WD7I",  # LS111 — Cyber Security Virtual Lab Building Series Ep1
	"intel": "vDygXGJzWCY",  # Adam Goss — Cyber Threat Intelligence Explained
	"detection": "nSOqU1iX5oQ",  # John Hammond — Detection Engineering with Wazuh
	"spray": "uF4K_-CKckk",  # Cybersaur — Brute Force vs Password Spray Attacks
	"triage": "k9c1PBynVpA",  # MyDFIR — SOC Alert Triage Explained
	"ir": "DR4iGzBN6wg",  # CYBRIXEN — Incident Response Process Explained
	"cloud": "WopTpel6DUY",  # BeSA — AWS Shared Responsibility Model
	"compliance": "mpxaZIUSOmc",  # Secureframe — SOC 2 Compliance
	"hitl": "9iS-YYLIXiw",  # IBM Technology — What is Human In The Loop with AI?
}

# ---------------------------------------------------------------------------
# EditorJS block helpers. Lesson.vue renders `content` through a read-only
# EditorJS, so the block shapes here have to match the tools registered in
# frontend/src/utils/index.js getEditorTools().
# ---------------------------------------------------------------------------

_seq = {"n": 0}


def _bid():
	_seq["n"] += 1
	return f"jutsu{_seq['n']:04d}"


def h(text, level=2):
	return {"id": _bid(), "type": "header", "data": {"text": text, "level": level}}


def p(text):
	return {"id": _bid(), "type": "paragraph", "data": {"text": text}}


def ul(items):
	return {
		"id": _bid(),
		"type": "list",
		"data": {"style": "unordered", "items": [{"content": i, "items": []} for i in items]},
	}


def ol(items):
	return {
		"id": _bid(),
		"type": "list",
		"data": {"style": "ordered", "items": [{"content": i, "items": []} for i in items]},
	}


def img(key, caption=""):
	return {
		"id": _bid(),
		"type": "image",
		"data": {
			"url": IMG[key],
			"caption": caption,
			"withBorder": False,
			"withBackground": False,
			"stretched": False,
		},
	}


def yt(key, caption=""):
	video_id = VID[key]
	return {
		"id": _bid(),
		"type": "embed",
		"data": {
			"service": "youtube",
			"source": f"https://www.youtube.com/watch?v={video_id}",
			"embed": video_id,
			"caption": caption,
		},
	}


def quiz_block(quiz_name):
	return {"id": _bid(), "type": "quiz", "data": {"quiz": quiz_name}}


def objectives(items):
	return [h("Learning objectives", 3), ul(items)]


def takeaways(items):
	return [h("Key takeaways", 3), ul(items)]


def content(blocks):
	return json.dumps({"time": 1770000000000, "blocks": blocks, "version": "2.29.0"})


# ---------------------------------------------------------------------------
# Knowledge checks. One LMS Quiz per concept block.
# Each question: (text, [(option, is_correct), ...])
# ---------------------------------------------------------------------------

QUIZZES = {
	"w1-soc": (
		"Knowledge Check: Cybersecurity and the SOC",
		[
			(
				"What is the main purpose of a SOC?",
				[
					("To design company logos", 0),
					("To monitor, investigate, and respond to security threats", 1),
					("To manage employee payroll", 0),
					("To write marketing content", 0),
				],
			),
			(
				"Which three pillars support a SOC?",
				[
					("Sales, branding, and finance", 0),
					("People, process, and technology", 1),
					("Hardware, software, and snacks", 0),
					("Marketing, support, and hiring", 0),
				],
			),
			(
				"True or false: cybersecurity is only about preventing attacks.",
				[("True", 0), ("False", 1)],
			),
		],
	),
	"w1-severity": (
		"Knowledge Check: Alert Severity",
		[
			(
				"What does alert severity help analysts decide?",
				[
					("Which alert to review first", 1),
					("Which employee to hire", 0),
					("Which software license to buy", 0),
					("Which company logo to use", 0),
				],
			),
			(
				"True or false: a critical alert is always a confirmed attack.",
				[("True", 0), ("False", 1)],
			),
			(
				"Which severity usually requires the fastest attention?",
				[("Low", 0), ("Medium", 0), ("Critical", 1), ("Informational", 0)],
			),
		],
	),
	"w1-agents": (
		"Knowledge Check: AI Agents and Agentic Security",
		[
			(
				"What is one difference between a chatbot and an AI agent?",
				[
					("A chatbot can only be used on phones", 0),
					("An AI agent can work through a task, not just answer a question", 1),
					("A chatbot is always more accurate", 0),
					("An AI agent cannot use tools", 0),
				],
			),
			(
				"True or false: AI agent output should always be treated as final truth.",
				[("True", 0), ("False", 1)],
			),
			(
				"Why do AI agents matter in a SOC?",
				[
					("They can help review, enrich, summarize, and reason through security data", 1),
					("They replace every security employee immediately", 0),
					("They remove the need for documentation", 0),
					("They make alerts unnecessary", 0),
				],
			),
		],
	),
	"w2-intel": (
		"Knowledge Check: Threat Intelligence and Enrichment",
		[
			(
				"What does enrichment do?",
				[
					("Deletes alerts", 0),
					("Adds context to security data", 1),
					("Turns off monitoring", 0),
					("Creates user accounts", 0),
				],
			),
			(
				"True or false: if an IP has no malicious reputation, it is always safe.",
				[("True", 0), ("False", 1)],
			),
			(
				"Which of the following is an example of enrichment?",
				[
					("Adding country and reputation data to an IP address", 1),
					("Turning off a firewall", 0),
					("Changing a password randomly", 0),
					("Deleting logs", 0),
				],
			),
			(
				"True or false: agentic enrichment should be treated as helpful context, not final proof.",
				[("True", 1), ("False", 0)],
			),
		],
	),
	"w2-detection": (
		"Knowledge Check: Detection Engineering",
		[
			(
				"What is an event?",
				[
					("A record of something that happened", 1),
					("A final incident report", 0),
					("A company policy", 0),
					("A certificate", 0),
				],
			),
			(
				"What is a detection rule?",
				[
					("A rule that deletes logs", 0),
					("Logic that identifies suspicious activity", 1),
					("A list of employee birthdays", 0),
					("A cloud invoice", 0),
				],
			),
			("True or false: every alert is a confirmed attack.", [("True", 0), ("False", 1)]),
			(
				"What does the AI agent help do after a detection rule creates an alert?",
				[
					("Add context and reasoning", 1),
					("Delete the evidence", 0),
					("Hide the alert from analysts", 0),
					("Replace all documentation", 0),
				],
			),
		],
	),
	"w3-verdicts": (
		"Knowledge Check: True Positive, False Positive, False Negative",
		[
			(
				"What is a true positive?",
				[
					("A real suspicious event correctly detected by an alert", 1),
					("A harmless event incorrectly detected by an alert", 0),
					("A missed attack", 0),
					("A deleted log", 0),
				],
			),
			(
				"What is a false positive?",
				[
					("A real attack that was missed", 0),
					("A harmless or expected activity that triggered an alert", 1),
					("A confirmed incident", 0),
					("A cloud storage bucket", 0),
				],
			),
			(
				"True or false: needs further investigation can be a valid temporary verdict.",
				[("True", 1), ("False", 0)],
			),
		],
	),
	"w4-ir": (
		"Knowledge Check: Incident Response",
		[
			(
				"What is containment?",
				[
					("Stopping the threat from spreading or causing more damage", 1),
					("Writing a LinkedIn post", 0),
					("Deleting the SOC dashboard", 0),
					("Ignoring the alert", 0),
				],
			),
			(
				"What is eradication?",
				[
					("Removing the root cause of the incident", 1),
					("Making a marketing video", 0),
					("Creating a new user account", 0),
					("Changing the company name", 0),
				],
			),
			(
				"True or false: lessons learned help improve future security.",
				[("True", 1), ("False", 0)],
			),
		],
	),
	"w4-cloud": (
		"Knowledge Check: Cloud Security",
		[
			(
				"In the shared responsibility model, who secures customer data access permissions?",
				[
					("Usually the customer", 1),
					("Always the internet provider", 0),
					("The office receptionist", 0),
					("No one", 0),
				],
			),
			(
				"What is a common cloud security issue?",
				[
					("Exposed storage bucket", 1),
					("Too many office chairs", 0),
					("Broken keyboard", 0),
					("Slow coffee machine", 0),
				],
			),
			(
				"True or false: cloud providers secure everything automatically, so customers do not need to configure security.",
				[("True", 0), ("False", 1)],
			),
		],
	),
	"w4-compliance": (
		"Knowledge Check: Compliance Basics",
		[
			(
				"What is one reason companies pursue SOC 2?",
				[
					("To prove they take customer data security seriously", 1),
					("To design a new logo", 0),
					("To replace all employees", 0),
					("To stop using computers", 0),
				],
			),
			(
				"Which of the following can be compliance evidence?",
				[
					("Triage notes", 0),
					("Incident reports", 0),
					("Logs", 0),
					("All of the above", 1),
				],
			),
			(
				"True or false: documentation is part of real security operations.",
				[("True", 1), ("False", 0)],
			),
			(
				"True or false: if an AI agent recommends a response action, that recommendation may also need to be documented.",
				[("True", 1), ("False", 0)],
			),
		],
	),
	"w4-oversight": (
		"Knowledge Check: Human Oversight of Autonomous Response",
		[
			(
				"What does autonomous response mean?",
				[
					("A system takes a response action without waiting for human approval", 1),
					("A user writes a LinkedIn post", 0),
					("A cloud provider sends an invoice", 0),
					("A SOC ignores all alerts", 0),
				],
			),
			(
				"Which response action may require human approval?",
				[
					("Disabling a production administrator account", 1),
					("Creating a low-risk note", 0),
					("Showing a dashboard tooltip", 0),
					("Displaying a help page", 0),
				],
			),
			(
				"True or false: human oversight can still be important when AI agents are useful.",
				[("True", 1), ("False", 0)],
			),
			(
				"What is the safest level of agent action?",
				[
					("Recommend only", 1),
					("Act automatically every time", 0),
					("Delete all logs", 0),
					("Disable all users", 0),
				],
			),
		],
	),
}


# ---------------------------------------------------------------------------
# Curriculum. Each lesson is (title, preview?, blocks-builder). The builder is a
# callable so quiz blocks can reference quiz docnames created earlier in seed().
# ---------------------------------------------------------------------------


def curriculum(q):
	"""q maps a quiz key to the LMS Quiz docname created for it."""
	return [
		(
			"Start Here",
			[
				(
					"Welcome to the Jutsu Ambassador Program",
					1,
					[
						h("Welcome to the Jutsu Ambassador Program"),
						img("soc", "Four weeks of hands-on security operations work."),
						p(
							"Over the next four weeks, you are going to build your own security lab from scratch, launch controlled attack simulations against it, and then sit down and investigate what happened, the same way a real Security Operations Center would, except this time you will be doing it alongside a team of AI agents instead of a room full of human analysts."
						),
						p(
							"You will set up a machine and connect it to AgentSOC, an agentic AI-powered SOC and SIEM platform built to detect threats, investigate alerts, and take automated response actions using a coordinated chain of specialized AI agents. You will generate real security activity inside your own approved lab environment and watch the alerts arrive in real time."
						),
						p(
							"Agentic security only works when the human in the loop knows how to evaluate what the agent is telling them, and that evaluation skill is the throughline of this entire program."
						),
						h("By the end of four weeks", 3),
						ul(
							[
								"You will triage a real alert from start to finish",
								"You will write a genuine incident response report",
								"You will share what you learned publicly on LinkedIn",
								"You will understand SOC, triage, incident response and AI agents because you practiced the workflow those words describe",
							]
						),
						yt("soc", "Security Operations Center (SOC) Explained — IBM Technology"),
					],
				),
				(
					"What Is AgentSOC?",
					1,
					[
						h("What Is AgentSOC?"),
						img("datacenter", "AgentSOC watches your lab the way a SOC watches an estate."),
						p(
							"AgentSOC is an agentic AI-powered SOC and SIEM platform. In plain terms, that means it detects threats, investigates alerts using a coordinated chain of specialized AI agents, and can take automated response actions, the same fundamental job a human-staffed Security Operations Center performs."
						),
						h("Agentic is doing real work in that sentence", 3),
						p(
							"An agentic system is not a single chatbot bolted onto a dashboard. It is a coordinated set of AI agents, each one responsible for a specific part of the security workflow, working together to move an alert from raw data all the way to a documented, defensible conclusion."
						),
						ul(
							[
								"One agent normalizes incoming data so it can be understood consistently",
								"Another enriches that data with threat intelligence and geolocation context",
								"Another reasons through the evidence and proposes an assessment",
								"Another recommends, or in some cases takes, a response action",
							]
						),
						p(
							"Every alert, every lab, and every triage decision you make in this program happens inside AgentSOC. It pulls in data from Wazuh SIEM and Google Workspace email logs, enriches that activity using nine separate threat intelligence providers, and can take real containment actions through SOAR playbooks: blocking IP addresses, blocking senders, disabling compromised users, and isolating EC2 instances."
						),
					],
				),
				(
					"The Journey, Week by Week",
					1,
					[
						h("The Journey, Week by Week"),
						img("monitors", "Each week adds a layer to the same workflow."),
						ol(
							[
								"<b>Week 1: Foundations.</b> What cybersecurity means, how a SOC decides what deserves attention, how alert severity works, and what an AI agent is at a foundational level, before building and connecting your own home lab.",
								"<b>Week 2: Threat Intel and Detection.</b> Watch raw activity become an alert in real time, run your first controlled attack simulation, and see AgentSOC's agents add layers of context that a raw log entry could never provide.",
								"<b>Week 3: Triage.</b> Triage a real alert yourself, deciding whether it is a true positive, a false positive, or something that still needs more digging, then compare your verdict against AgentSOC's assessment.",
								"<b>Week 4: The Broader Security Landscape.</b> Connect triage to incident response, explore how cloud security and compliance fit in, and confront one of the defining questions of agentic security: when should an AI agent be allowed to act entirely on its own?",
							]
						),
						h("Every week, the same rhythm", 3),
						ul(
							[
								"<b>Concepts</b> — short reading blocks that explain one topic at a time",
								"<b>Video</b> — a short explainer whenever a concept benefits from being shown rather than described",
								"<b>Lab</b> — a hands-on activity performed directly inside AgentSOC, using your own approved lab environment",
								"<b>Submission</b> — proof of the work you completed, a short written reflection, and a sample LinkedIn post",
								"<b>Belt Progress</b> — each completed weekly submission unlocks one stripe toward the Jutsu White Belt Certificate",
							]
						),
					],
				),
				(
					"The Jutsu Belt System",
					1,
					[
						h("The Jutsu Belt System"),
						p(
							"The Jutsu Ambassador Program borrows its progression system from real jiu-jitsu, and we take that metaphor seriously enough not to cheapen it. The real belt order is White, Blue, Purple, Brown, and Black, and each of those ranks is earned over years of consistent practice, never over a single weekend. Because this is a four-week beginner bootcamp, it would be dishonest to hand out anything beyond the earliest rank, so the entire program represents exactly one stage: White Belt, in training."
						),
						h("Your four stripes", 3),
						ul(
							[
								"Week 1 Stripe: Foundations complete",
								"Week 2 Stripe: Threat intelligence and detection complete",
								"Week 3 Stripe: Triage complete",
								"Week 4 Stripe: Program complete",
							]
						),
						p(
							"Once you have earned all four stripes, you unlock the Jutsu White Belt Certificate. It is important to be honest about what this certificate is and is not. It is not a professional certification, and it does not replace industry credentials like CompTIA Security+, ISC2 Certified in Cybersecurity, or ISO 27001. Think of it instead as solid proof that you did real, hands-on work in an agentic security environment."
						),
						h("After the bootcamp: the ongoing ambassador track", 3),
						ul(
							[
								"<b>Blue Belt — Contributor.</b> Active for at least three months, has created original Jutsu-related content, participates regularly in community discussions.",
								"<b>Purple Belt — Advocate.</b> Active for at least six months, multiple pieces of original content, helps answer questions from newer ambassadors.",
								"<b>Brown Belt — Senior Advocate.</b> Active for nine or more months, consistently high-quality content, actively mentors newer ambassadors.",
								"<b>Black Belt — Master Ambassador.</b> Active for twelve or more months, hosts sessions and workshops, represents the Jutsu community publicly.",
							]
						),
						p(
							"Unlike the bootcamp stripes, these tiers are not earned by completing another short course. They are earned over time, by staying active, creating original content, helping other participants, and genuinely contributing to the Jutsu community."
						),
					],
				),
				(
					"Before You Start: Read This",
					1,
					[
						h("Before You Start: Read This"),
						h("This is training, not policy", 3),
						p(
							"Jutsu is a controlled learning environment, and nothing in this program is meant to replace your employer's actual security policies, procedures, or legal requirements. If you already work in a real security role, always continue following your organization's approved processes rather than anything described here."
						),
						h("Authorized lab use only", 3),
						p(
							"Every hands-on activity in this program must happen inside your own approved lab environment. Never run scans, password attacks, brute force attempts, or any other security testing tool against employer systems, school systems, public websites, cloud systems that were not created specifically for this program, shared networks, or any device belonging to a friend, family member, or third party. This program exists to teach defensive skills, and every exercise is scoped accordingly."
						),
						h("No real company or customer data", 3),
						p(
							"Every lab in this program should use only personal lab machines, approved test accounts, demo data, training alerts, and controlled simulations. Never use real company data, real customer data, real employee data, production logs, private credentials, or internal systems belonging to a real organization."
						),
						h("AI agent output can be wrong", 3),
						p(
							"AgentSOC's AI agents are genuinely useful, but they are not infallible. An agent can miss important evidence, overstate or understate real risk, misread the surrounding context, reach an incorrect conclusion, or recommend an action that truly needs human review before it happens. Treat every agent output as a strong starting point for your own investigation, never as the final word."
						),
						h("LinkedIn posts are public", 3),
						p(
							"Only share information you would be comfortable having visible to your professional network, your current employer, future employers, classmates, and the broader internet. Never include private screenshots, real customer data, internal company names, real employer systems, real IP addresses from outside your lab, or credentials of any kind."
						),
						h("Certificate scope", 3),
						p(
							"The Jutsu White Belt Certificate reflects successful completion of a four-week introductory training program. You are welcome to list it on LinkedIn or your resume, but describe it honestly, as an introductory, hands-on ambassador program rather than a formal industry credential."
						),
					],
				),
			],
		),
		(
			"Week 1: Foundations",
			[
				(
					"Cybersecurity Is Not a Force Field, It Is a Habit",
					0,
					[
						h("Cybersecurity Is Not a Force Field, It Is a Habit"),
						img("soc", "A SOC exists to notice things, not only to block them."),
						*objectives(
							[
								"Explain what cybersecurity means, in plain language rather than buzzwords",
								"Describe what a Security Operations Center does over the course of a normal day",
								"Name the three pillars a SOC stands on: people, process, and technology",
								"Point to exactly where AgentSOC and its AI agents fit into that larger picture",
							]
						),
						p(
							"Here is something nobody tells beginners often enough: hackers do not pick you personally. They do not know your name, they do not care about your feelings, and they most certainly did not read your resume before deciding to target you. Attackers scan enormous swaths of the internet looking for weak spots, the same way water finds a crack in a sidewalk, and your system ends up on their list simply because it happened to have that crack."
						),
						p(
							"A useful way to picture this is to compare it with physical security. Instead of doors, we are protecting accounts and servers. Instead of security cameras, we are collecting detailed logs of activity. Instead of a guard walking the halls, a security analyst is watching a continuous stream of alerts and deciding, moment to moment, what genuinely deserves attention."
						),
						h("Prevention is not the whole job", 3),
						p(
							"New people entering security tend to assume the entire mission is stopping the attacker before they ever get in. Prevention absolutely matters, but treating it as the whole job is exactly how teams end up blindsided. The real question a mature security team asks itself was never <i>can we stop every single attack</i>. It is a more honest and more useful question: when something suspicious does happen, how quickly can we notice it, understand it, and respond to it before it causes real damage?"
						),
						h("The workflow, start to finish", 3),
						p(
							"Almost everything a SOC does follows the same underlying chain: <b>event, detection, alert, investigation, triage, response, and documentation</b>."
						),
						ol(
							[
								"<b>Event</b> — a record of something that happened, such as a single failed login attempt",
								"<b>Detection</b> — the logic that decides whether that event, or a pattern of events, is worth a second look",
								"<b>Alert</b> — the actual item an analyst reviews, produced once that logic fires",
								"<b>Investigation</b> — digging through the surrounding evidence",
								"<b>Triage</b> — the analyst's call: real threat, false alarm, or needs more information",
								"<b>Response</b> — whatever action follows, such as blocking an IP or disabling an account",
								"<b>Documentation</b> — writing it all down clearly so the incident does not evaporate from institutional memory",
							]
						),
						h("The three things holding a SOC up", 3),
						img("desk", "People, process, and technology — remove one and it wobbles."),
						p(
							"<b>People</b> are the analysts, engineers, and responders making the calls that matter. <b>Process</b> is the shared playbook that governs how alerts get assigned, how severity gets decided, and how escalation works. Without a clear process, five different analysts can end up handling the same kind of alert five completely different ways. <b>Technology</b> is everything that helps a team collect, detect, enrich, and respond at scale. Technology makes a team faster and more capable, but it does not make the underlying decisions on the team's behalf."
						),
						*takeaways(
							[
								"Cybersecurity protects digital systems and data, and it functions as an ongoing discipline rather than a one-time shield",
								"A SOC continuously monitors, investigates, and responds to threats; it does not simply try to prevent every attack",
								"SOC work follows a consistent chain: detection, investigation, triage, response, and documentation",
								"Every SOC ultimately depends on three pillars working together: people, process, and technology",
								"AgentSOC is your hands-on platform for the rest of this program, built around a coordinated chain of AI agents",
							]
						),
						quiz_block(q["w1-soc"]),
					],
				),
				(
					"Alert Severity: Loud Does Not Always Mean Dangerous",
					0,
					[
						h("Alert Severity: Loud Does Not Always Mean Dangerous"),
						img("monitors", "Severity answers 'how fast?', not 'is it real?'"),
						*objectives(
							[
								"Explain precisely what alert severity does and does not tell you",
								"Distinguish clearly between low, medium, high, and critical severity",
								"Recognize that severity functions as a priority signal, not a final verdict",
							]
						),
						p(
							"A genuinely busy SOC receives far more alerts than any single analyst could investigate in equal depth, so severity exists to help answer one narrow, practical question: <b>how quickly should someone look at this?</b> It deliberately does not answer a much larger question, which is whether this is truly an attack. Confusing severity with a confirmed verdict is the single most common mistake beginners make in this field."
						),
						h("Low severity", 3),
						p(
							"Activity that is genuinely unusual, but not urgent. A user logging in from an unfamiliar browser, a minor configuration drift, or a single isolated failed login. Low severity does not mean the alert is useless or safe to ignore entirely."
						),
						h("Medium severity", 3),
						p(
							"Deserves a closer look. Multiple failed login attempts, a login from an unfamiliar geographic location, or a brand-new device joining the network. Five failed logins by themselves might mean very little, but five failed logins immediately followed by a successful login from a country the organization has never operated in tells an entirely different story."
						),
						h("High severity", 3),
						p(
							"Points toward a genuine, credible possibility of malicious activity. Malware detected on a machine, sustained brute force login attempts, suspicious privilege escalation, or access to sensitive systems from somewhere it should never originate."
						),
						h("Critical severity", 3),
						p(
							"An immediate, credible risk to the organization itself. Ransomware behavior, active data exfiltration, a compromised administrator account, or ongoing command-and-control communication. Here is the twist worth remembering: even a critical alert can still turn out to be a false alarm once investigated. <b>Severity tells you how loudly the smoke detector is going off. It does not tell you whether there is a fire.</b>"
						),
						*takeaways(
							[
								"Severity helps prioritize which alerts get reviewed first, rather than confirming what happened",
								"Low, medium, high, and critical describe urgency and potential risk, not a confirmed fact",
								"A critical alert can still turn out to be a false positive once it is fully investigated",
								"Investigation and triage, not severity alone, ultimately decide what an alert truly means",
							]
						),
						quiz_block(q["w1-severity"]),
					],
				),
				(
					"What Is an AI Agent, and Why Does Agentic Security Matter Now?",
					0,
					[
						h("What Is an AI Agent, and Why Does Agentic Security Matter Now?"),
						img("ai", "An agent works through a task; a chatbot answers a question."),
						*objectives(
							[
								"Explain what an AI agent is, in clear, plain language",
								"Distinguish clearly between a chatbot, simple automation, and a true AI agent",
								"Explain why agentic AI specifically matters for modern security operations",
								"Recognize that AI agent reasoning needs to be actively checked, never trusted automatically",
							]
						),
						h("Agent, not just chatbot", 3),
						p(
							"A chatbot waits patiently for a question and then answers it, nothing more. An AI agent does considerably more: it can independently examine available information, decide what matters, call external tools when it needs additional data, follow a multi-step workflow from start to finish, produce a concrete recommendation, take an approved action when authorized, and explain its own reasoning along the way. <b>A chatbot responds. An agent works through an entire task.</b>"
						),
						p(
							"Ask a chatbot to define a brute force attack, and you will get a tidy definition back. An agent, facing that same situation live inside a real environment, might instead notice the repeated failed logins on its own initiative, pull the related logs without being asked, check IP enrichment data, review exactly who the targeted user is, compare the pattern against known attack behavior, decide whether the activity looks genuinely suspicious, recommend a concrete next step, and write a clear summary for the analyst reviewing it."
						),
						h("Automation versus agent", 3),
						p(
							"Plain automation follows a fixed rule with essentially zero flexibility: <i>if there are more than ten failed logins in five minutes, fire an alert</i>. That kind of rule is useful, but rigid by design. Ten failed logins originating from a known office VPN, against a designated test account, during a scheduled lab exercise, likely represents lower real risk. Ten failed logins followed immediately by a successful login from a brand-new country, against a privileged administrator account, should escalate quickly. <b>Automation follows a rule. An agent reasons about the situation that rule flagged.</b>"
						),
						h("Where the agent can still trip", 3),
						p(
							"AI agents genuinely can miss important details. They can misread surrounding context. They can recommend the wrong action entirely. They can sound completely confident even while standing on relatively weak evidence. This program is not only teaching you what AgentSOC's agents do behind the scenes, it is deliberately teaching you how to check their work, question their conclusions, and catch the moments where their reasoning falls short."
						),
						*takeaways(
							[
								"A chatbot responds to a question, automation follows a fixed rule, and an agent works through an entire task toward a goal",
								"AI agents can meaningfully help SOC teams investigate faster and cover far more ground",
								"Agent output should always be verified through human review, never trusted blindly",
								"AgentSOC relies on a coordinated chain of AI agents to support the security workflow from start to finish",
							]
						),
						yt("agents", "AI Agents, Clearly Explained"),
						quiz_block(q["w1-agents"]),
					],
				),
				(
					"Week 1 Lab: Set Up Your Home Lab",
					0,
					[
						h("Week 1 Lab: Set Up Your Home Lab"),
						img("terminal", "Your lab machine becomes the stage for every simulation."),
						p(
							"In this lab, you will stand up a machine that AgentSOC can actively monitor. This machine will serve as the stage for every simulated attack you run for the remainder of the program, so it is worth taking the time to get it connected and confirmed correctly before moving forward."
						),
						h("Step 1: Choose your setup path", 3),
						p(
							"Use a <b>local virtual machine</b> if your computer has sufficient resources: VirtualBox or VMware, an Ubuntu Linux VM, at least two CPU cores, at least 2 GB of RAM, and at least 20 GB of available disk space. Use the <b>VPS fallback</b> if your computer is slow, has limited RAM, or cannot run virtualization reliably: a free or low-cost VPS from GCP, AWS, Hostinger, or another approved provider, running Ubuntu Linux server with SSH access enabled."
						),
						h("Step 2: Install or prepare the machine", 3),
						p(
							"Follow the setup guide provided in the LMS. If you are using a local VM, install the Linux operating system and confirm the machine boots successfully. If you are using a VPS, create the server and confirm that you can connect to it using SSH."
						),
						h("Step 3: Connect the machine to AgentSOC", 3),
						p(
							"Open the AgentSOC connection page, copy the connection script it provides, run that script on your lab machine, and wait for the installation to finish completely."
						),
						h("Step 4: Confirm the connection inside AgentSOC", 3),
						p(
							"Return to AgentSOC, open the Assets or Machines page, and confirm that your lab machine now appears as connected, active, or online. The moment your machine appears there, it stops being just a server sitting in isolation. It becomes part of the actively monitored environment."
						),
						h("Step 5: Take a screenshot", 3),
						p(
							"Take a clear screenshot showing your connected machine inside AgentSOC. This screenshot becomes part of your Week 1 submission."
						),
						h("⚠️ Lab safety reminder", 3),
						p(
							"Only connect machines that you personally own or are explicitly authorized to use. Do not install the agent on any work, school, or shared system unless you have received explicit permission. Do not connect real company systems, real customer systems, or any production system to this training environment under any circumstances."
						),
						yt("lab", "Lab setup walkthrough: building a cyber security virtual lab"),
					],
				),
				(
					"Week 1 Submission",
					0,
					[
						h("Week 1 Submission"),
						p(
							"Submit the following three items to unlock the <b>Week 1 Stripe: Foundations Complete</b>."
						),
						ul(
							[
								"A screenshot of your connected machine inside AgentSOC",
								"A short prediction for what you expect to happen in Week 2",
								"A sample LinkedIn post",
							]
						),
						h("Prediction prompt", 3),
						p(
							"Before you run any attacks, write three to five sentences answering the following: what do you expect AgentSOC to show you when you run your first simulated attack next week? Consider whether you expect an alert to appear, what severity you would guess it will carry, what information you think the resulting alert will include, what you suspect might be confusing about it, and what you think the AI agent might help explain that you would otherwise miss on your own."
						),
						h("LinkedIn post", 3),
						p(
							"Remember that your post is public. Do not include sensitive details, private screenshots, IP addresses, credentials, or anything drawn from a real company system. Keep the post focused honestly on what you learned."
						),
						h("Sample post", 4),
						p(
							"<i>This week I started the Jutsu Ambassador Program and set up my first cybersecurity lab environment. I connected a lab machine to AgentSOC and got my first real look at how security monitoring works from the defender's side. Before this, \"SOC\" felt like a big, abstract term. Now I can see the basic workflow: connect systems, collect activity, review alerts, and investigate what happened. Next week I'll run my first controlled attack simulation in a lab and compare what I expected to see with what appears in AgentSOC. #Cybersecurity #SOC #SecurityOperations #Jutsu #AgentSOC</i>"
						),
					],
				),
			],
		),
		(
			"Week 2: Threat Intel and Detection",
			[
				(
					"Threat Intelligence and IP Enrichment",
					0,
					[
						h("Threat Intelligence and IP Enrichment"),
						img("fiber", "Raw traffic tells you nothing until it is enriched."),
						*objectives(
							[
								"Explain what threat intelligence is and where it comes from",
								"Understand what enrichment means in the context of a security alert",
								"Describe how IP reputation can meaningfully shape an investigation",
								"Recognize the real limits of threat intelligence as a source of evidence",
								"Explain how AgentSOC's AI agents support enrichment automatically",
							]
						),
						p(
							"Picture a connection arriving from an unfamiliar IP address. On its own, that address tells you almost nothing useful. Is it harmless? A known attacker? Part of a botnet? Has it been used in phishing campaigns before? Threat intelligence exists specifically to answer questions like these."
						),
						h("What enrichment really means", 3),
						p(
							"A raw alert might read <i>multiple failed login attempts from 198.51.100.25</i>, and by itself, that tells you very little. An enriched version of that same alert adds the IP address's reputation, its country of origin, its network owner, whether it is known to be malicious, whether it has appeared in previous attacks, related threat intelligence tags, and any historical activity tied to that address inside your own environment."
						),
						h("Threat intelligence is evidence, never proof", 3),
						p(
							"An IP address flagged as malicious does not automatically mean the current activity in front of you is malicious. An IP address with no known reputation does not automatically mean it is safe. Attackers rotate their infrastructure constantly, legitimate systems occasionally get mislabeled, and large shared cloud providers routinely host both perfectly normal traffic and genuinely malicious traffic side by side."
						),
						h("How AI agents handle enrichment and detection together", 3),
						p("A simplified version of the AgentSOC flow looks like this:"),
						ol(
							[
								"An event is collected",
								"The event is normalized by a <b>normalizer agent</b>, so it reads consistently across every source",
								"An alert is created",
								"The alert is enriched by an <b>enrichment agent</b> with IP reputation, geolocation, and related historical activity",
								"The alert is assessed by a <b>triage or reasoning agent</b>, which explains in plain language what it believes is happening",
								"A <b>response agent</b> may recommend, or in some cases initiate, a concrete next step",
								"A human analyst reviews the result",
							]
						),
						p(
							"The core idea worth holding onto: AgentSOC is never simply showing you a static alert sitting on a screen. It is actively building layered context around that alert before you ever look at it, and that context still deserves your own independent review."
						),
						*takeaways(
							[
								"Threat intelligence provides context about known threats drawn from many outside sources",
								"Enrichment adds useful, structured information to otherwise raw, unstructured alerts",
								"IP reputation can meaningfully help prioritize which investigations deserve attention first",
								"Threat intelligence is useful supporting evidence, but it is never absolute proof on its own",
								"AI-generated context is meant to support your investigation, never to replace it entirely",
							]
						),
						yt("intel", "Cyber Threat Intelligence Explained"),
						quiz_block(q["w2-intel"]),
					],
				),
				(
					"Detection Engineering Basics",
					0,
					[
						h("Detection Engineering Basics"),
						img("switch", "A detection rule decides where 'ordinary' ends."),
						*objectives(
							[
								"Explain the meaningful difference between an event and an alert",
								"Understand what a detection rule is and how it functions",
								"Explain why even well-built detections are never perfect",
								"Describe how repeated login failures can escalate into a genuine alert",
								"Understand how AgentSOC's agents reason about detection context after a rule fires",
							]
						),
						p(
							"An event is simply a record of something that happened: a user logged in, a user failed to log in, a file was opened, a process started, a network connection occurred. Not every event carries any real danger. An alert is created only once one or more events match logic that a detection engineer has judged suspicious enough to flag. One failed login might be completely normal. Twenty failed logins within two minutes, against the same account, might reasonably be considered suspicious."
						),
						h("Why detection engineering is genuinely difficult", 3),
						p(
							"Detection is difficult because normal human behavior and attacker behavior can look remarkably similar from the outside. A real employee who has simply forgotten their password may generate a long string of failed logins that looks nearly identical, at the event level, to an attacker methodically guessing passwords. The detection rule fires an alert in either case, but only a careful analyst, working through the surrounding context, can tell the two apart."
						),
						h("Detection is never perfect, and that is expected", 3),
						p(
							"A rule tuned too sensitively generates an overwhelming number of false positives, burying analysts in noise. A rule tuned too loosely misses real attacks entirely. The goal was never to generate the largest possible number of alerts. The goal is to generate alerts that are genuinely useful, worth an analyst's limited time and attention."
						),
						h("Password spray versus brute force", 3),
						p(
							"A <b>password spray</b> attack uses a single common password tried against many different usernames. A <b>brute force</b> attack instead uses many different passwords tried against a single username. Both patterns are genuinely suspicious, and both are worth an analyst's attention, but they leave behind noticeably different evidence trails, which is exactly what makes comparing them side by side such a useful learning exercise."
						),
						*takeaways(
							[
								"Events are simple records of activity; not every event carries real danger on its own",
								"Alerts are created only when activity matches logic that a team has judged suspicious",
								"Detection rules define, in advance, exactly what should trigger an alert",
								"Detection is never perfect, and tuning it is an ongoing, deliberate effort",
								"AI agents help explain why a detected pattern matters, closing the gap between trigger and understanding",
							]
						),
						yt("detection", "Detection engineering with Wazuh — how events become alerts"),
						quiz_block(q["w2-detection"]),
					],
				),
				(
					"Week 2 Lab: Run Your First Controlled Attack Simulation",
					0,
					[
						h("Week 2 Lab: Run Your First Controlled Attack Simulation"),
						img("rack", "Controlled activity, in your own approved lab, only."),
						h("⚠️ Safety reminder", 3),
						p(
							"Only perform this lab against your own approved lab machine. Never run password attacks against public systems, company systems, school systems, or any system where you lack explicit permission. This lab exists strictly for controlled, defensive training. Never use real company usernames, real customer data, real passwords, or real employer systems while completing it."
						),
						ol(
							[
								"<b>Prepare your lab environment.</b> Confirm your Week 1 lab machine is online and visible inside AgentSOC, and that you can access your approved attacker machine or terminal environment.",
								"<b>Install the required testing tool.</b> Follow the setup instructions provided in the LMS. Confirm the tool installed successfully, and do not use it outside this lab environment.",
								"<b>Run a password spray simulation.</b> One password attempted across multiple usernames. The goal is never to break into a real system — it is to generate activity that AgentSOC can detect, enrich, and explain.",
								"<b>Review the alert inside AgentSOC.</b> Record the alert ID, title, severity, source IP, target machine, affected usernames, timeline, enrichment data, and AgentSOC's own assessment. Screenshot the enrichment data specifically.",
								"<b>Run a brute force simulation.</b> Many passwords attempted against a single username. Wait for AgentSOC to detect and process the activity.",
								"<b>Compare both alerts.</b> Did they carry the same severity? The same source IP? Did the affected usernames differ? Did enrichment change your understanding? Which struck you as more serious, and why?",
								"<b>Identify the agentic enrichment.</b> In two or three sentences: what context did AgentSOC add, which part most helped you understand what happened, and did the agentic explanation genuinely make the alert clearer?",
							]
						),
						yt("spray", "Brute force vs password spray attacks explained"),
					],
				),
				(
					"Week 2 Submission",
					0,
					[
						h("Week 2 Submission"),
						p(
							"Submit the following to unlock the <b>Week 2 Stripe: Threat Intelligence and Detection Complete</b>."
						),
						ul(
							[
								"Password spray alert ID",
								"Brute force alert ID",
								"A screenshot showing enrichment data",
								"A reflection comparing your Week 1 prediction with what appeared",
								"A short note on AgentSOC's enrichment or assessment",
								"A sample LinkedIn post",
							]
						),
						h("Reflection prompt", 3),
						p(
							"Write five to seven sentences answering the following: what did you predict back in Week 1, what genuinely appeared inside AgentSOC once you ran your simulations, what surprised you along the way, did the enrichment data meaningfully help your understanding, which alert struck you as more serious and why, and did AgentSOC's agentic explanation help you make sense of what you were looking at?"
						),
						h("Sample post", 4),
						p(
							"<i>This week in the Jutsu Ambassador Program, I ran my first controlled security simulation inside a lab environment. I tested two login attack patterns, password spray and brute force, and then reviewed the resulting alerts in AgentSOC, comparing severity, source details, affected users, enrichment data, and the agentic explanation attached to each. The biggest lesson for me was that an alert is never the full story by itself. Context matters. #Cybersecurity #SOC #ThreatDetection #AgentSOC #Jutsu</i>"
						),
					],
				),
			],
		),
		(
			"Week 3: Triage",
			[
				(
					"True Positive, False Positive, and False Negative",
					0,
					[
						h("True Positive, False Positive, and False Negative"),
						img("desk", "Triage is where an alert becomes a defensible judgement."),
						*objectives(
							[
								"Define a true positive with a clear, concrete example",
								"Define a false positive with a clear, concrete example",
								"Define a false negative with a clear, concrete example",
								"Understand why triage sits at the center of SOC work",
								"Recognize that 'needs further investigation' is a genuinely valid, temporary verdict",
							]
						),
						p(
							"Alerts are not final answers. They are signals suggesting that something might be worth a closer look. Triage is the process of deciding, with real evidence behind the decision, what that signal genuinely means."
						),
						h("True positive", 3),
						p(
							"The alert correctly identified real suspicious or malicious activity. An alert flags possible brute force activity, and once the analyst reviews the logs, they confirm that a single source genuinely attempted many different passwords against the same account within a short window."
						),
						h("False positive", 3),
						p(
							"The alert fired, but the underlying activity was never malicious. An alert flags possible brute force activity, and once investigated, it turns out an employee simply forgot their password and kept retrying it in frustration. False positives are a completely normal, expected part of security work."
						),
						h("False negative", 3),
						p(
							"Malicious activity genuinely happened, but the system failed to detect it. This is often considerably more dangerous than a false positive, precisely because no alert gets created at all, leaving the organization with no signal that anything went wrong."
						),
						h("Needs further investigation", 3),
						p(
							"Sometimes there simply is not enough information available to decide responsibly. This is not a failure on the analyst's part. It is genuinely better to be honest about uncertainty than to commit to a decision before the evidence supports one."
						),
						*takeaways(
							[
								"A true positive means the alert correctly identified real suspicious activity",
								"A false positive means the alert fired, but the underlying activity was not malicious",
								"A false negative means malicious activity happened, but the system failed to catch it",
								"'Needs further investigation' is a fully valid, temporary verdict when evidence is genuinely incomplete",
								"Triage sits at the daily, decision-making center of SOC work",
							]
						),
						quiz_block(q["w3-verdicts"]),
					],
				),
				(
					"The Full Triage Process",
					0,
					[
						h("The Full Triage Process"),
						img("control2", "Build the story piece by piece, then decide."),
						*objectives(
							[
								"Follow a structured, repeatable alert triage process from start to finish",
								"Identify the source, target, user, and timeline behind an alert",
								"Use enrichment data effectively as part of your investigation",
								"Compare your own independent judgment against AgentSOC's assessment",
								"Write a short, clear justification for your final triage verdict",
							]
						),
						ol(
							[
								"<b>Read the alert title.</b> Treat it as your starting hypothesis, not a confirmed fact.",
								"<b>Check the severity.</b> Does it genuinely match the activity you are seeing, or does something feel off?",
								"<b>Identify the source.</b> Internal or external? Known malicious? An expected location? Seen here before?",
								"<b>Identify the target.</b> Which machine, which account, is it privileged, is it production or lab?",
								"<b>Review the timeline.</b> When did it start and end, how many attempts, and did a successful login eventually follow?",
								"<b>Review enrichment.</b> Reputation, country, network, threat intel tags — does it support or weaken the alert's hypothesis?",
								"<b>Look for related activity.</b> Other alerts from the same source or against the same user? Any outbound connection afterward?",
								"<b>Decide a verdict.</b> True positive, false positive, or needs further investigation.",
								"<b>Write triage notes.</b> Clear enough that another analyst could follow your decision cold.",
							]
						),
						h("Checking the agent's reasoning, not just your own", 3),
						p(
							"Before settling on your final verdict, review AgentSOC's own assessment. What verdict or severity did it suggest, what evidence did it explicitly mention, did it explain its reasoning clearly, did it miss anything you personally noticed, did it lean too heavily on a single piece of evidence, and do you agree with its conclusion? <b>Do not treat the agent's assessment as automatically correct simply because an AI produced it. Do not dismiss it either.</b> Treat it as one more source of evidence."
						),
						h("Example triage note", 3),
						p(
							"<i>Alert: Possible SSH Brute Force Attempt. Triggered by repeated failed login attempts against the lab machine. Source IP 198.51.100.25, target the Ubuntu lab server. Activity occurred over a short window and involved many password attempts against one user account. Enrichment showed the source was external, but no confirmed malicious reputation was found. AgentSOC marked the activity as suspicious login behavior and suggested it was likely brute force activity. <b>Verdict: True positive.</b> Justification: this was controlled lab activity, but the alert correctly detected brute force behavior. I agree with AgentSOC's assessment because the timeline and repeated failed logins support the brute force explanation. Recommended next step: document the activity and use it for the Week 4 incident response exercise.</i>"
						),
						*takeaways(
							[
								"Triage should follow a structured, repeatable process rather than an ad hoc gut check",
								"Alert title and severity are useful starting points, never final answers",
								"Source, target, user, timeline, and enrichment data all genuinely matter to a sound verdict",
								"AgentSOC's assessment should be reviewed carefully, never accepted blindly",
								"Triage notes should be understandable to another person reading them for the first time",
							]
						),
						yt("triage", "SOC alert triage explained: what most beginners get wrong"),
					],
				),
				(
					"Week 3 Lab: Full Alert Walkthrough",
					0,
					[
						h("Week 3 Lab: Full Alert Walkthrough"),
						img("monitors", "One alert, worked end to end."),
						p(
							"In this lab, you will open one of your Week 2 alerts and complete a fully structured triage process on it, deciding whether it is a true positive, a false positive, or something that needs further investigation, and then comparing your own verdict directly against AgentSOC's assessment."
						),
						ol(
							[
								"<b>Choose an alert</b> — either your brute force alert or your password spray alert.",
								"<b>Review the alert title and severity.</b> Write down the title, severity, and alert ID.",
								"<b>Identify the source.</b> Source IP, country, reputation, internal or external.",
								"<b>Identify the target.</b> Machine, user or users, and whether the target belongs to your own lab.",
								"<b>Review the timeline.</b> Start time, end time, number of attempts, and whether any successful login occurred.",
								"<b>Review enrichment data.</b> IP reputation, threat intel tags, geographic information.",
								"<b>Review AgentSOC's assessment.</b> What did it suggest, what evidence did it mention, did it miss anything you noticed?",
								"<b>Make your verdict.</b> True positive, false positive, or needs further investigation.",
								"<b>Compare your verdict with AgentSOC.</b> If it matched, what evidence led you to agree? If not, why did your judgment diverge?",
								"<b>Write triage notes</b> using the format: Alert ID, title, severity, source, target, timeline, key evidence, AgentSOC's assessment, whether your verdict matched, verdict, justification, recommended next step.",
							]
						),
					],
				),
				(
					"Week 3 Submission",
					0,
					[
						h("Week 3 Submission"),
						p("Submit the following to unlock the <b>Week 3 Stripe: Triage Complete</b>."),
						ul(
							[
								"Completed triage notes",
								"Your final verdict",
								"A screenshot of the alert you triaged",
								"A note comparing your verdict with AgentSOC's assessment",
								"A sample LinkedIn post",
							]
						),
						h("Sample post", 4),
						p(
							"<i>This week in the Jutsu Ambassador Program, I completed my first alert triage exercise. I reviewed a simulated login attack alert inside AgentSOC and worked through the evidence step by step: alert title, severity, source IP, target machine, timeline, enrichment data, related activity, and AgentSOC's own assessment. The biggest lesson for me was that triage is not simply clicking true positive or false positive. It is about explaining your reasoning clearly enough that another analyst could read your notes and understand exactly how you reached your decision. #Cybersecurity #SOCAnalyst #Triage #AgentSOC #Jutsu</i>"
						),
					],
				),
			],
		),
		(
			"Week 4: The Broader Security Landscape",
			[
				(
					"Incident Response Beyond Detection",
					0,
					[
						h("Incident Response Beyond Detection"),
						img("control2", "Triage asks what it means. Response asks what to do."),
						*objectives(
							[
								"Explain what incident response is and how it differs from triage",
								"Understand the four basic phases: containment, eradication, recovery, and lessons learned",
								"Connect your Week 3 alert triage directly to a real incident response mindset",
								"Write a clear, structured incident report",
							]
						),
						p(
							"Triage answers one question: what does this alert genuinely mean? Incident response answers a different, follow-up question: <b>what should we do about it?</b>"
						),
						h("Containment", 3),
						p(
							"Stopping the threat from spreading further or causing additional damage: blocking a suspicious IP address, disabling a compromised account, isolating a machine from the network, removing public access from an exposed cloud resource, pausing suspicious access tokens. Containment is usually the first urgent action a team takes."
						),
						h("Eradication", 3),
						p(
							"Removing the underlying cause, not just stopping its immediate spread: removing malware, deleting unauthorized access keys, patching a vulnerable service, fixing a misconfiguration, resetting compromised credentials. <b>Containment stops the bleeding. Eradication removes the root problem.</b>"
						),
						h("Recovery", 3),
						p(
							"Returning affected systems to a safe, normal working state: restoring from a clean backup, re-enabling a user account after a password reset, bringing a machine back online after it has been cleaned, confirming that logging is functioning correctly. Recovery should never happen too early."
						),
						h("Lessons learned", 3),
						p(
							"Honestly reviewing what happened and using that review to improve. How did we detect the issue, did we detect it quickly enough, what evidence was missing, which response actions worked well, do we need a new detection rule? This phase is what turns a single incident into genuine, long-term improvement."
						),
						*takeaways(
							[
								"Triage decides what an alert means; incident response decides what to do about it",
								"Containment limits damage as quickly as possible",
								"Eradication removes the underlying root cause of the incident",
								"Recovery returns systems to a safe, normal state, and should never happen prematurely",
								"Lessons learned turn a single incident into meaningful, long-term security improvement",
							]
						),
						yt("ir", "Incident response process explained"),
						quiz_block(q["w4-ir"]),
					],
				),
				(
					"Cloud Security Fundamentals",
					0,
					[
						h("Cloud Security Fundamentals"),
						img("cloud", "The provider secures the cloud; you secure what you build on it."),
						*objectives(
							[
								"Explain what cloud security means in practical terms",
								"Understand the shared responsibility model between cloud provider and customer",
								"Recognize why misconfiguration is such a common cloud security problem",
								"Describe a realistic exposed storage bucket scenario",
							]
						),
						h("The shared responsibility model", 3),
						p(
							"The clearest way to state it: <b>the cloud provider secures the cloud itself, while the customer secures what they build on top of it.</b> The provider typically handles physical data centers, hardware, core networking, power and cooling, and the availability of managed services. The customer typically handles user access, permissions, application security, data classification, storage bucket access, network rules, logging, monitoring, secrets and credentials, and ongoing configuration."
						),
						p(
							"A meaningful share of real-world cloud incidents happen because the customer side of this shared model was misconfigured, not because the underlying provider failed at their part."
						),
						h("Example: an exposed storage bucket", 3),
						p(
							"Imagine a company storing customer files inside a cloud storage bucket that should only be accessible to approved employees. Someone on the team accidentally makes that bucket public, and now anyone with the link may be able to view or download the data inside it. This is not a failure on the cloud provider's part. It is a customer configuration problem, and a remarkably common one."
						),
						h("Cloud-native alerts a SOC analyst will meet", 3),
						ul(
							[
								"A suspicious cloud login",
								"A new administrator user created unexpectedly",
								"A public storage bucket",
								"An exposed access key",
								"Security logging being disabled",
								"Unusual data download activity",
								"A permission change on a genuinely sensitive resource",
							]
						),
						*takeaways(
							[
								"Cloud security protects cloud-hosted systems and the data stored inside them",
								"Security responsibility is genuinely shared between the cloud provider and the customer",
								"Customers are responsible for permissions, configurations, users, and data protection",
								"Misconfiguration remains one of the most common cloud security risks organizations face",
								"SOC analysts increasingly need working knowledge of cloud-native alerts",
							]
						),
						yt("cloud", "The shared responsibility model for beginners"),
						quiz_block(q["w4-cloud"]),
					],
				),
				(
					"Compliance Basics",
					0,
					[
						h("Compliance Basics"),
						img("records", "Security work is also about proving the right thing was done."),
						*objectives(
							[
								"Explain compliance in clear, practical terms",
								"Understand what SOC 2 and ISO 27001 mean at a high level",
								"Recognize why logging, triage, and documentation genuinely matter for compliance",
								"Connect your work in this program to real business security requirements",
							]
						),
						p(
							"Compliance means consistently following required rules, standards, or frameworks. Compliance is not the same thing as security, though the two are closely connected. A company can be technically compliant and still carry real security weaknesses. A company can also have genuinely strong security practices while still lacking the documentation needed to prove it to an outside auditor."
						),
						h("What is SOC 2?", 3),
						p(
							"A widely used security and compliance framework, especially common among technology companies, focused specifically on how a company protects customer data. SOC 2 typically examines security, availability, confidentiality, processing integrity, and privacy."
						),
						h("What is ISO 27001?", 3),
						p(
							"An international standard for information security management, helping organizations build and maintain a formal information security management system over time: identifying real risks, building meaningful controls, documenting the resulting processes, and continuously improving."
						),
						h("Why documentation genuinely matters", 3),
						p(
							"Security work is never only about doing the right thing in the moment. It is equally about proving, later, that the right thing was genuinely done. The work you have completed throughout this program — collecting alerts, reviewing logs, writing triage notes, comparing your own judgment against AgentSOC's assessment, and building a full incident report — is the exact same kind of evidence real organizations depend on every day."
						),
						p(
							"Once AI agents become genuinely involved in security decisions and actions, documentation becomes even more critical, because organizations increasingly need to show not only what a human decided, but also what an AI agent recommended, and precisely why it made that recommendation."
						),
						*takeaways(
							[
								"Compliance helps organizations prove, with evidence, that they follow required security expectations",
								"SOC 2 is a widely used compliance framework among technology companies",
								"ISO 27001 is an international standard for ongoing information security management",
								"Logs, alerts, triage notes, and incident reports all serve as important compliance evidence",
								"AI agent recommendations should be documented whenever they meaningfully influence a security decision",
							]
						),
						yt("compliance", "SOC 2 compliance: everything you need to know"),
						quiz_block(q["w4-compliance"]),
					],
				),
				(
					"Human Oversight of Autonomous Response",
					0,
					[
						h("Human Oversight of Autonomous Response"),
						img("robot", "The agent prepares the decision. The human keeps the call."),
						*objectives(
							[
								"Explain what autonomous response means in practical terms",
								"Understand why automatic response can be genuinely useful",
								"Understand why automatic response can also be genuinely risky",
								"Describe the meaningful difference between recommendation, approval, and autonomous action",
								"Think critically about when a human should stay firmly in the loop",
							]
						),
						p(
							"The next question, and it is arguably the defining question of agentic security, is this: <b>should an AI agent only recommend what to do, or should it be allowed to take action entirely on its own?</b> There is no single answer that applies cleanly to every organization or every situation."
						),
						h("Three levels of agent action", 3),
						ol(
							[
								"<b>Recommend.</b> The agent explains what it believes should happen, without taking any action itself. The safest level, and especially appropriate for beginners and for any action with high potential impact.",
								"<b>Ask for approval.</b> The agent prepares a specific action but waits for a human to sign off. <i>I can block this IP address for twenty-four hours, approve or reject?</i> The human stays firmly in control while the agent reduces the manual work.",
								"<b>Act automatically.</b> The agent takes the action immediately. Powerful, because real attacks often move faster than any human approval process — and risky, because if the agent's judgment is wrong it might block a legitimate user or disable a critical account with nobody able to catch the mistake beforehand.",
							]
						),
						h("Why it can genuinely help", 3),
						p(
							"A known malicious IP actively attacking multiple systems, malware actively spreading, a compromised token being actively used, a brute force attack in progress, or a cloud resource accidentally left public are all situations where waiting for a human to manually approve every step can genuinely increase the damage done."
						),
						h("Why it can also be genuinely risky", 3),
						p(
							"Blocking an IP address might inadvertently block a legitimate customer. Disabling an account might accidentally lock out a company executive mid-work. Isolating a machine might interrupt an active production process. Revoking a token might silently break a business-critical integration."
						),
						h("The human-in-the-loop principle", 3),
						p(
							"Human-in-the-loop means a person reviews or explicitly approves an important decision before any action is taken on it. This matters especially when the action could disrupt real users, when the affected asset is a production system, when the affected account holds privileged access, when the available evidence is incomplete, or when the action would be difficult to reverse. <b>Human oversight does not mean the AI agent is useless. It means the agent helps prepare a well-informed decision, while the human retains the final call.</b>"
						),
						*takeaways(
							[
								"Autonomous response means an AI agent can take action without waiting for human approval first",
								"Some response actions are genuinely safer to automate than others",
								"Recommendation, approval, and automatic action represent three distinct levels of agent autonomy",
								"Faster response can meaningfully reduce damage during an active, ongoing attack",
								"An incorrect automated response can meaningfully disrupt real users or real systems",
								"Strong security teams deliberately decide where automation is safe and where human approval remains required",
							]
						),
						yt("hitl", "What is human in the loop with AI?"),
						quiz_block(q["w4-oversight"]),
					],
				),
				(
					"Week 4 Lab: Incident Response Exercise",
					0,
					[
						h("Week 4 Lab: Incident Response Exercise"),
						img("datacenter", "The capstone: turn your triage into a real report."),
						p(
							"In this lab, you will revisit the alert you triaged in Week 3 and turn it into a genuine, structured incident response report. You will also reflect honestly on whether an AI agent should have been allowed to take containment action automatically in that specific situation."
						),
						ol(
							[
								"<b>Review your Week 3 alert.</b> Title, ID, severity, source, target, timeline, enrichment, AgentSOC's assessment, your verdict, and your original triage notes.",
								"<b>Describe what happened.</b> What activity triggered the alert, when did it happen, what system or user was affected, and why was it genuinely suspicious?",
								"<b>Write containment actions.</b> Blocking the source IP, disabling or protecting the affected account, restricting access to the target machine, increasing monitoring, notifying the responsible team.",
								"<b>Write eradication actions.</b> Removing unauthorized access, resetting credentials, patching exposed services, fixing weak passwords, reviewing account permissions.",
								"<b>Write recovery actions.</b> Confirming no successful compromise occurred, restoring system access, re-enabling accounts, monitoring for repeated attempts, validating that logging and detection work.",
								"<b>Write lessons learned.</b> Improving password policy, enabling multi-factor authentication, tuning detection rules, adding rate limiting, improving documentation, adding better alert enrichment.",
								"<b>Reflect on autonomous response.</b> If an AI agent had been authorized to take the containment action automatically here, would you have wanted it to, and why or why not?",
								"<b>Complete your final incident report</b> using the template: incident title, alert ID, date and time, severity, summary, affected asset, affected user, source, triage verdict, AgentSOC assessment, evidence reviewed, containment, eradication, recovery, lessons learned, autonomous response reflection, recommended improvements, final status.",
							]
						),
					],
				),
				(
					"Week 4 Closing: Where to Go Next",
					0,
					[
						h("Week 4 Closing: Where to Go Next"),
						img("soc", "Not the end of the path — the entry point."),
						p(
							"Completing this program is meant to be a starting point, not an ending. You now understand the basic SOC workflow from end to end: connecting a monitored asset, generating security activity, reviewing alerts, understanding enrichment, comparing human and AI agent reasoning, making a genuine triage decision, documenting a real incident response report, and thinking critically about when autonomous response should, or should not, be allowed."
						),
						h("Recommended certifications", 3),
						ul(
							[
								"CompTIA Security+",
								"ISC2 Certified in Cybersecurity",
								"Google Cybersecurity Certificate",
								"Microsoft SC-900",
								"AWS Certified Cloud Practitioner, for cloud fundamentals specifically",
							]
						),
						h("Recommended hands-on platforms", 3),
						ul(["TryHackMe", "LetsDefend", "CyberDefenders", "Blue Team Labs", "Hack The Box Academy"]),
						h("Recommended communities", 3),
						ul(
							[
								"Local cybersecurity meetups",
								"LinkedIn cybersecurity groups",
								"Discord communities focused on blue team skills",
								"University security clubs",
								"Capture the Flag communities",
								"Security vendor webinars and workshops",
								"The ongoing Jutsu Ambassador community",
							]
						),
						h("Next 90 days prompt", 3),
						p(
							"Write a short note answering the following: what cybersecurity topic do you genuinely want to keep learning, what certification or platform will you explore next, how many hours per week can you realistically commit to practicing, what kind of role or skill are you most drawn to, and do you want to continue toward the next Jutsu ambassador belt?"
						),
					],
				),
				(
					"Week 4 Submission and Your White Belt Certificate",
					0,
					[
						h("Week 4 Submission"),
						p("Submit the following to unlock the <b>Jutsu White Belt Certificate</b>."),
						ul(
							[
								"Completed incident report",
								"Autonomous response reflection",
								"A short personal next 90 days learning note",
								"Closing LinkedIn post",
							]
						),
						h("Sample post", 4),
						p(
							"<i>I just completed the Jutsu Ambassador Program, a four-week hands-on introduction to security operations and agentic security workflows. Over the program, I set up a lab machine, connected it to AgentSOC, generated controlled security alerts, reviewed enrichment data, completed my first triage decision, compared my reasoning with AgentSOC's assessment, and wrote a full incident response report. I also learned that AI agents can genuinely help analysts move faster, but their reasoning still needs to be checked, every time. #Cybersecurity #SOC #IncidentResponse #BlueTeam #AgentSOC #Jutsu</i>"
						),
						h("Your Jutsu White Belt Certificate", 2),
						p(
							"Four weeks ago, you set up your first lab machine. Since then, you have run controlled attack simulations, reviewed real alerts, studied genuine enrichment data, triaged an alert from start to finish, compared your own judgment against an AI agent's assessment, and written a real incident response report. <b>That is your White Belt, earned.</b> Every stripe on it represents something you personally built, tested, reviewed, and documented, not something handed to you."
						),
						p(
							"This certificate represents completion of an introductory Jutsu training program. It is not a professional certification or industry credential."
						),
						p(
							"Here is the part worth remembering: this is not the end of the path, it is the entry point. Wherever you go next, you are not starting from zero anymore. You have done the work. <b>Welcome to the Jutsu community.</b>"
						),
					],
				),
			],
		),
	]


COURSE_DESCRIPTION = """
<p>A four-week, hands-on introduction to security operations and agentic security.
You will build your own lab, connect it to AgentSOC, run controlled attack
simulations against it, and then investigate what happened alongside a chain of
AI agents rather than a room full of human analysts.</p>
<p><b>Week 1 — Foundations.</b> What cybersecurity means in practice, how a SOC
decides what deserves attention, how alert severity works, and what an AI agent
actually is. You finish the week with a lab machine connected to AgentSOC.</p>
<p><b>Week 2 — Threat Intel and Detection.</b> Watch raw activity become an alert,
run your first controlled password spray and brute force simulation, and see the
enrichment layer add context a raw log entry never could.</p>
<p><b>Week 3 — Triage.</b> Work a real alert end to end, decide whether it is a true
positive, a false positive, or something that still needs digging, and compare
your verdict against the agent's own assessment.</p>
<p><b>Week 4 — The Broader Security Landscape.</b> Incident response, cloud security,
compliance, and the defining question of agentic security: when should an AI
agent be allowed to act on its own?</p>
<p>Each completed week earns one stripe. All four unlock the Jutsu White Belt
Certificate — an introductory training record, not a professional certification.</p>
"""


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


def seed():
	"""Create the whole course. Safe to run more than once."""
	_ensure_category()
	instructor = _ensure_instructor()
	quizzes = {key: _ensure_quiz(key) for key in QUIZZES}
	course = _ensure_course(instructor)

	for chapter_title, lessons in curriculum(quizzes):
		chapter = _ensure_chapter(course, chapter_title)
		for title, preview, blocks in lessons:
			_ensure_lesson(course, chapter, title, preview, blocks)

	graduates = _ensure_graduates(course)

	# lessons/enrollments are denormalized onto the course for the cards.
	frappe.db.set_value(
		"LMS Course",
		course.name,
		"lessons",
		frappe.db.count("Course Lesson", {"course": course.name}),
	)
	frappe.db.set_value(
		"LMS Course",
		course.name,
		"enrollments",
		frappe.db.count("LMS Enrollment", {"course": course.name}),
	)
	frappe.db.commit()

	print(f"Seeded '{COURSE_TITLE}' as {course.name}")
	print(f"  chapters:     {frappe.db.count('Course Chapter', {'course': course.name})}")
	print(f"  lessons:      {frappe.db.count('Course Lesson', {'course': course.name})}")
	print(f"  quizzes:      {len(quizzes)}")
	print(f"  certificates: {len(graduates)}")
	print(f"  open:         /courses/{course.name}")
	for name in graduates:
		print(f"  certificate:  /courses/{course.name}/{name}")
	return course.name


def _ensure_graduates(course):
	"""Enrol the dummy learners, complete the course for them, certify them."""
	lessons = frappe.get_all(
		"Course Lesson", {"course": course.name}, pluck="name", order_by="creation asc"
	)
	issued = []

	for learner in LEARNERS:
		member = _ensure_learner(learner)
		_ensure_enrollment(course, member, learner)
		_complete_lessons(course, member, lessons)
		issued.append(_ensure_certificate(course, member, learner))

	return issued


def _ensure_learner(learner):
	if frappe.db.exists("User", learner["email"]):
		return learner["email"]

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": learner["email"],
			"first_name": learner["first_name"],
			"last_name": learner["last_name"],
			"username": learner["email"].split("@")[0].replace(".", "_"),
			"send_welcome_email": 0,
			"user_type": "Website User",
			# Certified Participants joins User and filters on enabled=1
			# (api.py:get_certification_query), so a disabled learner would be
			# certified and invisible.
			"enabled": 1,
		}
	).insert(ignore_permissions=True)
	return user.name


def _ensure_enrollment(course, member, learner):
	filters = {"member": member, "course": course.name}
	existing = frappe.db.exists("LMS Enrollment", filters)
	doc = (
		frappe.get_doc("LMS Enrollment", existing)
		if existing
		else frappe.new_doc("LMS Enrollment")
	)
	doc.update(
		{
			"member": member,
			"course": course.name,
			"member_name": f"{learner['first_name']} {learner['last_name']}",
			"progress": 100,
		}
	)
	doc.save(ignore_permissions=True)
	return doc


def _complete_lessons(course, member, lessons):
	for lesson in lessons:
		filters = {"member": member, "lesson": lesson, "course": course.name}
		if frappe.db.exists("LMS Course Progress", filters):
			continue
		frappe.get_doc(
			{
				"doctype": "LMS Course Progress",
				"member": member,
				"lesson": lesson,
				"course": course.name,
				"status": "Complete",
			}
		).insert(ignore_permissions=True)


def _ensure_certificate(course, member, learner):
	filters = {"member": member, "course": course.name}
	existing = frappe.db.exists("LMS Certificate", filters)
	doc = (
		frappe.get_doc("LMS Certificate", existing)
		if existing
		else frappe.new_doc("LMS Certificate")
	)
	doc.update(
		{
			"member": member,
			"member_name": f"{learner['first_name']} {learner['last_name']}",
			"course": course.name,
			"course_title": course.title,
			"issue_date": frappe.utils.add_days(frappe.utils.today(), -learner["issued_days_ago"]),
			# Required. The one standard format the app ships
			# (lms/lms/print_format/certificate); www/certificate.py reads this
			# field back to build the PDF URL, so a certificate without it 500s
			# on its own public page.
			"template": CERTIFICATE_TEMPLATE,
			# Certified Participants only lists published ones
			# (api.py:get_certification_query).
			"published": 1,
		}
	)
	doc.save(ignore_permissions=True)

	frappe.db.set_value(
		"LMS Enrollment", {"member": member, "course": course.name}, "certificate", doc.name
	)
	return doc.name


def _ensure_category():
	if not frappe.db.exists("LMS Category", CATEGORY):
		frappe.get_doc({"doctype": "LMS Category", "category": CATEGORY}).insert()


def _ensure_instructor():
	if frappe.db.exists("User", INSTRUCTOR_EMAIL):
		return INSTRUCTOR_EMAIL

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": INSTRUCTOR_EMAIL,
			"first_name": "Jutsu",
			"last_name": "Sensei",
			"username": "jutsu_sensei",
			"send_welcome_email": 0,
			"user_type": "Website User",
		}
	).insert(ignore_permissions=True)
	user.add_roles("Course Creator", "Moderator")
	return user.name


def _ensure_course(instructor):
	existing = frappe.db.exists("LMS Course", {"title": COURSE_TITLE})
	course = frappe.get_doc("LMS Course", existing) if existing else frappe.new_doc("LMS Course")
	course.update(
		{
			"title": COURSE_TITLE,
			"short_introduction": "Build a lab, attack it safely, and triage the alerts alongside a chain of AI agents. Four weeks, one white belt.",
			"description": COURSE_DESCRIPTION,
			"category": CATEGORY,
			"tags": "Cybersecurity, SOC, AgentSOC, Triage, Incident Response, Jutsu",
			"image": IMG["soc"],
			"video_link": VID["soc"],
			"card_gradient": "Cyan",
			"status": "Approved",
			"published": 1,
			"published_on": frappe.utils.today(),
			"featured": 1,
			"enable_certification": 1,
		}
	)
	course.set("instructors", [{"instructor": instructor}])
	course.save(ignore_permissions=True)
	return course


def _ensure_chapter(course, title):
	existing = frappe.db.exists("Course Chapter", {"course": course.name, "title": title})
	if existing:
		return frappe.get_doc("Course Chapter", existing)

	chapter = frappe.get_doc(
		{"doctype": "Course Chapter", "course": course.name, "title": title}
	).insert(ignore_permissions=True)

	course.reload()
	course.append("chapters", {"chapter": chapter.name})
	course.save(ignore_permissions=True)
	return chapter


def _ensure_lesson(course, chapter, title, preview, blocks):
	filters = {"course": course.name, "chapter": chapter.name, "title": title}
	existing = frappe.db.exists("Course Lesson", filters)
	lesson = (
		frappe.get_doc("Course Lesson", existing) if existing else frappe.new_doc("Course Lesson")
	)
	lesson.update(
		{
			"course": course.name,
			"chapter": chapter.name,
			"title": title,
			"include_in_preview": preview,
			"content": content(blocks),
		}
	)
	lesson.save(ignore_permissions=True)

	if not existing:
		chapter.reload()
		chapter.append("lessons", {"lesson": lesson.name})
		chapter.save(ignore_permissions=True)
	return lesson


def _ensure_quiz(key):
	title, questions = QUIZZES[key]
	existing = frappe.db.exists("LMS Quiz", {"title": title})
	if existing:
		return existing

	rows = [_create_question(text, options) for text, options in questions]
	quiz = frappe.new_doc("LMS Quiz")
	quiz.update(
		{
			"title": title,
			"passing_percentage": 70,
			"total_marks": len(rows),
			"show_answers": 1,
			"show_submission_history": 1,
		}
	)
	for name in rows:
		quiz.append("questions", {"question": name, "marks": 1})
	quiz.insert(ignore_permissions=True)
	return quiz.name


def _create_question(text, options):
	doc = frappe.new_doc("LMS Question")
	doc.question = text
	doc.type = "Choices"
	doc.multiple = 0
	for index, (option, is_correct) in enumerate(options, start=1):
		doc.set(f"option_{index}", option)
		doc.set(f"is_correct_{index}", is_correct)
	doc.insert(ignore_permissions=True)
	return doc.name


# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------


def teardown():
	"""Delete everything seed() created, children first."""
	course = frappe.db.exists("LMS Course", {"title": COURSE_TITLE})
	deleted = {
		"certificates": 0,
		"progress": 0,
		"enrollments": 0,
		"lessons": 0,
		"chapters": 0,
		"questions": 0,
		"quizzes": 0,
		"learners": 0,
	}

	if course:
		# Before the lessons: LMS Course Progress links to Course Lesson, so a
		# lesson delete with progress rows still pointing at it raises
		# LinkExistsError. Enrollment likewise points at the certificate.
		for dt, counter in (
			("LMS Certificate", "certificates"),
			("LMS Course Progress", "progress"),
			("LMS Enrollment", "enrollments"),
		):
			if dt == "LMS Enrollment":
				frappe.db.set_value(
					"LMS Enrollment", {"course": course}, "certificate", None, update_modified=False
				)
			for name in frappe.get_all(dt, {"course": course}, pluck="name"):
				frappe.delete_doc(dt, name, force=1, ignore_permissions=True)
				deleted[counter] += 1

		# The child tables hold Link rows to the docs below, so clear the
		# references before deleting their targets or every delete raises
		# LinkExistsError.
		for chapter in frappe.get_all("Course Chapter", {"course": course}, pluck="name"):
			doc = frappe.get_doc("Course Chapter", chapter)
			doc.set("lessons", [])
			doc.save(ignore_permissions=True)

		course_doc = frappe.get_doc("LMS Course", course)
		course_doc.set("chapters", [])
		course_doc.save(ignore_permissions=True)

		for lesson in frappe.get_all("Course Lesson", {"course": course}, pluck="name"):
			frappe.delete_doc("Course Lesson", lesson, force=1, ignore_permissions=True)
			deleted["lessons"] += 1

		for chapter in frappe.get_all("Course Chapter", {"course": course}, pluck="name"):
			frappe.delete_doc("Course Chapter", chapter, force=1, ignore_permissions=True)
			deleted["chapters"] += 1

		frappe.delete_doc("LMS Course", course, force=1, ignore_permissions=True)

	for title, _questions in QUIZZES.values():
		quiz = frappe.db.exists("LMS Quiz", {"title": title})
		if not quiz:
			continue
		question_names = frappe.get_all(
			"LMS Quiz Question", {"parent": quiz}, pluck="question"
		)
		frappe.delete_doc("LMS Quiz", quiz, force=1, ignore_permissions=True)
		deleted["quizzes"] += 1
		for question in question_names:
			if frappe.db.exists("LMS Question", question):
				frappe.delete_doc("LMS Question", question, force=1, ignore_permissions=True)
				deleted["questions"] += 1

	if frappe.db.exists("User", INSTRUCTOR_EMAIL):
		frappe.delete_doc("User", INSTRUCTOR_EMAIL, force=1, ignore_permissions=True)

	for learner in LEARNERS:
		if frappe.db.exists("User", learner["email"]):
			frappe.delete_doc("User", learner["email"], force=1, ignore_permissions=True)
			deleted["learners"] += 1

	if frappe.db.exists("LMS Category", CATEGORY) and not frappe.db.exists(
		"LMS Course", {"category": CATEGORY}
	):
		frappe.delete_doc("LMS Category", CATEGORY, force=1, ignore_permissions=True)

	frappe.db.commit()
	print("Removed the Jutsu seed:", deleted)
