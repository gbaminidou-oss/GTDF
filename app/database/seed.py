# -*- coding: utf-8 -*-
"""
Seed database with modules, lessons, scenarios, questions, answers and badges.
Only runs once — skips if data already present.
"""

import json
from app import db
from app.models.assessment import Question, Answer
from app.models.module import Module, Lesson, Scenario, ScenarioOption
from app.models.gamification import Badge


def seed_all():
    if Module.query.count() > 0:
        return  # already seeded
    _seed_badges()
    _seed_modules()
    _seed_questions()
    db.session.commit()


# ── Badges ────────────────────────────────────────────────────────────────────
def _seed_badges():
    badges = [
        {"name": "Eagle Eye",            "description": "Completed Phishing Recognition module",                "icon": "fa-eye",            "color": "#ef4444"},
        {"name": "Unbreakable",          "description": "Completed Authority and Urgency Resistance module",    "icon": "fa-user-shield",    "color": "#8b5cf6"},
        {"name": "Vault Guardian",       "description": "Completed Credential Security module",                 "icon": "fa-vault",          "color": "#f59e0b"},
        {"name": "Web Detective",        "description": "Completed Safe Browsing module",                       "icon": "fa-magnifying-glass","color": "#06b6d4"},
        {"name": "Human Firewall",       "description": "Completed Pretexting Detection module",                "icon": "fa-shield-halved",  "color": "#ec4899"},
        {"name": "Data Steward",         "description": "Completed Data Handling and Classification module",    "icon": "fa-database",       "color": "#10b981"},
        {"name": "First Responder",      "description": "Completed Incident Reporting module",                  "icon": "fa-bell",           "color": "#3b82f6"},
        {"name": "Assessment Champion",  "description": "Scored ≥75% in the pre-assessment",           "icon": "fa-star",           "color": "#f59e0b", "badge_type": "achievement"},
        {"name": "Speed Learner",        "description": "Completed a module in under 10 minutes",       "icon": "fa-bolt",           "color": "#fbbf24", "badge_type": "achievement"},
        {"name": "Streak Master",        "description": "Answered 10 questions correctly in a row",    "icon": "fa-fire",           "color": "#ef4444", "badge_type": "achievement"},
        {"name": "GTDF Graduate",        "description": "Completed all 7 modules",                     "icon": "fa-graduation-cap", "color": "#6366f1", "badge_type": "special"},
        {"name": "Cybersecurity Aware",  "description": "Passed the post-assessment with ≥75%",        "icon": "fa-shield-halved",  "color": "#10b981", "badge_type": "special"},
    ]
    for b in badges:
        badge = Badge(
            name=b["name"],
            description=b["description"],
            icon=b["icon"],
            color=b["color"],
            badge_type=b.get("badge_type", "module"),
        )
        db.session.add(badge)


# ── Modules & Lessons ─────────────────────────────────────────────────────────
_MODULE_DATA = [
    {
        "order": 1, "domain": "phishing", "title": "Phishing Recognition",
        "description": "Identify and defend against phishing emails and fraudulent communications.",
        "icon": "fa-fish", "color": "#ef4444", "xp_reward": 50, "badge_name": "Eagle Eye",
        "lessons": [
            {"order": 1, "title": "What is Phishing?",
             "content": "Phishing is a cyber-attack where attackers impersonate legitimate organisations to steal sensitive information. Attackers send deceptive emails, messages, or create fake websites that appear authentic. According to the NCSC, phishing accounts for over 80% of reported security incidents.\n\nKey characteristics include:\n• Urgency or fear-based messaging\n• Requests for personal/financial information\n• Suspicious sender addresses\n• Generic greetings (e.g., 'Dear Customer')\n• Grammatical errors or unusual formatting",
             "key_points": '["Phishing uses social engineering to manipulate victims", "Always verify the sender email domain", "Legitimate organisations rarely request credentials via email", "When in doubt, contact the organisation directly"]'},
            {"order": 2, "title": "Spotting a Phishing Email",
             "content": "To detect phishing emails, examine these six key indicators:\n\n1. SENDER ADDRESS — Hover over the sender name. Does the domain match the official website? (e.g. support@paypa1.com vs support@paypal.com)\n\n2. LINKS — Hover before clicking. Check the URL in the status bar. Short links can hide malicious destinations.\n\n3. URGENCY — 'Your account will be closed in 24 hours!' is a manipulation tactic.\n\n4. ATTACHMENTS — Unexpected .exe, .zip, or macro-enabled Office files are dangerous.\n\n5. REQUESTS — Legitimate banks never ask for passwords via email.\n\n6. DESIGN — Poor formatting, low-res logos, and mismatched colour schemes indicate fakes.",
             "key_points": '["Check the actual email domain, not the display name", "Never click links — navigate directly to the website", "Report suspicious emails to your IT/security team", "Enable email authentication (SPF, DKIM, DMARC) on your domain"]'},
            {"order": 3, "title": "Responding to Phishing",
             "content": "When you receive a suspected phishing email:\n\nDO:\n✓ Mark it as spam/phishing in your email client\n✓ Report to your security team immediately\n✓ Forward to the organisation being impersonated (e.g. phishing@bankname.com)\n✓ Delete the email\n\nDO NOT:\n✗ Click any links\n✗ Open attachments\n✗ Reply to the sender\n✗ Enter credentials on any linked page\n\nIf you DID click a link or enter data:\n1. Disconnect from the internet immediately\n2. Change all related passwords from a safe device\n3. Report to IT security\n4. Monitor accounts for suspicious activity",
             "key_points": '["Report phishing — do not just delete", "Change credentials immediately if compromised", "Document the incident for your security team", "Most email clients have a built-in Report Phishing button"]'},
            {"order": 4, "title": "The SLAM Framework — Analysing Any Message",
             "content": "The SLAM framework is a four-point analytical scaffold for evaluating any suspicious email, message, or notification. Work through each letter before acting:\n\nS — SENDER\nExamine the actual email address, not just the display name. Attackers set the display name to 'NatWest Bank' whilst the address is security@natwest-verify.co.uk. Ask: Does the domain after the @ match the organisation's official website exactly? Is there a number substituted for a letter (paypa1.com)? Is it a subdomain used to deceive (paypal.com.phish.net)?\n\nL — LINKS\nHover over every link before clicking — the status bar or tooltip shows the real destination. Ask: Does the URL shown match where the link claims to go? Does it use HTTPS? Does the domain match the sender's official domain? When in doubt, navigate to the website directly by typing it yourself.\n\nA — ATTACHMENTS\nAny unexpected attachment is a red flag. Malicious file types include: .exe, .zip, .js, .doc/.docx with macros, .pdf with embedded scripts. Ask: Were you expecting this file? Does it match the message context? Even if you know the sender — their account may be compromised.\n\nM — MESSAGE\nEvaluate the tone and content. Ask: Is there artificial urgency ('within 24 hours')? Threats ('your account will be closed')? Generic greetings ('Dear Valued Customer')? Requests for credentials, payment, or personal data? Unusual spelling or formatting? Legitimate organisations do not pressurise recipients through email.\n\nApplying SLAM takes less than 60 seconds and catches the overwhelming majority of phishing attempts before any click occurs.",
             "key_points": '["S — Sender: check the actual domain, not the display name", "L — Links: hover to reveal the real URL before clicking", "A — Attachments: treat all unexpected files as suspicious", "M — Message: urgency, threats, and credential requests are manipulation tactics"]'},
        ],
        "scenarios": [
            {
                "title": "Suspicious Bank Email",
                "scenario_type": "email",
                "description": "You receive this email in your inbox. Analyse it carefully.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value suspicious">security@natwest-verify.co.uk</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">you@company.com</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">⚠️ URGENT: Your account has been suspended</span></div>
  </div>
  <div class="email-body">
    <p>Dear Valued Customer,</p>
    <p>We have detected <strong>suspicious activity</strong> on your NatWest account. Your account has been <span style="color:red">TEMPORARILY SUSPENDED</span> for your protection.</p>
    <p>To restore access immediately, please verify your identity by clicking the button below:</p>
    <a href="#" class="fake-btn">Verify My Account Now →</a>
    <p>Failure to verify within <strong>24 hours</strong> will result in permanent account closure.</p>
    <p>NatWest Security Team<br><small>natwest-verify.co.uk | 0800 123 456</small></p>
  </div>
</div>""",
                "question": "What should you do with this email?",
                "correct_action": "report",
                "explanation": "This is a phishing email. Red flags: (1) Domain 'natwest-verify.co.uk' is NOT NatWest's official domain (natwest.com). (2) Creates urgency with '24-hour' threat. (3) Requests you click a link. (4) Generic 'Valued Customer' greeting. Never click such links. Report it.",
                "difficulty": "beginner",
                "time_limit": 60,
                "xp_reward": 25,
                "options": [
                    {"text": "Click 'Verify My Account Now' to restore access", "is_correct": False, "feedback": "Wrong! This link leads to a fake website designed to steal your credentials."},
                    {"text": "Reply to ask if the email is genuine", "is_correct": False, "feedback": "Wrong! Never reply to suspected phishing emails — you confirm your address is active."},
                    {"text": "Report it as phishing and delete it", "is_correct": True, "feedback": "Correct! Always report phishing emails. Contact your bank directly using their official website if concerned."},
                    {"text": "Forward to your colleagues to warn them", "is_correct": False, "feedback": "Partially right intent, but forwarding phishing emails can spread the threat. Report to IT instead."},
                ],
            },
            {
                "title": "Spear Phishing — Targeted HR Email",
                "scenario_type": "email",
                "description": "You receive this email that appears to know personal details about you.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value suspicious">hr-benefits@acme-corp-uk.com</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">j.smith@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Action Required: Update your pension details before 31 October</span></div>
  </div>
  <div class="email-body">
    <p>Dear Jamie,</p>
    <p>Following your recent move to the <strong>Marketing &amp; Communications team</strong>, our benefits system requires you to re-confirm your pension contribution details.</p>
    <p>As you have been with us since <strong>March 2021</strong>, you are now eligible for the enhanced employer contribution. Please use your employee number <strong>ACM-4471</strong> to log in and update your banking details:</p>
    <a href="#" class="fake-btn">Update Pension Details →</a>
    <p>This must be completed by <strong>31 October</strong> or your contributions will revert to the standard rate.</p>
    <p>Kind regards,<br>HR Benefits Team<br>Acme Corporation</p>
  </div>
</div>""",
                "question": "This email uses your real name and employment details. What is the most appropriate response?",
                "correct_action": "verify",
                "explanation": "This is spear phishing — a targeted attack using personal information gathered from LinkedIn, social media, or prior data breaches to appear credible. The sender domain 'acme-corp-uk.com' differs from the legitimate 'acmecorp.co.uk'. The use of personal details creates false trust. Always verify through official HR channels before clicking.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Click the link — it knows your employee number so it must be genuine", "is_correct": False, "feedback": "Personal details can be harvested from LinkedIn and data breaches. Familiarity does not equal legitimacy."},
                    {"text": "Contact HR directly through the company intranet to verify the request", "is_correct": True, "feedback": "Correct! Verify through a known, independent channel. The sender domain is subtly different from your real company domain."},
                    {"text": "Reply to the email asking for confirmation", "is_correct": False, "feedback": "Replying to the attacker confirms your email is active and may provide additional information to them."},
                    {"text": "Forward to a colleague to check if they received the same email", "is_correct": False, "feedback": "Spear phishing is targeted — colleagues may not have received it. Verify through official HR, not peer consensus."},
                ],
            },
            {
                "title": "Smishing — Parcel Delivery SMS",
                "scenario_type": "sms",
                "description": "You receive this text message on your work mobile.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">📱 SMS — Royal Mail UK</div>
  <div class="chat-body">
    <div class="chat-msg received" style="background:#e8f5e9;">
      <strong>Royal-Mail-UK:</strong> Your parcel (GB7743021X) could not be delivered. A customs charge of £2.99 is due. Pay now to avoid return: <span style="color:#1565c0;text-decoration:underline;">http://royalmai1-redelivery.uk/pay</span><br><small style="color:#757575;">Reply STOP to opt out</small>
    </div>
  </div>
</div>""",
                "question": "What should you do with this text message?",
                "correct_action": "report",
                "explanation": "This is smishing (SMS phishing). Red flags: (1) 'royalmai1-redelivery.uk' uses a '1' instead of 'l' — classic typosquatting. (2) Royal Mail uses royalmail.com. (3) Unexpected delivery charge creates urgency. (4) The 'STOP' opt-out is a legitimacy illusion. Report to your IT team and forward to 7726 (SPAM) on your phone.",
                "difficulty": "intermediate",
                "time_limit": 75,
                "xp_reward": 30,
                "options": [
                    {"text": "Pay the £2.99 — it is a small amount and I am expecting a parcel", "is_correct": False, "feedback": "Small amounts are used deliberately to lower your guard. The payment page is designed to harvest your card details."},
                    {"text": "Click the link to see if the parcel tracking looks real", "is_correct": False, "feedback": "The fake page may install malware or redirect to a card-skimming form. Never click links in unsolicited texts."},
                    {"text": "Reply STOP to unsubscribe from the messages", "is_correct": False, "feedback": "Replying confirms your number is active and may increase targeting. The STOP option is a social engineering tactic."},
                    {"text": "Delete the message and check Royal Mail's official website directly for any parcels", "is_correct": True, "feedback": "Correct! Type royalmail.com directly into your browser. Report the smishing attempt to 7726 (SPAM) and your IT security team."},
                ],
            },
            {
                "title": "Homograph Domain Attack — Advanced Visual Deception",
                "scenario_type": "website",
                "description": "You receive this email. Examine it very carefully — you have 45 seconds.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value">security@apple.com</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">j.smith@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Your Apple ID has been locked — immediate action required</span></div>
  </div>
  <div class="email-body">
    <div style="text-align:center; margin-bottom:16px;">
      <div style="font-size:2em;"></div>
      <strong>Apple ID Security Alert</strong>
    </div>
    <p>Your Apple ID has been locked due to suspicious sign-in activity from an unrecognised device.</p>
    <p>To unlock your account, click below and sign in to verify your identity:</p>
    <a href="#" class="fake-btn">Unlock Apple ID →</a>
    <p style="margin-top:16px; font-size:0.85em; color:#555;">
      This link will take you to: <code style="background:#f3f4f6; padding:2px 6px; border-radius:3px;">https://www.&#x430;pple.com/unlock</code>
    </p>
    <p><small>Apple Inc. | One Apple Park Way, Cupertino, CA | apple.com</small></p>
  </div>
</div>
<div style="margin-top:12px; background:#fffbeb; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; font-size:0.8rem; color:#78350f;">
  <strong>Advanced challenge:</strong> Inspect every element. The sender address, branding, and content all appear legitimate. One thing is wrong. What is it, and what should you do?
</div>""",
                "question": "The link destination is 'https://www.аpple.com/unlock' — what is the threat and what should you do?",
                "correct_action": "report",
                "explanation": "This is an IDN homograph attack. The URL uses the Cyrillic letter 'а' (Unicode U+0430) in place of the Latin 'a' (U+0061) — visually identical at normal reading size. The destination is actually xn--pple-43d.com, a completely different domain from apple.com. Even the sender address 'security@apple.com' may be spoofed via domain impersonation. At Advanced tier, the SLAM framework must be applied in full: Sender (verify domain), Links (inspect URL character by character — look for punycode), Attachments (none here), Message (urgency cue: 'locked account'). Report to IT and navigate to apple.com directly to check account status.",
                "difficulty": "advanced",
                "time_limit": 45,
                "xp_reward": 50,
                "options": [
                    {"text": "Click the link — the sender is security@apple.com and the branding looks genuine", "is_correct": False, "feedback": "The domain in the link uses a Cyrillic 'а' not a Latin 'a'. Sender addresses can be spoofed. Visual legitimacy is not proof of legitimacy — inspect the URL character by character."},
                    {"text": "The link URL uses a visually identical Cyrillic character — this is a homograph attack; report it and navigate to apple.com directly", "is_correct": True, "feedback": "Correct! The 'а' in the link URL is Unicode U+0430 (Cyrillic) not U+0061 (Latin). Browsers may display xn--pple-43d.com instead. Inspect links at the character level, especially in high-stakes communications."},
                    {"text": "Forward to a colleague to get a second opinion before clicking", "is_correct": False, "feedback": "Sharing a suspicious link with colleagues risks them clicking it. Report to IT Security, not colleagues. Navigate to apple.com directly to check your account status."},
                    {"text": "The email looks real so it is probably a genuine Apple security alert — unlock the account", "is_correct": False, "feedback": "Visual authenticity is the entire point of a homograph attack. The SLAM framework requires inspecting the actual link URL, not just the visual appearance. One character difference creates a completely different domain."},
                ],
            },
        ],
    },
    {
        "order": 2, "domain": "social_engineering", "title": "Authority and Urgency Resistance",
        "description": "Apply concrete verification techniques to resist social engineering using authority and urgency tactics.",
        "icon": "fa-user-shield", "color": "#8b5cf6", "xp_reward": 50, "badge_name": "Unbreakable",
        "lessons": [
            {"order": 1, "title": "Social Engineering Fundamentals",
             "content": "Social engineering exploits human psychology rather than technical vulnerabilities. Attackers manipulate people into divulging confidential information or performing actions that compromise security.\n\nThe six principles of influence (Cialdini) exploited by attackers:\n1. AUTHORITY — Impersonating executives, IT support, or government officials\n2. URGENCY — Creating time pressure to prevent rational thinking\n3. SCARCITY — 'Only 1 hour left to act'\n4. SOCIAL PROOF — 'Your colleagues have already updated their credentials'\n5. LIKING — Building rapport before the attack\n6. RECIPROCITY — Offering help first to create obligation",
             "key_points": '["Never share passwords even with IT support", "Always verify caller identity through official channels", "Slow down — urgency is a manipulation tactic", "When in doubt, escalate to your manager or security team"]'},
            {"order": 2, "title": "CEO Fraud & Business Email Compromise",
             "content": "CEO Fraud (Business Email Compromise — BEC) is one of the costliest cyber crimes. Attackers impersonate senior executives to pressure employees into:\n• Urgent wire transfers\n• Sharing sensitive HR/financial data\n• Installing software\n• Bypassing approval processes\n\nReal-world impact: BEC caused $2.9 billion in losses in 2023 (FBI IC3).\n\nProtection measures:\n1. Implement call-back verification for wire transfers\n2. Use out-of-band communication to verify unusual requests\n3. Establish financial transfer approval protocols\n4. Train employees to question urgency pressure\n5. Enable multi-factor authentication on all email accounts",
             "key_points": '["Always verify financial requests via phone using a known number", "Legitimate CEOs understand security verification", "BEC attacks often happen on Fridays before weekends", "No email sender address can be fully trusted without DMARC"]'},
            {"order": 3, "title": "The Verification Script — What to Say Under Pressure",
             "content": "Knowing that social engineering attacks should be resisted is not enough. Under real pressure from an authoritative caller, improvising a refusal is genuinely difficult. A pre-learned verbal script removes that difficulty. The goal is to pause the interaction, find an independent verification channel, and only proceed after confirmation — without revealing information or causing unnecessary conflict.\n\nTHE FOUR-STEP VERIFICATION SCRIPT:\n\nSTEP 1 — ACKNOWLEDGE (do not refuse yet):\n'Thank you for calling / for your message. I want to make sure I handle this correctly.'\n\nSTEP 2 — PAUSE THE INTERACTION:\n'For security purposes, I need to verify your identity before I can proceed with any action.'\n\nSTEP 3 — FIND AN INDEPENDENT NUMBER:\n'Could I take your name and callback number? I will contact [the IT helpdesk / your organisation's main switchboard] to confirm this request and call you straight back.'\n\nSTEP 4 — CALL BACK THROUGH A KNOWN CHANNEL:\nDo NOT use the number the caller gave you. Look up the number on the official intranet, company website, or your phone directory, and call that number to verify.\n\nWHY THIS WORKS:\n• It does not accuse the caller of lying — it simply follows policy\n• Legitimate callers always accept this procedure\n• It removes the need to make a real-time judgement under pressure\n• It creates an independent verification trail\n• Attackers almost always abandon the call at Step 3 or 4\n\nIMPORTANT: If the caller claims there is no time for verification, that urgency itself is the attack. Real emergencies have real escalation paths — your manager, your security team — that do not require you to bypass security policy.",
             "key_points": '["A pre-learned script removes the need to improvise under pressure", "Always verify through an independent channel — not a number the caller provides", "Legitimate parties always accept callback verification", "If the caller refuses verification, that refusal is the red flag"]'},
        ],
        "scenarios": [
            {
                "title": "IT Support Phone Call",
                "scenario_type": "phone",
                "description": "You receive an unexpected phone call. Read the transcript carefully.",
                "content_html": """<div class="fake-phone">
  <div class="phone-header">📞 Incoming Call — Unknown Number</div>
  <div class="phone-transcript">
    <div class="caller"><strong>Caller:</strong> "Hi, this is James from the IT Help Desk. We've detected a critical security breach on your workstation. Your account is being used to send malware across the network right now. I need your Windows login credentials immediately so I can remotely fix this before it spreads to the whole company. Management is watching — if we don't resolve this in 5 minutes the CEO has authorised account suspension."</div>
    <div class="you"><strong>You:</strong> "I wasn't expecting this call..."</div>
    <div class="caller"><strong>Caller:</strong> "There's no time! Every second counts. Just give me your username and password now."</div>
  </div>
</div>""",
                "question": "How do you respond to this call?",
                "correct_action": "verify",
                "explanation": "This is a vishing (voice phishing) attack using authority (IT/CEO) and urgency. Legitimate IT staff NEVER ask for passwords over the phone. The correct action is to end the call, look up the IT helpdesk number independently, and report the incident.",
                "difficulty": "beginner",
                "time_limit": 60,
                "xp_reward": 25,
                "options": [
                    {"text": "Give your username and password to resolve the issue quickly", "is_correct": False, "feedback": "Never share passwords! Legitimate IT staff have system-level access and do not need your credentials."},
                    {"text": "Ask for the caller's employee ID then give credentials", "is_correct": False, "feedback": "Still wrong — employee IDs can be fabricated. Always verify through an independent channel."},
                    {"text": "Hang up, find the IT helpdesk number on the company intranet, and call back to verify", "is_correct": True, "feedback": "Correct! Verify through an independent, known channel. Report the call to your security team."},
                    {"text": "Put the caller on hold and ask your manager", "is_correct": False, "feedback": "Better than sharing credentials, but you should end the call and report it — not leave the attacker on hold."},
                ],
            },
            {
                "title": "CEO Urgent Wire Transfer",
                "scenario_type": "email",
                "description": "You work in Finance and receive this email while your manager is on annual leave.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value suspicious">c.harrison@acmecorp-exec.com</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">finance@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Confidential — Urgent Wire Transfer Required Today</span></div>
  </div>
  <div class="email-body">
    <p>Hi,</p>
    <p>I need you to process an urgent wire transfer of <strong>£47,500</strong> to finalise a confidential acquisition we are completing today. Legal have approved this — please do not discuss with colleagues as it is commercially sensitive.</p>
    <p><strong>Bank:</strong> First Commerce Bank<br>
    <strong>Account:</strong> 83920471<br>
    <strong>Sort Code:</strong> 40-12-09<br>
    <strong>Reference:</strong> ACQ-2024-CONF</p>
    <p>Process this before 3pm today. I am in back-to-back meetings but will confirm by email when done. Do NOT call me.</p>
    <p>Thanks,<br>C. Harrison<br>Chief Executive Officer</p>
  </div>
</div>""",
                "question": "What is the correct response to this email?",
                "correct_action": "verify",
                "explanation": "This is a Business Email Compromise (BEC) / CEO fraud attack. Red flags: (1) Sender domain 'acmecorp-exec.com' differs from the real company domain. (2) Requests you not discuss with colleagues. (3) 'Do NOT call me' prevents out-of-band verification. (4) Time pressure. Always verify financial transfers via phone using a known number, regardless of apparent seniority.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Process the transfer — the CEO has authority and it is time sensitive", "is_correct": False, "feedback": "BEC attacks cost organisations billions annually. The sender domain is spoofed. Never transfer funds without out-of-band verification."},
                    {"text": "Reply by email asking for confirmation before transferring", "is_correct": False, "feedback": "Replying to a spoofed address confirms to the attacker that you are engaged. The attacker controls that inbox."},
                    {"text": "Call the CEO on their known phone number to verify before doing anything", "is_correct": True, "feedback": "Correct! Always verify financial requests out-of-band using a pre-known contact number. Legitimate CEOs understand and support this policy."},
                    {"text": "Forward to your manager on annual leave to decide", "is_correct": False, "feedback": "Your manager cannot be reached easily, and this delays a proper security response. Call the CEO directly to verify first."},
                ],
            },
            {
                "title": "Tailgating into Secure Area",
                "scenario_type": "chat",
                "description": "You are approaching the secure server room door with your access badge. Read what happens next.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">🏢 Workplace Scenario — Secure Area Access</div>
  <div class="chat-body">
    <div class="chat-msg received" style="background:#f3f4f6; border-left: 3px solid #6366f1; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
      <strong>Situation:</strong> You badge into the secure server room. As the door begins to close, a person in a high-visibility vest carrying a clipboard calls out: <em>"Hold the door please! I'm from Nexus Facilities — here to check the air conditioning units. My access card isn't working and reception is closed."</em>
    </div>
    <div class="chat-msg received" style="background:#fff8e1; border-left: 3px solid #f59e0b; padding: 14px; border-radius: 8px;">
      <strong>Observation:</strong> The person is wearing a convincing uniform and carrying equipment. They look frustrated and in a hurry.
    </div>
  </div>
</div>""",
                "question": "What is the safest response to this situation?",
                "correct_action": "verify",
                "explanation": "Tailgating (also called piggybacking) is a physical social engineering technique. A professional appearance and a plausible story exploit helpfulness and authority. The correct response is to not hold the door and instead direct the person to reception or security to obtain proper escorted access. Physical security is as important as digital security.",
                "difficulty": "intermediate",
                "time_limit": 75,
                "xp_reward": 30,
                "options": [
                    {"text": "Hold the door — they look legitimate and seem in a hurry", "is_correct": False, "feedback": "Uniforms, clipboards, and urgency are classic social engineering props. Holding the door bypasses physical security controls entirely."},
                    {"text": "Let them in but stay to supervise their work", "is_correct": False, "feedback": "You cannot authorise access for unverified individuals regardless of supervision. This violates your organisation's physical security policy."},
                    {"text": "Do not hold the door; direct them to reception or security to get proper escorted access", "is_correct": True, "feedback": "Correct! All visitors must be properly verified and escorted. A legitimate contractor will understand and follow the proper procedure."},
                    {"text": "Ask to see their ID badge before holding the door", "is_correct": False, "feedback": "Contractor ID badges can be faked or belong to a different organisation. Access must be granted through reception, not informal checks at a secure door."},
                ],
            },
        ],
    },
    {
        "order": 3, "domain": "password_security", "title": "Credential Security",
        "description": "Master password security, MFA, and credential management best practices.",
        "icon": "fa-key", "color": "#f59e0b", "xp_reward": 50, "badge_name": "Vault Guardian",
        "lessons": [
            {"order": 1, "title": "Password Security Fundamentals",
             "content": "Weak passwords are responsible for 81% of hacking-related breaches (Verizon DBIR). A strong password strategy requires:\n\nLENGTH — Minimum 12 characters. Longer = stronger. A 16-character passphrase is stronger than an 8-character complex password.\n\nCOMPLEXITY — Mix uppercase, lowercase, numbers, and symbols.\n\nUNIQUENESS — Never reuse passwords across accounts. One breach = all accounts compromised.\n\nPASSPHRASES — 'Purple-Elephant-Dances-7!' is stronger than 'P@55w0rd' and easier to remember.\n\nPASSWORD MANAGERS — Use a reputable manager (Bitwarden, 1Password) to generate and store unique passwords for every account.",
             "key_points": '["Use a unique password for every account", "Passphrases are both secure and memorable", "A password manager is essential for security", "Enable breach alerts (HaveIBeenPwned)"]'},
            {"order": 2, "title": "Multi-Factor Authentication (MFA)",
             "content": "MFA adds a second layer of verification beyond your password. Even if your password is stolen, MFA blocks 99.9% of automated attacks (Microsoft research).\n\nMFA FACTORS:\n• Something you KNOW — Password / PIN\n• Something you HAVE — Phone app, hardware token, SMS code\n• Something you ARE — Fingerprint, face recognition\n\nMFA TYPES (most to least secure):\n1. Hardware keys (YubiKey) — strongest\n2. Authenticator apps (Google Authenticator, Authy)\n3. Push notifications\n4. SMS codes — convenient but vulnerable to SIM swapping\n\nAlways enable MFA on:\n✓ Email accounts\n✓ Banking and financial services\n✓ Work systems and VPN\n✓ Social media accounts\n✓ Cloud storage",
             "key_points": '["MFA blocks 99.9% of credential-based attacks", "Authenticator apps are more secure than SMS", "Never share MFA codes with anyone", "Enable MFA on all critical accounts today"]'},
        ],
        "scenarios": [
            {
                "title": "Password Reset Request",
                "scenario_type": "email",
                "description": "You receive this password reset email for your work account.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value suspicious">noreply@accounts-google-security.com</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Action Required: Confirm your Google password reset</span></div>
  </div>
  <div class="email-body">
    <div style="text-align:center; padding: 10px;">
      <div style="font-size:2em">🔐</div>
      <h3>Google Account Security Alert</h3>
    </div>
    <p>A password reset was requested for your account. Your temporary password is:</p>
    <div style="background:#f3f4f6; padding:10px; text-align:center; font-size:1.3em; letter-spacing:3px; font-family:monospace;">TempPass2024!</div>
    <p>Please log in at the link below and change this temporary password:</p>
    <a href="#" class="fake-btn">Login to Google Account →</a>
    <p><small>If you did not request this, click here to secure your account.</small></p>
  </div>
</div>""",
                "question": "What is the most important red flag in this email?",
                "correct_action": "report",
                "explanation": "The sender domain 'accounts-google-security.com' is NOT Google's domain (google.com). Google never sends temporary passwords — they send password reset links. This is a credential harvesting attack. Report it and do not click any links.",
                "difficulty": "beginner",
                "time_limit": 60,
                "xp_reward": 25,
                "options": [
                    {"text": "Use the temporary password to log in and change it", "is_correct": False, "feedback": "Wrong! The link leads to a fake login page. Entering your new password there gives it to attackers."},
                    {"text": "The sender domain is not google.com — this is a phishing attempt", "is_correct": True, "feedback": "Correct! 'accounts-google-security.com' is not Google. Legitimate password resets come from google.com. Report this."},
                    {"text": "Click 'secure your account' since you didn't request a reset", "is_correct": False, "feedback": "Both links are malicious. Never click links in suspicious emails regardless of what they claim to do."},
                    {"text": "Forward it to your IT team then use the temporary password", "is_correct": False, "feedback": "Reporting is correct but still do not use the temporary password or click any links."},
                ],
            },
            {
                "title": "MFA Code Requested via Chat",
                "scenario_type": "chat",
                "description": "You receive this message on your work Slack while your MFA app generates a code.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">💬 Slack — IT Security Bot</div>
  <div class="chat-body">
    <div class="chat-msg received">
      <strong>IT-Security-Bot:</strong> 🔒 We are conducting an emergency account security audit across all active sessions. Your account has been flagged for unusual login activity from Germany (IP: 82.145.XX.XX).<br><br>
      To confirm this is not you and LOCK the suspicious session, please reply with the 6-digit code from your authenticator app within the next 3 minutes.<br><br>
      <em>This is an automated security measure — no action = account suspended for investigation.</em>
    </div>
  </div>
</div>""",
                "question": "The Slack message is asking for your MFA code. What do you do?",
                "correct_action": "report",
                "explanation": "This is an MFA phishing / real-time phishing attack. No legitimate security system will ever ask you to share your MFA code — the code is a one-time token that grants account access. Sharing it hands account control to the attacker. Attacker-controlled bots can appear on any platform including Slack. Report this to IT security immediately.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Share the code quickly to lock the suspicious session", "is_correct": False, "feedback": "MFA codes are authentication tokens. Sharing one with anyone — including apparent security tools — gives them access to your account."},
                    {"text": "Share only the last 3 digits for partial verification", "is_correct": False, "feedback": "6-digit TOTP codes cannot be partially shared. The attacker only needs the full code to authenticate as you."},
                    {"text": "Ignore the message and change your password immediately", "is_correct": False, "feedback": "Close — but you should also report this to IT security so they can investigate the Slack bot and warn colleagues."},
                    {"text": "Do not share the code; report this to IT security and investigate via official channels", "is_correct": True, "feedback": "Correct! Legitimate security systems never ask for MFA codes. This is a social engineering attack. Report it immediately."},
                ],
            },
            {
                "title": "Credential Stuffing Alert",
                "scenario_type": "email",
                "description": "You receive this notification about your work email account.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value">security-alerts@microsoft.com</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">j.smith@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Microsoft 365: Sign-in from new location blocked</span></div>
  </div>
  <div class="email-body">
    <div style="padding:10px; border-left: 4px solid #d93025; background: #fff8f8; margin-bottom: 12px;">
      <strong>⚠ Sign-in attempt blocked</strong>
    </div>
    <p>A sign-in to your Microsoft 365 account was blocked because it came from an unusual location.</p>
    <table style="width:100%; border-collapse: collapse; font-size:0.85em;">
      <tr><td style="padding:4px; color:#555;">Time:</td><td style="padding:4px;"><strong>Today, 02:14 AM</strong></td></tr>
      <tr><td style="padding:4px; color:#555;">Location:</td><td style="padding:4px;"><strong>Bucharest, Romania</strong></td></tr>
      <tr><td style="padding:4px; color:#555;">App:</td><td style="padding:4px;"><strong>Microsoft Outlook</strong></td></tr>
    </table>
    <p>If this was not you, your password may have been compromised via a third-party data breach.</p>
    <p>This email was sent from microsoft.com — you do not need to click anything. Log in to Microsoft 365 directly to review activity.</p>
  </div>
</div>""",
                "question": "This alert appears to come from a legitimate Microsoft domain. What action should you take?",
                "correct_action": "verify",
                "explanation": "This email appears legitimate — security-alerts@microsoft.com is a real Microsoft domain and the email correctly advises you not to click links. The correct action is to independently navigate to Microsoft 365 (portal.office.com), change your password, review sign-in logs, and notify IT. This is a real-world credential stuffing alert pattern — someone attempted to use your password, likely obtained from a breach on another site.",
                "difficulty": "advanced",
                "time_limit": 120,
                "xp_reward": 40,
                "options": [
                    {"text": "Ignore it — blocked sign-ins mean the system is working fine", "is_correct": False, "feedback": "A blocked attempt means someone has your password and is actively trying to access your account. Change your password immediately."},
                    {"text": "Navigate directly to portal.office.com, change your password, enable MFA, and notify IT security", "is_correct": True, "feedback": "Correct! Act immediately: change your password (use a unique, strong one), review sign-in activity, enable MFA if not already on, and report to IT."},
                    {"text": "Click the link in the email to review the sign-in activity", "is_correct": False, "feedback": "The email correctly says not to click anything. Even when an email seems genuine, navigate directly to the service rather than using email links."},
                    {"text": "Change only the password for this account", "is_correct": False, "feedback": "If this password was used elsewhere (credential reuse), those accounts are also at risk. Change ALL accounts that used the same or similar password."},
                ],
            },
        ],
    },
    {
        "order": 4, "domain": "safe_browsing", "title": "Safe Browsing",
        "description": "Identify malicious websites, secure your browsing, and avoid drive-by attacks.",
        "icon": "fa-compass", "color": "#06b6d4", "xp_reward": 50, "badge_name": "Web Detective",
        "lessons": [
            {"order": 1, "title": "Identifying Malicious Websites",
             "content": "Malicious websites can steal credentials, install malware, or conduct drive-by downloads. Key indicators:\n\nURL INSPECTION:\n• Check the domain carefully — 'paypa1.com' vs 'paypal.com'\n• Look for HTTPS (padlock icon) — but note this does NOT guarantee legitimacy\n• Subdomains can be deceptive: 'paypal.com.fake-site.com' — the real domain is fake-site.com\n\nCONTENT WARNINGS:\n• Browser security warnings (do not bypass)\n• Requests to disable antivirus\n• Pop-ups requesting immediate software download\n• Poor design quality or broken images\n\nDOWNLOAD SAFETY:\n• Scan downloads with antivirus before opening\n• Only download from official sources\n• Be suspicious of executable files (.exe, .msi, .bat)",
             "key_points": '["HTTPS = encrypted, not safe — criminals use HTTPS too", "Always check the full domain in the address bar", "Never bypass browser security warnings", "Use a reputable browser extension like uBlock Origin"]'},
            {"order": 2, "title": "Safe Download Practices & Search Ad Risks",
             "content": "Attackers exploit internet search to place malicious sites at the top of results. Two key threats:\n\nTYPOSQUATTING:\nAttackers register domains like 'microsft.com' or 'go0gle.com' to intercept users who mistype URLs. These sites may look identical to the real thing.\n\nMALVERTISING (Malicious Advertising):\nAttackers pay for sponsored search result ads that point to malware-distributing sites. The ad may look completely legitimate and appear above the real website in search results.\n\nSAFE DOWNLOAD CHECKLIST:\n1. Search for the software vendor's official website first\n2. Verify the URL matches the official domain before downloading\n3. Avoid clicking sponsored/advertised search results for software downloads\n4. Prefer your operating system's official app store when available\n5. Check the digital signature of installers before running them\n6. If your browser warns about a download, treat it as malicious\n\nBROWSER SECURITY SETTINGS:\n• Keep your browser updated — most attacks target unpatched browsers\n• Enable pop-up blocking\n• Use DNS filtering (e.g., Cloudflare 1.1.1.2) to block known malicious domains",
             "key_points": '["Sponsored search ads can link to malware — type URLs directly", "Verify the publisher digital signature before running any installer", "Keep your browser updated to patch known vulnerabilities", "Prefer official app stores over third-party download sites"]'},
            {"order": 3, "title": "SSL Certificate Inspection — Reading the Padlock",
             "content": "The padlock icon in your browser's address bar signals an HTTPS (encrypted) connection, but it does NOT guarantee the site is legitimate. Attackers routinely obtain free SSL certificates for phishing domains. To properly evaluate a site, you must inspect the certificate itself, not just notice the padlock.\n\nHOW TO INSPECT A CERTIFICATE:\n1. Click the padlock icon (or the area to the left of the URL)\n2. Select 'Connection is secure' → 'Certificate is valid'\n3. Check the following fields:\n\nISSUED TO (Common Name / Subject):\nThis must exactly match the domain you are visiting. A certificate for paypal.com visited on paypa1.com is an instant red flag.\n\nISSUED BY (Certificate Authority):\nTrusted CAs include DigiCert, Comodo, GlobalSign, Sectigo, and Let's Encrypt. An unknown CA is suspicious.\n\nVALIDITY PERIOD:\nCheck the 'Not Before' and 'Not After' dates. An expired certificate is a warning sign — legitimate organisations maintain valid certs.\n\nCERTIFICATE TYPE:\nDV (Domain Validated) — only proves the applicant controls the domain; free and available to anyone, including attackers\nOV (Organisation Validated) — verifies the legal existence of the organisation; shown in the cert details\nEV (Extended Validation) — highest bar; previously showed a green company name in the bar (now shown in cert details only)\n\nFor financial or healthcare transactions, prefer sites with OV or EV certificates.\n\nHOMOGRAPH ATTACKS:\nCyrillic, Greek, and other Unicode characters are visually identical to Latin letters but technically different. 'аpple.com' using a Cyrillic 'а' (U+0430) is a different domain from 'apple.com' (U+0061). Certificate inspection and the URL punycode (xn-- prefix) expose this — the browser may display xn--pple-43d.com rather than the fake apple.com.",
             "key_points": '["HTTPS means encrypted, not safe — inspect the certificate itself", "Check that the certificate is Issued To the exact domain you are visiting", "DV certificates are free — criminals obtain them for phishing sites", "Homograph attacks use visually identical Unicode characters — check the padlock cert details"]'},
        ],
        "scenarios": [
            {
                "title": "Suspicious Download Website",
                "scenario_type": "website",
                "description": "You're searching for a free PDF converter and find this website.",
                "content_html": """<div class="fake-website">
  <div class="browser-bar">
    <span class="protocol http">⚠ Not Secure</span>
    <span class="url">http://free-pdf-convert0r.net/download</span>
  </div>
  <div class="site-content">
    <h2>🎉 FREE PDF Converter — #1 Trusted Tool 2024!</h2>
    <p>✅ 100% Free | ✅ No Registration | ✅ Instant Download</p>
    <div class="warning-box" style="background:#fff3cd; border:1px solid #ffc107; padding:10px; margin:10px 0;">
      ⚠️ <strong>Your PDF plugin is outdated!</strong> Update now for best performance.
    </div>
    <button class="fake-btn" style="font-size:1.2em; padding:15px 30px;">⬇ Download Now (Free!)</button>
    <p><small>Downloaded by 2,847,293 users | 5-star rated</small></p>
  </div>
</div>""",
                "question": "Is it safe to download from this website?",
                "correct_action": "ignore",
                "explanation": "Multiple red flags: (1) HTTP not HTTPS — no encryption. (2) Suspicious domain with number substitution '0r'. (3) 'Outdated plugin' warning is a classic malware distribution tactic. (4) Generic inflated download counts. Use only official sources like Adobe Acrobat or LibreOffice.",
                "difficulty": "beginner",
                "time_limit": 60,
                "xp_reward": 25,
                "options": [
                    {"text": "Download — it has 5 stars and millions of users", "is_correct": False, "feedback": "Fake statistics are cheap to display. The HTTP URL and suspicious domain are clear warning signs."},
                    {"text": "Update the PDF plugin first, then download", "is_correct": False, "feedback": "The 'plugin update' is the malware delivery mechanism — a classic drive-by download tactic."},
                    {"text": "Leave the site and find an official PDF tool instead", "is_correct": True, "feedback": "Correct! Use Adobe Acrobat, LibreOffice, or another known reputable source for PDF tools."},
                    {"text": "Download but scan with antivirus first", "is_correct": False, "feedback": "Better than downloading blindly, but the safest choice is not to download from suspicious sites at all."},
                ],
            },
            {
                "title": "Typosquatting — Fake Banking Site",
                "scenario_type": "website",
                "description": "You search for your bank and click the top result. This is the website you land on.",
                "content_html": """<div class="fake-website">
  <div class="browser-bar">
    <span class="protocol https">🔒 Secure</span>
    <span class="url">https://www.lloydsbannk.co.uk/personal/login</span>
  </div>
  <div class="site-content" style="max-width:400px; margin:0 auto; padding:20px; border:1px solid #e0e0e0; border-radius:8px;">
    <div style="text-align:center; margin-bottom:20px;">
      <div style="font-size:2em; font-weight:bold; color:#006a4d;">Lloyds Bank</div>
      <div style="color:#555; font-size:0.85em;">Personal Banking</div>
    </div>
    <div style="margin-bottom:12px;">
      <label style="font-size:0.85em; color:#333;">User ID</label>
      <input type="text" placeholder="Enter your User ID" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; box-sizing:border-box;">
    </div>
    <div style="margin-bottom:16px;">
      <label style="font-size:0.85em; color:#333;">Memorable Information</label>
      <input type="password" placeholder="Enter your memorable information" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; box-sizing:border-box;">
    </div>
    <button class="fake-btn" style="width:100%;">Log In →</button>
  </div>
</div>""",
                "question": "You notice the URL is 'lloydsbannk.co.uk' not 'lloydsbank.co.uk'. What should you do?",
                "correct_action": "ignore",
                "explanation": "This is a typosquatting attack. The URL contains a double 'n' — 'lloydsbannk.co.uk' instead of 'lloydsbank.co.uk'. The HTTPS padlock only confirms the connection is encrypted — it does NOT verify the site is legitimate. Attackers obtain valid SSL certificates for fake domains. Close this tab immediately, type the correct URL directly, and report the fake site.",
                "difficulty": "intermediate",
                "time_limit": 75,
                "xp_reward": 30,
                "options": [
                    {"text": "It is safe — it has a padlock and looks identical to the real site", "is_correct": False, "feedback": "HTTPS and visual design can be copied exactly. The URL is the only reliable identifier — and this one is wrong."},
                    {"text": "Log in but change your password immediately afterwards", "is_correct": False, "feedback": "Logging in sends your credentials directly to the attacker. Even changing your password afterwards does not undo this."},
                    {"text": "Close the tab, type 'lloydsbank.co.uk' directly into the address bar, and report the fake site", "is_correct": True, "feedback": "Correct! Always type bank URLs directly. Report the typosquat to the real bank and to the National Cyber Security Centre (NCSC)."},
                    {"text": "Use the search result again — it must be the real site if it appeared in Google", "is_correct": False, "feedback": "Attackers use SEO and paid ads to place typosquat sites near the top of search results. Never trust search ranking as proof of legitimacy."},
                ],
            },
            {
                "title": "Suspicious Browser Extension Request",
                "scenario_type": "website",
                "description": "While browsing, a pop-up asks you to install a browser extension.",
                "content_html": """<div class="fake-website">
  <div class="browser-bar">
    <span class="protocol http">⚠ Not Secure</span>
    <span class="url">http://stream-content-unlocker.net/install</span>
  </div>
  <div class="site-content" style="text-align:center; padding: 20px;">
    <div style="font-size:2.5em; margin-bottom:10px;">🔓</div>
    <h3 style="margin-bottom:8px;">StreamUnlock Pro — Free</h3>
    <p style="color:#555; font-size:0.88em; margin-bottom:16px;">Access geo-blocked streaming content from anywhere!</p>
    <div style="background:#fff3cd; border:1px solid #ffc107; padding:10px; border-radius:6px; margin-bottom:16px; font-size:0.83em; text-align:left;">
      <strong>This extension will be able to:</strong><br>
      • Read and change all your data on all websites<br>
      • Read and change your browsing history<br>
      • Manage your downloads<br>
      • Communicate with cooperating native applications
    </div>
    <button class="fake-btn">Add to Chrome — Free!</button>
  </div>
</div>""",
                "question": "The extension requests permission to 'read and change all your data on all websites'. What should you do?",
                "correct_action": "ignore",
                "explanation": "This extension requests excessive permissions — the ability to read and modify all your data on every website, including banking, email, and work systems. Malicious extensions use these permissions to steal credentials, inject ads, or redirect traffic. Legitimate streaming tools do not require such broad access. Never install extensions from unknown sites; only use the official Chrome Web Store and verify developer reputation.",
                "difficulty": "advanced",
                "time_limit": 90,
                "xp_reward": 40,
                "options": [
                    {"text": "Install it — the permissions are standard for extensions", "is_correct": False, "feedback": "Permission to read ALL data on ALL websites is extremely dangerous. A malicious extension with this access can steal every password and session token you use."},
                    {"text": "Install it but use it only on streaming sites, not work sites", "is_correct": False, "feedback": "Once installed, the extension runs on all sites regardless of your intention. You cannot limit where it activates without removing it."},
                    {"text": "Close the page without installing; only install extensions from trusted sources with minimal permissions", "is_correct": True, "feedback": "Correct! Request excessive permissions is a major red flag. Use only extensions from reputable developers with specific, minimal permissions, via the official browser store."},
                    {"text": "Install it after running a virus scan on the extension file", "is_correct": False, "feedback": "Antivirus cannot evaluate what a browser extension will do at runtime. Permissions describe its capability — and these permissions are intrinsically dangerous."},
                ],
            },
        ],
    },
    {
        "order": 5, "domain": "pretexting", "title": "Pretexting Detection",
        "description": "Identify fabricated scenarios used to extract sensitive information.",
        "icon": "fa-mask", "color": "#ec4899", "xp_reward": 50, "badge_name": "Human Firewall",
        "lessons": [
            {"order": 1, "title": "What is Pretexting?",
             "content": "Pretexting is a form of social engineering where attackers create a fabricated scenario (pretext) to manipulate a target into revealing information or performing an action.\n\nCommon pretexts:\n• VENDOR IMPERSONATION — 'I'm from Microsoft Support, your PC is sending error reports'\n• SURVEY FRAUD — 'We're conducting a security audit and need your login details'\n• NEW EMPLOYEE — 'I just joined the IT team and need system access urgently'\n• CONTRACTOR — 'I'm here to service the network equipment, can you let me in?'\n• BANK FRAUD TEAM — 'We've detected fraud — I need to verify your account number'\n\nPretexting exploits:\n• Authority (impersonating officials)\n• Helpfulness (people want to assist)\n• Trust (building rapport first)\n• Fear (threat of consequences)",
             "key_points": '["Verify identity through official channels independently", "No legitimate service requires your password", "Physical access requests require badge verification", "When in doubt, say no and escalate"]'},
            {"order": 2, "title": "Recognising Pretexts in the Workplace",
             "content": "Pretexting scenarios are designed to feel completely normal. Attackers research their targets before calling — they may know your manager's name, your current project, or your company's IT systems.\n\nHOW TO DETECT A PRETEXT:\n\n1. UNSOLICITED CONTACT — Did you initiate this interaction? Unexpected calls or visits requesting access or information are high-risk.\n\n2. UNUSUAL REQUESTS — Does the request fall outside normal procedures? Any request to bypass standard verification is a major red flag.\n\n3. URGENCY + SECRECY — Legitimate business requests rarely require secrecy from colleagues or managers.\n\n4. INFORMATION THEY SHOULD ALREADY HAVE — A real IT administrator does not need your password. A real bank does not need your full account number.\n\n5. RESISTANCE TO VERIFICATION — Legitimate parties welcome identity verification. If they resist or create obstacles to verification, that is suspicious.\n\nTHE VERIFICATION PROTOCOL:\n1. Politely pause the interaction ('I need to verify your identity before proceeding')\n2. Find the contact information INDEPENDENTLY (from your company intranet or official website)\n3. Call the verified number and confirm the request\n4. Only proceed if confirmed — document and report if unverified",
             "key_points": '["Legitimate parties always welcome proper verification", "Urgency combined with secrecy is a strong red flag", "Research by attackers makes pretexts feel credible — verify anyway", "Document every suspicious interaction and report it"]'},
            {"order": 3, "title": "Callback Verification — The Definitive Procedure",
             "content": "Callback verification is the single most effective countermeasure against pretexting. It works by breaking the attacker's control of the communication channel and re-establishing contact through a number YOU independently source.\n\nTHE FULL CALLBACK PROCEDURE:\n\nPHASE 1 — RECEIVE AND RECORD\n• Note the caller's claimed name, organisation, and the nature of the request\n• Do not commit to any action during the initial contact\n• Decline to provide any information until verification is complete\n• If in person: ask for an ID or access card and ask the individual to wait in a public/reception area\n\nPHASE 2 — FIND THE REAL NUMBER (critical step)\nSource the contact number INDEPENDENTLY from one of these:\n✓ Your company's official intranet directory\n✓ The organisation's publicly listed website (not a link from the caller)\n✓ A number you have used and verified previously\n✓ A physical phonebook or directory enquiry service\n\nNEVER use:\n✗ A number provided by the caller themselves\n✗ A number from an email or message the caller sent\n✗ A number from a business card handed to you on the spot\n\nPHASE 3 — CALL BACK AND VERIFY\n• Call the number you sourced independently\n• Ask to confirm whether [person/ticket/request] exists and is legitimate\n• If confirmed: proceed. If not confirmed: report immediately as a suspected social engineering attempt\n\nPHASE 4 — DOCUMENT\n• Record the time, caller details, what was requested, and the outcome of your verification\n• Report even confirmed interactions if they seemed unusual\n\nCALLBACK VERIFICATION DEFEATS:\n• Vendor impersonation (they cannot control what the real vendor says when you call back)\n• New employee pretexts (HR can confirm whether a person exists and has access)\n• IT support scams (your real IT desk will know nothing about the call)\n• Physical access pretexts (facilities management can confirm contractor bookings)",
             "key_points": '["Source the callback number independently — never use a number the requester provides", "Callback verification works against all pretexting categories", "Document every verification interaction, confirmed or not", "A requester who refuses to wait for callback has revealed themselves"]'},
        ],
        "scenarios": [
            {
                "title": "Microsoft Support Caller",
                "scenario_type": "phone",
                "description": "You get this message via your work chat system.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">💬 Teams Message — James Wilson (Microsoft Support)</div>
  <div class="chat-body">
    <div class="chat-msg received">
      <strong>James Wilson:</strong> Hello! I'm James from Microsoft Enterprise Support. Our monitoring system has flagged critical errors on your organisation's tenant. I need to schedule an urgent remote session to prevent data loss. Could you please share your Microsoft 365 admin credentials so I can begin the remediation? This needs to happen in the next 30 minutes per your SLA.
    </div>
    <div class="chat-msg received">
      <strong>James Wilson:</strong> I've sent a verification code to your email. Please share it with me to authenticate the session.
    </div>
  </div>
</div>""",
                "question": "What is the correct response to this message?",
                "correct_action": "report",
                "explanation": "This is a pretexting attack. Microsoft never proactively contacts customers to request credentials via Teams chat. Sharing admin credentials or MFA codes gives attackers full control of your organisation's systems. Report this to IT security immediately.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Share credentials since it's coming through official Teams", "is_correct": False, "feedback": "Teams accounts can be compromised. Microsoft never requests credentials through chat."},
                    {"text": "Share the verification code only, not the full password", "is_correct": False, "feedback": "The verification code IS the MFA token — sharing it gives attackers full access to your account."},
                    {"text": "Ignore the message and report it to IT security", "is_correct": True, "feedback": "Correct! Report immediately. Legitimate Microsoft support is raised through your IT team, not direct unsolicited contact."},
                    {"text": "Ask for their employee ID before sharing anything", "is_correct": False, "feedback": "Employee IDs can be fabricated. Verification must happen through an independent channel — call Microsoft's official support line."},
                ],
            },
            {
                "title": "Software Vendor Impersonation Email",
                "scenario_type": "email",
                "description": "You receive this email claiming to be from your company's HR software supplier.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value suspicious">support@bamboohr-helpdesk.net</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">hr-admin@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">BambooHR — Scheduled Maintenance: Admin credentials needed</span></div>
  </div>
  <div class="email-body">
    <p>Dear BambooHR Administrator,</p>
    <p>We are conducting a planned database migration this weekend (Sat 2–4 AM). To ensure your data migrates correctly, our engineers require temporary access to your admin account.</p>
    <p>Please reply to this email with:</p>
    <ul>
      <li>Your BambooHR admin username</li>
      <li>Your current admin password</li>
      <li>Your account subdomain (e.g. acme.bamboohr.com)</li>
    </ul>
    <p>This information will be used solely for the migration and deleted immediately after. Our SLA guarantees confidentiality.</p>
    <p>Please respond by <strong>Friday 5pm</strong> to be included in the migration window.</p>
    <p>Kind regards,<br>BambooHR Technical Operations Team</p>
  </div>
</div>""",
                "question": "What should you do with this request from your HR software supplier?",
                "correct_action": "verify",
                "explanation": "This is vendor impersonation pretexting. The sender domain 'bamboohr-helpdesk.net' is not BambooHR's official domain (bamboohr.com). No legitimate SaaS vendor ever requires your admin password for a migration — they perform backend operations themselves. If you receive this from a known vendor domain, still verify by calling the vendor's official support line. Sharing credentials gives attackers full access to all employee personal data.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Reply with the credentials — the migration deadline is Friday", "is_correct": False, "feedback": "Legitimate SaaS providers never ask for your password. They perform backend migrations without needing your credentials."},
                    {"text": "Create a temporary admin account with a new password for the migration", "is_correct": False, "feedback": "Creating any account for an unverified party still gives them access to all sensitive HR data. Verify the request first through official channels."},
                    {"text": "Contact BambooHR through their official website to verify the migration", "is_correct": True, "feedback": "Correct! Find BambooHR's support contact at bamboohr.com and call to confirm. The sender domain is not bamboohr.com — this is almost certainly fraudulent."},
                    {"text": "Forward to IT and reply saying credentials will follow once IT approves", "is_correct": False, "feedback": "Correct to involve IT, but do not promise credentials or imply they may be provided. Treat this as a suspected phishing/pretexting attack from the outset."},
                ],
            },
            {
                "title": "New Colleague Requests System Access",
                "scenario_type": "chat",
                "description": "You receive this message on Microsoft Teams from someone claiming to be a new starter.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">💬 Teams Message — Alex Turner (New Starter)</div>
  <div class="chat-body">
    <div class="chat-msg received">
      <strong>Alex Turner:</strong> Hi! I started this week in the Compliance team (line manager is Sarah). Still waiting for IT to set up my full access. I need to pull the Q3 audit files from the shared drive to brief Sarah by 4pm. Could you share your login so I can access the folders? I'll only be 10 mins and will log straight off.
    </div>
    <div class="chat-msg received">
      <strong>Alex Turner:</strong> Sarah's in a meeting and I don't want to bother her. You'd really be saving me here!
    </div>
  </div>
</div>""",
                "question": "What is the most appropriate response to Alex's request?",
                "correct_action": "verify",
                "explanation": "This is a new-employee pretext attack using helpfulness, time pressure, and a plausible authority figure (Sarah). Account sharing violates security policy and removes individual accountability — any malicious action would appear to come from you. Verify the new starter's identity with HR or the named manager before taking any action, and direct them to IT for proper access provisioning.",
                "difficulty": "advanced",
                "time_limit": 90,
                "xp_reward": 40,
                "options": [
                    {"text": "Share your login credentials temporarily — it is just for 10 minutes", "is_correct": False, "feedback": "Account sharing violates acceptable use policy and removes audit trails. Any data access, modification, or theft would appear to come from your account."},
                    {"text": "Ask Alex to send you the files they need and forward them", "is_correct": False, "feedback": "You should not act on an unverified identity. The person may not be who they claim, and the request itself may be part of a pretext to access sensitive data."},
                    {"text": "Verify Alex's identity with HR or Sarah directly, then advise them to contact IT for proper access", "is_correct": True, "feedback": "Correct! Verify first, then direct them to IT. Legitimate new starters have IT provisioning paths — sharing credentials is never the right answer regardless of urgency."},
                    {"text": "Tell Alex you are too busy and suggest they wait for IT", "is_correct": False, "feedback": "While not sharing credentials is correct, you should still verify the identity and report the request to your security team if unconfirmed."},
                ],
            },
        ],
    },
    {
        "order": 6, "domain": "data_handling", "title": "Data Handling & Classification",
        "description": "Handle, classify, and dispose of sensitive data securely.",
        "icon": "fa-database", "color": "#10b981", "xp_reward": 50, "badge_name": "Data Steward",
        "lessons": [
            {"order": 1, "title": "Data Classification Fundamentals",
             "content": "Data classification assigns a sensitivity level to information, determining how it must be protected, handled, and disposed of.\n\nTYPICAL CLASSIFICATION LEVELS:\n\n🔴 CONFIDENTIAL / TOP SECRET\nExamples: Personal data (GDPR), financial records, trade secrets, medical records\nHandling: Encrypted storage and transmission, need-to-know access only, secure deletion\n\n🟡 INTERNAL / RESTRICTED\nExamples: Internal reports, project plans, employee data\nHandling: Access controls, not for external sharing, secure email\n\n🟢 PUBLIC\nExamples: Marketing materials, published annual reports\nHandling: No special controls, but verify before publishing\n\nGDPR OBLIGATIONS:\n• Personal data = any information relating to an identified/identifiable person\n• Must be processed lawfully, fairly, and transparently\n• Right to erasure (right to be forgotten)\n• Breach notification within 72 hours",
             "key_points": '["Classify data before storing or transmitting", "Personal data under GDPR requires special protection", "Secure deletion means overwriting, not just emptying the bin", "Only share data on a need-to-know basis"]'},
            {"order": 2, "title": "Aggregation Risk — When Harmless Data Becomes Dangerous",
             "content": "Aggregation risk is the principle that combining multiple individually innocuous pieces of information creates a combined profile that is significantly more sensitive than any single piece alone. This is one of the most important and least-understood concepts in data handling, and it is directly exploited in targeted social engineering attacks.\n\nTHE AGGREGATION PRINCIPLE IN PRACTICE:\n\nConsider what an attacker can learn from openly available sources:\n• LinkedIn: Full name, job title, employer, team, start date, skills, connections\n• Instagram: Location tags, daily routine, home neighbourhood, social circle\n• Company website: Organisational structure, office addresses, email format\n• Facebook: Birthday, family members, school attended, life events\n• Twitter/X: Opinions, frustrations, events attended, check-ins\n\nNone of these items alone is particularly sensitive. Combined, they enable:\n✓ Convincing spear phishing (attacker knows your name, team, manager, start date)\n✓ Physical social engineering ('Hi Jamie, I'm here for the 2pm IT meeting with Sarah')\n✓ Account recovery bypasses ('What is your mother's maiden name?')\n✓ Financial fraud (birthday + address + employer = credit application)\n\nGDPR ARTICLE 4 AND AGGREGATION:\nGDPR defines personal data as 'any information relating to an identified or identifiable natural person.' Aggregation is relevant here because data that appears anonymous in isolation may become identifiable when combined with other available data — a principle known as the mosaic effect. A dataset containing only postcodes and birthdays may seem innocuous; cross-referenced with a voter register it can identify individuals.\n\nORGANISATIONAL CONTROLS:\n• Apply the data minimisation principle — only collect what you actually need\n• Restrict access on a need-to-know basis — not everyone needs every field\n• Be careful what you publish on organisational websites and LinkedIn company pages\n• Treat any combination of name + role + contact detail + location as personal data\n• Conduct Data Protection Impact Assessments (DPIAs) before aggregating datasets",
             "key_points": '["Individually harmless data items become sensitive when combined — the mosaic effect", "Social engineering attacks routinely exploit aggregated open-source intelligence", "GDPR data minimisation reduces aggregation risk at source", "Before sharing any dataset, consider what it reveals when combined with other available data"]'},
            {"order": 3, "title": "GDPR Compliance & Secure Data Disposal",
             "content": "The General Data Protection Regulation (GDPR) mandates how personal data must be handled throughout its lifecycle, including at the point of disposal.\n\nSECURE DISPOSAL METHODS:\n\nDIGITAL DATA:\n• Use certified data erasure software (DoD 5220.22-M standard or equivalent)\n• Simply deleting a file or emptying the Recycle Bin does NOT remove data — it only removes the index entry\n• For end-of-life hardware: physical destruction (degaussing, shredding) or certified ITAD (IT Asset Disposal)\n• Cloud storage: use the provider's verified deletion process; retain audit logs\n\nPHYSICAL DOCUMENTS:\n• Cross-cut shredding (not strip shredding — strips can be reassembled)\n• Confidential waste sacks collected by licensed contractors\n• Never leave confidential documents in standard recycling bins\n\nDATA MINIMISATION:\n• Only collect personal data you actually need\n• Do not retain personal data longer than necessary\n• Define and enforce retention periods for all data types\n\nBREACH RESPONSE:\n• Report to the ICO (UK) or relevant supervisory authority within 72 hours\n• Notify affected individuals if the breach poses high risk to them\n• Maintain a breach register even for minor incidents",
             "key_points": '["Deleting a file does not remove the data — use certified erasure", "Cross-cut shred paper documents containing personal data", "GDPR breach notification to the ICO must happen within 72 hours", "Retain data only for as long as necessary — enforce retention policies"]'},
        ],
        "scenarios": [
            {
                "title": "USB Drive Found in Car Park",
                "scenario_type": "usb",
                "description": "You find a USB drive in your company car park labelled 'Salary Data Q4 2024'.",
                "content_html": """<div class="fake-usb">
  <div class="usb-visual">💾</div>
  <div class="usb-label">
    <strong>USB DRIVE FOUND IN CAR PARK</strong>
    <p>Label reads: <em>"Salary Data Q4 2024 — CONFIDENTIAL"</em></p>
    <p>The drive appears to be a standard USB flash drive. Your curiosity is piqued — what are you paid compared to colleagues?</p>
  </div>
</div>""",
                "question": "What do you do with the USB drive?",
                "correct_action": "report",
                "explanation": "USB baiting is a well-documented attack technique. Attackers deliberately leave malware-loaded USB drives in locations where employees will find them. Plugging in an unknown USB can install malware, ransomware, or create a backdoor — even on an air-gapped system. Hand it to IT security unopened.",
                "difficulty": "beginner",
                "time_limit": 60,
                "xp_reward": 25,
                "options": [
                    {"text": "Plug it in to see if it belongs to a colleague", "is_correct": False, "feedback": "This is a USB baiting attack. Plugging in unknown USBs can install malware instantly, even before you open any files."},
                    {"text": "Plug it in to a personal laptop, not a work computer", "is_correct": False, "feedback": "Still dangerous — malware can spread from personal to work devices and compromise your home network."},
                    {"text": "Leave it where you found it", "is_correct": False, "feedback": "Another person may plug it in and become compromised. Hand it to IT security."},
                    {"text": "Hand it to IT security without plugging it in", "is_correct": True, "feedback": "Correct! IT security can analyse the drive safely in an isolated environment. This is the only safe response."},
                ],
            },
            {
                "title": "Accidental Email to Wrong Recipient",
                "scenario_type": "email",
                "description": "You just sent a customer data export and realise the autocomplete added the wrong address.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value">you@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value suspicious">david.jones@externalprovider.com</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Customer Data Export — Q3 2024</span></div>
    <div class="email-field"><span class="label">Attachment:</span> <span class="value">customer_data_Q3_2024.xlsx (4,847 rows)</span></div>
  </div>
  <div class="email-body" style="background:#fff8f8; border-left: 4px solid #d93025; padding: 14px; border-radius: 4px;">
    <p><strong>⚠ You have just sent this email.</strong></p>
    <p>You intended to send to <strong>david.jones@acmecorp.co.uk</strong> (your colleague) but email autocomplete selected <strong>david.jones@externalprovider.com</strong> — an external contact with the same name.</p>
    <p>The file contains names, email addresses, and purchase history for 4,847 customers.</p>
  </div>
</div>""",
                "question": "You have accidentally sent customer personal data to an external party. What is your immediate response?",
                "correct_action": "report",
                "explanation": "This is a personal data breach under GDPR. Accidental disclosure to an unauthorised recipient must be reported to your Data Protection Officer (DPO) or Privacy team immediately. You should also request the recipient delete the file. The organisation must assess whether to notify the ICO within 72 hours and whether affected customers need to be informed. Do not attempt to handle this alone — escalate immediately.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Email the external recipient and ask them to delete it — problem solved", "is_correct": False, "feedback": "While requesting deletion is one step, you cannot verify they comply. This is a notifiable data breach that must be reported to your DPO regardless of any recipient assurances."},
                    {"text": "Say nothing and hope the recipient does not notice", "is_correct": False, "feedback": "Concealing a data breach is a serious GDPR violation. Fines for failing to report a known breach can be far higher than for the breach itself."},
                    {"text": "Report it immediately to your DPO/Privacy team and document exactly what happened", "is_correct": True, "feedback": "Correct! The DPO/Privacy team will assess reportability to the ICO, manage customer notifications if required, and coordinate with the external recipient. Speed is essential — 72 hours starts now."},
                    {"text": "Ask a colleague for advice before deciding whether to report", "is_correct": False, "feedback": "Seeking informal advice delays a formal breach report. Go directly to your DPO or Privacy team — they are the right people to assess and manage this."},
                ],
            },
            {
                "title": "Sensitive Data Visible in Screen Share",
                "scenario_type": "chat",
                "description": "You are presenting in a video call with 12 external partners when you notice this.",
                "content_html": """<div class="fake-chat">
  <div class="chat-header">📹 Video Call — Strategy Review (12 Participants including External Partners)</div>
  <div class="chat-body">
    <div class="chat-msg received" style="background:#fff3e0; border-left: 3px solid #f59e0b; padding: 14px; border-radius: 8px; margin-bottom: 12px;">
      <strong>Situation:</strong> You are screen-sharing your desktop to present a strategy slide deck. A notification pops up at the bottom of your screen:<br><br>
      <em>"HR: Redundancy shortlist attached — strictly confidential.xlsx"</em><br><br>
      The notification is visible to all 12 participants for approximately 5 seconds before disappearing. The file is not open, but the title was visible.
    </div>
    <div class="chat-msg received" style="background:#fce4ec; border-left: 3px solid #ef4444; padding: 14px; border-radius: 8px;">
      <strong>You notice:</strong> One external partner has already typed <em>"Was that a redundancy list?"</em> in the chat.
    </div>
  </div>
</div>""",
                "question": "What should you do first in this situation?",
                "correct_action": "report",
                "explanation": "Accidental disclosure of confidential HR data (even just a document title) during a client call is a data incident. Immediately pause sharing, acknowledge the notification briefly without elaborating, and end the call at the earliest natural point. Report the incident to your DPO and HR team so they can assess the impact and decide on follow-up communication. Do not discuss the content of the document with external parties.",
                "difficulty": "intermediate",
                "time_limit": 75,
                "xp_reward": 30,
                "options": [
                    {"text": "Continue the presentation — only a title was visible, not the actual data", "is_correct": False, "feedback": "Even a document title revealing a redundancy shortlist can constitute a data breach if it discloses information about identifiable individuals' employment status. Report it."},
                    {"text": "Immediately stop screen sharing and report the incident to HR and your DPO", "is_correct": True, "feedback": "Correct! Stop the exposure, acknowledge minimally if asked, and report through proper channels. Your DPO will determine if regulatory notification is needed."},
                    {"text": "Tell the partner it was nothing and that they misread the notification", "is_correct": False, "feedback": "Attempting to minimise or deny the incident could worsen your organisation's legal position. Report accurately — do not mislead external parties."},
                    {"text": "Email the external partner privately asking them to keep it confidential", "is_correct": False, "feedback": "You cannot legally enforce confidentiality through informal email. Report through your DPO — they have the appropriate processes and legal authority to manage this."},
                ],
            },
        ],
    },
    {
        "order": 7, "domain": "incident_reporting", "title": "Incident Reporting",
        "description": "Recognise, escalate, and document security incidents correctly.",
        "icon": "fa-bell", "color": "#3b82f6", "xp_reward": 50, "badge_name": "First Responder",
        "lessons": [
            {"order": 1, "title": "What Constitutes a Security Incident?",
             "content": "A security incident is any event that actually or potentially jeopardises the confidentiality, integrity, or availability of information or systems.\n\nEXAMPLES OF REPORTABLE INCIDENTS:\n• Clicking a phishing link\n• Receiving a suspicious email\n• Finding unknown devices on the network\n• Noticing unusual account activity\n• Losing a device containing company data\n• Discovering an unlocked screen in a public place\n• Someone tailgating through a secure door\n• A colleague asking for your password\n\nWHY REPORT IMMEDIATELY?\n✓ Early reporting limits damage\n✓ Security teams can isolate affected systems\n✓ GDPR requires breach notification within 72 hours\n✓ Your report may prevent attacks on colleagues\n✓ You are protected — reporting is not about blame",
             "key_points": '["Report ALL suspicious activity — you cannot over-report", "Act fast: the first 24 hours are critical", "Do not try to investigate or fix it yourself", "Document everything: time, what happened, what you clicked"]'},
            {"order": 2, "title": "The Incident Response Process",
             "content": "When you suspect or discover an incident, follow this sequence:\n\n1. STOP — Do not take further action on the affected system\n2. ISOLATE — Disconnect from the network if instructed (but do not power off)\n3. REPORT — Contact IT Security / Help Desk immediately\n   • What happened\n   • When it happened\n   • What systems/data were involved\n   • What actions you took\n4. PRESERVE EVIDENCE — Do not delete emails or files\n5. DOCUMENT — Write down everything while it is fresh\n6. COOPERATE — Follow IT Security instructions\n7. LEARN — Attend any follow-up security briefings\n\nDO NOT:\n✗ Try to remediate the issue yourself\n✗ Tell attackers you have detected them\n✗ Post about the incident on social media\n✗ Delay reporting out of embarrassment",
             "key_points": '["Speed is critical in incident response", "Preserve evidence — do not delete anything", "Embarrassment should never delay reporting", "Follow the official incident response procedure"]'},
        ],
        "scenarios": [
            {
                "title": "Ransomware Warning",
                "scenario_type": "email",
                "description": "You arrive at work and see this on your screen.",
                "content_html": """<div class="fake-ransomware">
  <div style="background:#1a1a1a; color:#ff4444; padding:20px; border:3px solid #ff4444; font-family:monospace; text-align:center;">
    <h2>⚠️ YOUR FILES HAVE BEEN ENCRYPTED ⚠️</h2>
    <p>All your documents, photos and databases have been encrypted with military-grade AES-256 encryption.</p>
    <p>To recover your files, send <strong>0.5 Bitcoin</strong> to the wallet below within 72 hours:</p>
    <div style="background:#333; padding:10px; margin:10px; word-break:break-all;">1A2b3C4d5E6f7G8h9I0jKlMnOpQrStUvWx</div>
    <p style="color:#ffff00;">⏱ Time remaining: 71:58:42</p>
    <p><small>Do NOT contact police or your files will be permanently deleted.</small></p>
  </div>
</div>""",
                "question": "What is your FIRST action when you see this screen?",
                "correct_action": "report",
                "explanation": "You've discovered a ransomware attack. Do NOT pay the ransom (no guarantee of recovery, funds criminal activity). Do NOT shut down (may destroy recovery evidence). IMMEDIATELY disconnect from the network and call IT Security. Speed is critical — other systems may still be unaffected.",
                "difficulty": "intermediate",
                "time_limit": 90,
                "xp_reward": 30,
                "options": [
                    {"text": "Pay the ransom to recover your files quickly", "is_correct": False, "feedback": "Never pay! There is no guarantee files will be recovered, and payment funds further attacks. Organisations that pay are often re-targeted."},
                    {"text": "Shut down the computer immediately", "is_correct": False, "feedback": "Shutting down may destroy forensic evidence and interrupt recovery processes. Disconnect network cable instead, then call IT."},
                    {"text": "Disconnect from the network and immediately call IT Security", "is_correct": True, "feedback": "Correct! Isolating the machine prevents spread while preserving evidence. Speed is critical to limit the blast radius."},
                    {"text": "Try to find and delete the ransomware yourself", "is_correct": False, "feedback": "You could destroy evidence and spread the infection further. Leave remediation to the security team."},
                ],
            },
            {
                "title": "Suspicious Login Alert in Your Inbox",
                "scenario_type": "email",
                "description": "You arrive at your desk on Monday morning and find this email waiting.",
                "content_html": """<div class="fake-email">
  <div class="email-header">
    <div class="email-field"><span class="label">From:</span> <span class="value">no-reply@accounts.google.com</span></div>
    <div class="email-field"><span class="label">To:</span> <span class="value">j.smith@acmecorp.co.uk</span></div>
    <div class="email-field"><span class="label">Subject:</span> <span class="value">Security alert: New sign-in to your account</span></div>
  </div>
  <div class="email-body">
    <div style="padding:10px; border-left:4px solid #1a73e8; background:#e8f0fe; margin-bottom:12px;">
      <strong>🔔 New sign-in to j.smith@acmecorp.co.uk</strong>
    </div>
    <table style="width:100%; border-collapse:collapse; font-size:0.85em;">
      <tr><td style="padding:5px; color:#555;">When:</td><td><strong>Saturday, 23 Nov 2024 at 3:07 AM</strong></td></tr>
      <tr><td style="padding:5px; color:#555;">Device:</td><td><strong>Windows PC</strong></td></tr>
      <tr><td style="padding:5px; color:#555;">Location:</td><td><strong>Lagos, Nigeria</strong></td></tr>
      <tr><td style="padding:5px; color:#555;">Browser:</td><td><strong>Chrome 118</strong></td></tr>
    </table>
    <p>If this was you, you can ignore this message.</p>
    <p>If you did not sign in at this time and location, your account may be compromised.</p>
    <p>This email was sent from accounts.google.com — do not click any links. Visit myaccount.google.com directly.</p>
  </div>
</div>""",
                "question": "You were asleep at 3am on Saturday and do not recognise this login. What is your FIRST action?",
                "correct_action": "report",
                "explanation": "A login from an unrecognised location at 3am on a weekend is a strong indicator of account compromise. Your immediate actions should be: (1) Navigate directly to myaccount.google.com (do not click links). (2) Change your password immediately. (3) Review and revoke active sessions. (4) Report to IT security — your work email may have been accessed, exposing company data. This is potentially a notifiable data breach.",
                "difficulty": "intermediate",
                "time_limit": 75,
                "xp_reward": 30,
                "options": [
                    {"text": "Ignore it — it is probably just a VPN or travel notification", "is_correct": False, "feedback": "3am Saturday from Lagos is a strong compromise indicator. This assumption could allow an attacker continued access to your account and all data within it."},
                    {"text": "Click the 'secure your account' link in the email to investigate", "is_correct": False, "feedback": "Even when emails appear legitimate, navigate directly to the service. The email itself correctly advises this. Do not click links from login alert emails."},
                    {"text": "Change your password via the official site, revoke sessions, and report to IT security", "is_correct": True, "feedback": "Correct! Act immediately: secure the account yourself, then report to IT. If your work email was accessed, company data may be at risk — this requires a security incident response."},
                    {"text": "Wait until Monday to ask IT security whether to act", "is_correct": False, "feedback": "Every hour of delay allows the attacker continued access. Change your password immediately and report — do not wait for business hours."},
                ],
            },
            {
                "title": "Work Laptop Left on Public Transport",
                "scenario_type": "usb",
                "description": "You have just arrived at the office and realised what happened on your commute.",
                "content_html": """<div class="fake-usb">
  <div class="usb-visual">💼</div>
  <div class="usb-label">
    <strong>DEVICE LOSS SCENARIO</strong>
    <p>You left your work laptop on the train during your morning commute. The laptop contains:</p>
    <ul style="text-align:left; font-size:0.9em; margin-top:8px;">
      <li>Customer contracts and personal data</li>
      <li>Your work email (cached offline)</li>
      <li>A spreadsheet with employee salaries</li>
      <li>VPN client with saved credentials</li>
    </ul>
    <p style="margin-top: 10px;"><em>The laptop requires a Windows login password but does NOT have full-disk encryption enabled.</em></p>
  </div>
</div>""",
                "question": "What is the correct order of immediate actions for this device loss?",
                "correct_action": "report",
                "explanation": "A lost unencrypted laptop containing personal data is a serious data breach. Without full-disk encryption, the Windows password provides minimal protection — data can be accessed by booting from an external device. Immediate actions: (1) Report to IT Security immediately so they can remotely wipe the device. (2) Report to your DPO — this is a likely reportable breach under GDPR. (3) Change all credentials that were accessible on the device. (4) Contact the transport company's lost property. Speed is essential — the ICO 72-hour clock has started.",
                "difficulty": "advanced",
                "time_limit": 120,
                "xp_reward": 40,
                "options": [
                    {"text": "Go to the train's lost property office first to try to recover it", "is_correct": False, "feedback": "Recovery is worth attempting but is not the first priority. IT security must be notified immediately so a remote wipe can be triggered before the device is accessed."},
                    {"text": "Call IT Security immediately to trigger a remote wipe and report to your DPO", "is_correct": True, "feedback": "Correct! Remote wipe is time-critical — act in the first minutes. Your DPO must assess GDPR reportability since personal data was on the device without encryption."},
                    {"text": "Change your Windows password — that will lock out anyone who finds it", "is_correct": False, "feedback": "Without full-disk encryption, a Windows password can be bypassed by booting from external media. The data is exposed regardless of the login screen."},
                    {"text": "Wait to see if it turns up at lost property before reporting", "is_correct": False, "feedback": "Every minute of delay risks data exposure. The 72-hour GDPR breach notification window is already running. Report immediately and pursue recovery in parallel."},
                ],
            },
        ],
    },
]


def _seed_modules():
    for m_data in _MODULE_DATA:
        module = Module(
            order=m_data["order"],
            domain=m_data["domain"],
            title=m_data["title"],
            description=m_data["description"],
            icon=m_data["icon"],
            color=m_data["color"],
            xp_reward=m_data["xp_reward"],
            badge_name=m_data["badge_name"],
        )
        db.session.add(module)
        db.session.flush()

        for l_data in m_data.get("lessons", []):
            lesson = Lesson(
                module_id=module.id,
                order=l_data["order"],
                title=l_data["title"],
                content=l_data["content"],
                key_points=l_data.get("key_points", "[]"),
            )
            db.session.add(lesson)

        for s_data in m_data.get("scenarios", []):
            scenario = Scenario(
                module_id=module.id,
                title=s_data["title"],
                scenario_type=s_data["scenario_type"],
                description=s_data["description"],
                content_html=s_data["content_html"],
                question=s_data["question"],
                correct_action=s_data["correct_action"],
                explanation=s_data["explanation"],
                difficulty=s_data["difficulty"],
                time_limit=s_data["time_limit"],
                xp_reward=s_data["xp_reward"],
            )
            db.session.add(scenario)
            db.session.flush()

            for o_data in s_data.get("options", []):
                opt = ScenarioOption(
                    scenario_id=scenario.id,
                    text=o_data["text"],
                    is_correct=o_data["is_correct"],
                    feedback=o_data["feedback"],
                )
                db.session.add(opt)


# ── Assessment Questions ───────────────────────────────────────────────────────
_QUESTIONS = [
    # ── Phishing (3 questions) ────────────────────────────────────────────────
    {"domain": "phishing", "difficulty": "beginner", "points": 10,
     "text": "You receive an email from 'security@paypa1.com' asking you to verify your account. What should you do?",
     "explanation": "The domain 'paypa1.com' uses a number '1' instead of the letter 'l'. This typosquatting technique is classic phishing. Always inspect the full sender domain carefully.",
     "answers": [
         ("Click the link and verify your account", False),
         ("Report it as phishing — the domain is spoofed", True),
         ("Forward it to colleagues to warn them", False),
         ("Reply asking if it is genuine", False),
     ]},
    {"domain": "phishing", "difficulty": "beginner", "points": 10,
     "text": "An email claims your account will be deleted in 24 hours unless you click a link. This is most likely:",
     "explanation": "Artificial urgency is one of the most common phishing tactics. Legitimate services do not threaten immediate deletion to rush you into clicking links without thinking.",
     "answers": [
         ("A genuine security warning from the service", False),
         ("A phishing attempt using urgency as manipulation", True),
         ("A routine maintenance notification", False),
         ("A legitimate account verification email", False),
     ]},
    {"domain": "phishing", "difficulty": "intermediate", "points": 10,
     "text": "Which of the following is the safest way to verify if an email from your bank is genuine?",
     "explanation": "Always navigate directly to the official website by typing the address. Never use links or phone numbers from suspicious emails as attackers can control both.",
     "answers": [
         ("Click the link in the email and check if the page looks correct", False),
         ("Call the number provided in the email", False),
         ("Navigate to the bank's official website directly and log in from there", True),
         ("Reply to the email to confirm authenticity", False),
     ]},
    # ── Social Engineering (3 questions) ─────────────────────────────────────
    {"domain": "social_engineering", "difficulty": "beginner", "points": 10,
     "text": "A caller claims to be from IT support and asks for your password to 'fix an urgent issue'. What do you do?",
     "explanation": "Legitimate IT support never needs your password — they have system-level access. This is vishing (voice phishing). End the call and verify through official channels.",
     "answers": [
         ("Give them the password — IT support is trustworthy", False),
         ("Give a temporary password you can change later", False),
         ("Refuse, end the call, and report it to your security team", True),
         ("Ask for their employee ID then share the password", False),
     ]},
    {"domain": "social_engineering", "difficulty": "beginner", "points": 10,
     "text": "What is CEO Fraud (Business Email Compromise)?",
     "explanation": "BEC attackers impersonate executives to authorise fraudulent wire transfers. They exploit authority and urgency. Always verify financial requests through a secondary channel such as a phone call.",
     "answers": [
         ("A virus that targets CEO computers specifically", False),
         ("An attack where criminals impersonate executives to authorise fraud", True),
         ("Fraud committed by company CEOs against shareholders", False),
         ("A type of ransomware targeting corporate email", False),
     ]},
    {"domain": "social_engineering", "difficulty": "intermediate", "points": 10,
     "text": "Which Cialdini principle does an attacker exploit when claiming 'Everyone else in your department has already updated their credentials'?",
     "explanation": "Social proof exploits our tendency to follow the actions of others. Attackers fabricate peer behaviour to make targets feel they should comply.",
     "answers": [
         ("Authority", False),
         ("Urgency", False),
         ("Social Proof", True),
         ("Scarcity", False),
     ]},
    # ── Password Security (3 questions) ──────────────────────────────────────
    {"domain": "password_security", "difficulty": "beginner", "points": 10,
     "text": "Which of the following is the strongest password?",
     "explanation": "Length beats complexity. 'Purple-Elephant-Dances-7!' is a passphrase — long, memorable, and includes multiple character types. Short complex passwords are easier to crack than long passphrases.",
     "answers": [
         ("P@55w0rd!", False),
         ("Purple-Elephant-Dances-7!", True),
         ("password123", False),
         ("MyName1990", False),
     ]},
    {"domain": "password_security", "difficulty": "beginner", "points": 10,
     "text": "Why is reusing the same password across multiple accounts dangerous?",
     "explanation": "Credential stuffing attacks use leaked username/password pairs from one breach to attack other services. One breach means every reused account is compromised.",
     "answers": [
         ("It is not dangerous — reusing passwords saves memory", False),
         ("A breach on one site gives attackers access to all reused accounts", True),
         ("Reused passwords expire faster", False),
         ("It only affects accounts on the same platform", False),
     ]},
    {"domain": "password_security", "difficulty": "intermediate", "points": 10,
     "text": "Which MFA method provides the strongest protection against account takeover?",
     "explanation": "Hardware security keys (FIDO2/WebAuthn) are immune to phishing because they verify the website domain cryptographically. SMS codes are weakest due to SIM-swapping vulnerabilities.",
     "answers": [
         ("SMS one-time codes", False),
         ("Security questions", False),
         ("Hardware security key (e.g. YubiKey)", True),
         ("Email verification codes", False),
     ]},
    # ── Safe Browsing (3 questions) ───────────────────────────────────────────
    {"domain": "safe_browsing", "difficulty": "beginner", "points": 10,
     "text": "A website has a padlock icon and HTTPS. Does this mean it is safe to enter your payment details?",
     "explanation": "HTTPS means the connection is encrypted, not that the site is legitimate. Phishing sites widely use HTTPS. Always verify the domain is correct regardless of the padlock.",
     "answers": [
         ("Yes — HTTPS guarantees the site is legitimate and secure", False),
         ("No — HTTPS only means the connection is encrypted, not that the site is trustworthy", True),
         ("Yes — only official sites can obtain SSL certificates", False),
         ("No — HTTPS sites are actually more likely to be malicious", False),
     ]},
    {"domain": "safe_browsing", "difficulty": "beginner", "points": 10,
     "text": "You find a USB drive in the office car park. What should you do?",
     "explanation": "USB baiting is a documented attack technique. Attackers leave malware-loaded drives in public areas. Never plug in unknown USB devices — hand them to IT security.",
     "answers": [
         ("Plug it in to see if it belongs to a colleague", False),
         ("Use a personal device to check, not a work device", False),
         ("Hand it to IT security without plugging it in", True),
         ("Leave it where you found it", False),
     ]},
    {"domain": "safe_browsing", "difficulty": "intermediate", "points": 10,
     "text": "Which of these is the safest approach when downloading software?",
     "explanation": "Official vendor websites provide verified, unmodified software. Third-party download sites frequently bundle malware or modified versions with legitimate software.",
     "answers": [
         ("Download from the first search result", False),
         ("Download from any site if it has positive reviews", False),
         ("Download exclusively from the official vendor website", True),
         ("Download the file and run antivirus before opening", False),
     ]},
    # ── Pretexting (3 questions) ──────────────────────────────────────────────
    {"domain": "pretexting", "difficulty": "beginner", "points": 10,
     "text": "Someone calls claiming to be from Microsoft and says your computer is sending error messages. They ask for remote access. What is this?",
     "explanation": "The 'Microsoft Support' tech support scam has been one of the most reported scams globally for over a decade. Microsoft does not proactively contact users about PC issues. This is pretexting.",
     "answers": [
         ("A genuine Microsoft technical support call", False),
         ("A pretexting/vishing attack — Microsoft never calls unsolicited", True),
         ("A routine security update notification", False),
         ("A legitimate warranty support call", False),
     ]},
    {"domain": "pretexting", "difficulty": "intermediate", "points": 10,
     "text": "An attacker creates a detailed fake backstory about being a new IT contractor before asking for access credentials. Which social engineering technique is this?",
     "explanation": "Pretexting involves creating a fabricated scenario (pretext) to establish trust and manipulate the target. The attacker invests in building credibility before making the actual request.",
     "answers": [
         ("Phishing", False),
         ("Baiting", False),
         ("Pretexting", True),
         ("Tailgating", False),
     ]},
    {"domain": "pretexting", "difficulty": "intermediate", "points": 10,
     "text": "A 'bank fraud investigator' calls and says they need your card number to verify a suspicious transaction. What should you do?",
     "explanation": "Legitimate bank fraud teams never ask for your full card number. They already have it. Hang up and call the number on the back of your card to verify. This is a common pretext attack.",
     "answers": [
         ("Provide the card number — they need it to protect you", False),
         ("Provide only the last 4 digits", False),
         ("Hang up and call the bank directly using the number on the card", True),
         ("Ask them to verify your identity first, then provide the number", False),
     ]},
    # ── Data Handling (2 questions) ───────────────────────────────────────────
    {"domain": "data_handling", "difficulty": "beginner", "points": 10,
     "text": "Under GDPR, how quickly must a personal data breach be reported to the relevant supervisory authority?",
     "explanation": "Article 33 of GDPR requires organisations to report personal data breaches to the supervisory authority within 72 hours of becoming aware, where feasible and where the breach poses a risk to individuals.",
     "answers": [
         ("24 hours", False),
         ("72 hours", True),
         ("7 days", False),
         ("30 days", False),
     ]},
    {"domain": "data_handling", "difficulty": "intermediate", "points": 10,
     "text": "What is the correct way to dispose of a document containing personal data?",
     "explanation": "Personal data on physical documents must be securely destroyed so it cannot be reconstructed. Cross-cut shredding or approved secure waste disposal bags are appropriate. Simply putting it in the bin is a data breach.",
     "answers": [
         ("Put it in the office recycling bin", False),
         ("Tear it in half and throw it away", False),
         ("Cross-cut shred it or place in a confidential waste bin", True),
         ("Store it in a drawer for one year then dispose", False),
     ]},
    # ── Incident Reporting (2 questions) ─────────────────────────────────────
    {"domain": "incident_reporting", "difficulty": "beginner", "points": 10,
     "text": "You accidentally clicked a link in a suspicious email. What is your FIRST action?",
     "explanation": "Immediate reporting allows IT security to isolate the incident, change credentials, and investigate before damage spreads. Do not wait or try to fix it yourself.",
     "answers": [
         ("Wait and see if anything bad happens", False),
         ("Delete the email and hope for the best", False),
         ("Report immediately to IT Security and disconnect from the network", True),
         ("Run a quick antivirus scan yourself", False),
     ]},
    {"domain": "incident_reporting", "difficulty": "intermediate", "points": 10,
     "text": "Why should employees report security incidents even if they caused the incident through their own mistake?",
     "explanation": "A blame-free reporting culture is essential for effective security. Early reports enable faster response. GDPR also legally requires breach reporting. The cost of silence vastly exceeds any embarrassment from reporting.",
     "answers": [
         ("They should not — they will face disciplinary action", False),
         ("Early reporting limits damage; the culture should be blame-free", True),
         ("Only if they think the incident will be discovered anyway", False),
         ("Reporting is optional for minor incidents", False),
     ]},
]


def _seed_questions():
    for q_data in _QUESTIONS:
        q = Question(
            domain=q_data["domain"],
            difficulty=q_data["difficulty"],
            text=q_data["text"],
            explanation=q_data["explanation"],
            points=q_data["points"],
        )
        db.session.add(q)
        db.session.flush()
        for text, is_correct in q_data["answers"]:
            a = Answer(question_id=q.id, text=text, is_correct=is_correct)
            db.session.add(a)
