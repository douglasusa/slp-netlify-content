#!/usr/bin/env python3
"""
SLP FAQ T1-T4 Updater
Spec: 64 - FAQ UPDATES TO SLP CONTENT 64 V438PM.docx

T1 – REPLACE: first <p> after <h1>  →  faq-intro-lead  (tailored per slug)
T2 – ADD:     after 1st-2nd <p>     →  faq-practical-apps div (tailored per slug)
T3 – ADD:     near page bottom      →  faq-prevention-statement  (universal)
T4 – ADD:     absolute last element →  faq-closing-cta div       (universal)

Idempotency: article elements already carrying data-slp-updated="t1-t4"
             are skipped unless --force is passed.

Usage:
  python scripts/update_faqs.py           # skip already-updated files
  python scripts/update_faqs.py --force   # reprocess every file
"""

import sys, os, re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

FORCE   = "--force" in sys.argv
FAQ_DIR = Path(__file__).resolve().parent.parent / "static" / "faqs"
MARKER  = "t1-t4"

# ── Universal T3 (identical on every page) ────────────────────────────────────
T3_HTML = (
    '<p class="faq-prevention-statement" style="font-style: italic; '
    'margin-top: 2rem; margin-bottom: 1.5rem; color: #4b5563; '
    'border-top: 1px solid #e5e7eb; padding-top: 1rem;">'
    "<strong>What this prevents:</strong> delays, loss without defensible "
    "history, inventory gaps, and after-the-fact reconciliation.</p>"
)

# ── Universal T4 (identical on every page) ────────────────────────────────────
T4_HTML = (
    '<div class="faq-closing-cta" style="margin-top: 2.5rem; margin-bottom: '
    '3rem; padding-top: 1.5rem; border-top: 2px solid #f3f4f6;">'
    '<p style="font-size: 1rem; line-height: 1.625; color: #1f2937; '
    'margin-bottom: 1rem;">If your program is decentralized or regulated and '
    "you're experiencing avoidable disruption, SLP can help you map failure "
    'points and implement a more governable approach.</p>'
    '<a href="https://strategiclabpartners.com/contact-slp/" '
    'style="display: inline-flex; align-items: center; font-weight: 600; '
    'color: #0284c7; text-decoration: none; border-bottom: 2px solid '
    'transparent;" '
    "onmouseover=\"this.style.borderBottomColor='#0284c7'\" "
    "onmouseout=\"this.style.borderBottomColor='transparent'\">"
    "Contact SLP &rarr;</a></div>"
)

# ── Per-slug tailored content: t1 intro + practical-apps bullets ──────────────
CONTENT = {
    "benefits-of-centralized-medical-logistics": {
        "t1": "Centralizing medical logistics under a single specialized partner eliminates the fragmentation that creates cost overruns, shipment delays, and compliance exposure. Strategic Lab Partners consolidates kitting, fulfillment, and inventory management into a single governed operation supported by continuous SLP CONNECT oversight, giving program managers immediate operational stability and a defensible audit trail from day one.",
        "bullets": [
            "Consolidating multi-vendor medical supply chains into a single SLP-managed hub to eliminate handoff gaps.",
            "Applying standardized QC checks across all kit types from one facility rather than auditing multiple vendors.",
            "Using SLP CONNECT dashboards to surface real-time inventory and shipment data across all distribution points.",
            "Reducing freight costs by routing all outbound medical shipments through a single optimized carrier network.",
            "Enabling rapid program scaling without renegotiating logistics contracts with multiple fulfillment vendors.",
        ],
    },
    "benefits-of-medical-kitting-for-healthcare-agencies": {
        "t1": "Healthcare agencies operating diagnostic or treatment programs face mounting pressure to deliver consistent, compliant kits across diverse patient and site populations. Strategic Lab Partners removes the operational burden by designing, assembling, and fulfilling agency-grade medical kits with built-in quality controls and SLP CONNECT tracking — so your team can focus on program outcomes rather than logistics exceptions.",
        "bullets": [
            "Designing custom kit configurations that match each agency program's clinical and regulatory specifications.",
            "Automating kit replenishment cycles based on real-time consumption data from the SLP CONNECT portal.",
            "Applying lot-control and expiration-date rules at the assembly line to ensure zero out-of-spec kits ship.",
            "Packaging kits for patient-direct delivery with compliant labeling and chain-of-custody documentation.",
            "Providing agencies with a single audit-ready data source for inventory, fulfillment, and return reconciliation.",
        ],
    },
    "benefits-of-outsourcing-medical-fulfillment": {
        "t1": "Attempting to run medical fulfillment in-house forces healthcare organizations to maintain warehouse infrastructure, staffing, and compliance systems that rarely scale efficiently with program demand. Strategic Lab Partners absorbs that operational burden — providing regulated fulfillment, real-time SLP CONNECT visibility, and the scalable capacity to grow with your program without capital investment.",
        "bullets": [
            "Transferring kit assembly, QC, and outbound shipping to SLP to free internal staff for clinical operations.",
            "Accessing regulated cold-chain and controlled-environment storage without building or leasing warehouse space.",
            "Scaling fulfillment volume up or down within days in response to program enrollment changes.",
            "Receiving shipment-level tracking data through SLP CONNECT without building a proprietary logistics system.",
            "Passing compliance and audit obligations to SLP, whose facilities and processes are built to regulatory standards.",
        ],
    },
    "benefits-of-outsourcing-medical-kitting-and-fulfillment": {
        "t1": "Managing kitting and fulfillment in parallel inside a healthcare organization strains resources and introduces compliance risk at every handoff between assembly and shipping. Strategic Lab Partners integrates both functions under one operational roof — governed by SLP CONNECT — so kits are assembled, verified, and dispatched through a single accountable process with no internal coordination overhead.",
        "bullets": [
            "Eliminating the scheduling gap between kit assembly and fulfillment that causes delays in decentralized programs.",
            "Applying identical lot-control and expiration policies from kitting through shipping for seamless compliance.",
            "Reducing per-unit cost by running assembly and fulfillment on a shared facility and labor model.",
            "Accessing SLP CONNECT data showing kit status from build through delivery in a single integrated view.",
            "Freeing procurement and operations teams from vendor management by consolidating to a single logistics partner.",
        ],
    },
    "benefits-of-sku-consolidation-in-medical-kitting": {
        "t1": "Excessive SKU proliferation in medical kitting programs drives up holding costs, complicates QC processes, and creates reconciliation headaches that compound over time. Strategic Lab Partners applies disciplined SKU rationalization — identifying which configurations can be merged, eliminated, or standardized — to deliver the same clinical outcomes with a leaner, more manageable catalog that SLP CONNECT tracks in real time.",
        "bullets": [
            "Auditing existing kit SKUs to identify configurations with overlapping components or redundant specifications.",
            "Merging low-volume specialty SKUs into flexible base configurations that accommodate multiple program needs.",
            "Reducing warehousing footprint and carrying costs by eliminating slow-moving kit variants.",
            "Simplifying QC inspection checklists by aligning kit standards across consolidated SKU categories.",
            "Improving replenishment forecast accuracy as SLP CONNECT demand signals become cleaner with fewer SKU variants.",
        ],
    },
    "can-slp-handle-canadian-shipping": {
        "t1": "Cross-border medical fulfillment into Canada introduces regulatory, customs, and carrier complexity that generic logistics providers are not equipped to navigate reliably. Strategic Lab Partners supports Canadian shipping with compliant documentation, appropriate carrier selection, and SLP CONNECT tracking that maintains chain-of-custody visibility from the fulfillment center through Canadian final delivery.",
        "bullets": [
            "Preparing CFIA and Health Canada-compliant shipping documentation for regulated medical kit contents.",
            "Selecting carrier services with verified Canadian medical goods handling capabilities and temperature control.",
            "Managing customs brokerage requirements for diagnostic supplies and specimen collection materials.",
            "Providing SLP CONNECT shipment tracking through the border crossing and into Canadian delivery networks.",
            "Coordinating return logistics from Canadian sites back to SLP facilities for processing or disposal.",
        ],
    },
    "can-we-edit-or-cancel-orders-in-real-time": {
        "t1": "Order management in time-sensitive medical fulfillment programs demands the ability to intervene — modifying or canceling orders before they enter the pick-pack-ship cycle. Strategic Lab Partners exposes order editing and cancellation controls through SLP CONNECT, giving authorized program personnel a defined window to correct errors, update quantities, or stop shipments before they reach the carrier.",
        "bullets": [
            "Modifying order quantities or kit configurations in SLP CONNECT before the fulfillment cutoff window closes.",
            "Canceling individual orders or batch runs when program enrollment changes or site delays occur.",
            "Updating shipping addresses for participant-direct deliveries without re-entering the full order.",
            "Receiving automated alerts in SLP CONNECT when an edited order re-enters the fulfillment queue.",
            "Maintaining a complete edit and cancellation audit trail for compliance review and billing reconciliation.",
        ],
    },
    "compliance-geographies-regulations": {
        "t1": "Medical kitting and fulfillment programs that operate across multiple states or countries must satisfy a layered matrix of shipping regulations, controlled-substance rules, and import-export requirements that change by jurisdiction. Strategic Lab Partners maps compliance obligations to each program's geographic footprint and builds those rules into SLP CONNECT workflows — so the right documentation, labeling, and carrier selection apply automatically to every order.",
        "bullets": [
            "Mapping state-level shipping restrictions for diagnostic specimens and regulated medical device kits.",
            "Applying jurisdiction-specific labeling and manifesting rules to outbound shipments automatically.",
            "Managing DEA scheduling compliance for programs that include controlled-substance collection materials.",
            "Maintaining IATA dangerous goods documentation for programs shipping biological specimens by air.",
            "Providing program-level compliance reporting through SLP CONNECT for multi-jurisdiction regulatory audits.",
        ],
    },
    "custom-medical-kits-for-healthcare-agencies": {
        "t1": "Healthcare agencies rarely fit a standard kit template — clinical protocols, patient populations, site configurations, and regulatory environments all demand bespoke kit designs. Strategic Lab Partners builds custom medical kits from the ground up, engineering component selection, packaging format, and labeling to match your agency's exact program requirements, with every configuration governed through SLP CONNECT.",
        "bullets": [
            "Designing kit bill-of-materials from clinical protocol specifications provided by the agency's medical team.",
            "Sourcing regulated components from qualified suppliers and managing vendor qualification documentation.",
            "Prototyping and validating kit configurations before full production to confirm clinical and regulatory fitness.",
            "Applying agency-branded labeling and patient-facing instructions formatted to program specifications.",
            "Managing kit version control through SLP CONNECT so configuration changes are traced and auditable.",
        ],
    },
    "decentralized-at-home-collections": {
        "t1": "Decentralized at-home collection programs place the most compliance-sensitive logistics step — specimen collection — in the hands of participants who are far from clinical oversight. Strategic Lab Partners stabilizes that environment by delivering fully compliant, pre-configured collection kits directly to participants and maintaining SLP CONNECT chain-of-custody tracking from kit dispatch through lab receipt.",
        "bullets": [
            "Fulfilling participant-direct collection kits with pre-printed return labels and pre-paid return shipping.",
            "Packaging collection materials to survive ambient transit conditions while maintaining specimen integrity.",
            "Tracking each kit's outbound delivery and return scan through SLP CONNECT in real time.",
            "Coordinating collection kit replenishment for programs with rolling enrollment and variable return rates.",
            "Providing exception alerts when return shipments exceed transit time thresholds or show handling anomalies.",
        ],
    },
    "difference-between-medical-kitting-and-3pl-fulfillment": {
        "t1": "Medical kitting and third-party logistics fulfillment address fundamentally different problems in a healthcare supply chain. Kitting involves the design, assembly, and QC of custom component combinations; 3PL fulfillment handles storage, pick-pack, and shipping of finished goods. Strategic Lab Partners delivers both under one operational model governed by SLP CONNECT, eliminating the coordination overhead that arises when kitting and fulfillment are split between vendors.",
        "bullets": [
            "Distinguishing kit assembly QC requirements from standard 3PL pick-accuracy requirements in program design.",
            "Integrating kitting production schedules with fulfillment dispatch windows to eliminate inter-vendor delays.",
            "Applying lot-control tracking continuously from kit assembly through 3PL outbound shipping.",
            "Using SLP CONNECT to present a single data view spanning both kitting and fulfillment operations.",
            "Pricing program operations on a unified per-kit model rather than splitting kitting and 3PL cost structures.",
        ],
    },
    "does-slp-offer-inbound-freight-services": {
        "t1": "Inbound freight management is the foundation of an uninterrupted kitting operation — delays or discrepancies in component receipts cascade directly into kit production shortfalls and missed fulfillment windows. Strategic Lab Partners manages inbound freight coordination and receiving inspection as an integrated part of its kitting programs, with every receipt captured in SLP CONNECT to maintain a complete component-level audit trail.",
        "bullets": [
            "Coordinating inbound component shipments from multiple suppliers to align with production schedule windows.",
            "Performing receiving inspection against purchase order specifications and flagging discrepancies immediately.",
            "Recording lot numbers, expiration dates, and quantities into SLP CONNECT at the point of receipt.",
            "Managing supplier non-conformances and coordinating replacements without program delays.",
            "Providing clients with inbound receipt visibility through SLP CONNECT dashboards updated in real time.",
        ],
    },
    "does-slp-offer-saturday-fulfillment": {
        "t1": "Clinical programs that operate on a Monday-through-Friday fulfillment cycle frequently encounter participant scheduling conflicts, holiday disruptions, and enrollment surges that demand weekend shipping capability. Strategic Lab Partners offers Saturday fulfillment for qualifying programs, extending outbound dispatch through SLP CONNECT-coordinated weekend operations to maintain delivery windows without forcing programs to buffer excess inventory.",
        "bullets": [
            "Scheduling Saturday outbound runs for time-sensitive diagnostic kit deliveries to participants or sites.",
            "Aligning Saturday fulfillment windows with carrier pickup schedules for guaranteed Monday delivery.",
            "Managing clinical trial enrollment surges that spike kit demand across the weekend shipping cycle.",
            "Providing SLP CONNECT order status updates for Saturday dispatches identical to weekday operations.",
            "Coordinating Saturday receiving for inbound component deliveries from supplier networks with weekend logistics.",
        ],
    },
    "how-does-slp-connect-improve-visibility": {
        "t1": "Supply chain visibility gaps are the root cause of most program exceptions in medical logistics — when stakeholders cannot see inventory levels, shipment status, or exception conditions in real time, problems compound before they can be addressed. SLP CONNECT resolves this by providing a unified, real-time data layer across SLP's kitting and fulfillment operations, giving program managers the intelligence they need to intervene before exceptions become failures.",
        "bullets": [
            "Accessing live inventory balances at the SKU and lot level through the SLP CONNECT dashboard.",
            "Tracking individual shipments from dispatch through final delivery without leaving the SLP CONNECT portal.",
            "Receiving automated exception alerts when orders miss SLA thresholds or encounter carrier disruptions.",
            "Reviewing historical fulfillment performance metrics to identify recurring friction points in program operations.",
            "Exporting SLP CONNECT data into program reporting tools for regulatory submissions and sponsor reviews.",
        ],
    },
    "how-does-slp-connect-integrate-with-kitting-and-3pl": {
        "t1": "SLP CONNECT is not a bolt-on reporting layer — it is the system of record that drives SLP's kitting assembly, inventory management, and 3PL fulfillment operations from a single integrated data model, eliminating the reconciliation work that plagues programs running disparate systems.",
        "bullets": [
            "Recording kit assembly completions, QC results, and lot assignments in SLP CONNECT at the production line.",
            "Triggering fulfillment pick lists from SLP CONNECT when orders are released by authorized program personnel.",
            "Synchronizing inventory deductions across kitting production and fulfillment picks in a single real-time ledger.",
            "Feeding carrier tracking numbers back into SLP CONNECT automatically upon shipment tender.",
            "Presenting a unified order lifecycle view — from kit build through delivered confirmation — in a single portal.",
        ],
    },
    "how-does-slp-connect-support-exception-handling": {
        "t1": "In medical logistics, exceptions are inevitable — the measure of an operation is how fast they are detected and resolved. SLP CONNECT is built around exception visibility, surfacing out-of-threshold conditions across inventory, production, and fulfillment as they occur and routing them to the right personnel for resolution before they affect program continuity or compliance standing.",
        "bullets": [
            "Alerting operations teams when kit inventory falls below program-defined safety stock thresholds.",
            "Flagging fulfillment orders that have not scanned at expected carrier checkpoints within SLA windows.",
            "Escalating quality holds on kit lots to program managers through SLP CONNECT notification workflows.",
            "Tracking open exceptions from detection through resolution with timestamped status updates.",
            "Generating exception frequency reports to identify systemic issues requiring process or supplier correction.",
        ],
    },
    "how-does-slp-connect-support-forecasting": {
        "t1": "Demand forecasting in clinical and diagnostic programs is complicated by enrollment variability, site-level consumption differences, and seasonal collection patterns that generic inventory systems cannot model accurately. SLP CONNECT aggregates historical consumption data, current order pipelines, and program enrollment signals to support evidence-based inventory planning that keeps kit availability aligned with actual program demand.",
        "bullets": [
            "Analyzing rolling kit consumption trends by site, region, and enrollment cohort to project future demand.",
            "Comparing forecast demand against current inventory positions to identify replenishment gaps weeks in advance.",
            "Modeling kit build schedules against component lead times to ensure production capacity meets forecast peaks.",
            "Adjusting forecast inputs in SLP CONNECT when program protocols change or enrollment accelerates.",
            "Providing sponsor-facing forecast reports that align kit supply planning with clinical milestone timelines.",
        ],
    },
    "how-does-slp-connect-support-program-visibility": {
        "t1": "Program sponsors, site coordinators, and operations teams all need different views of the same logistics data — and building those views across multiple disconnected systems wastes time and creates version-control risk. SLP CONNECT delivers role-appropriate program visibility through a single portal, so every stakeholder sees accurate, current data without reconciling spreadsheets or chasing status updates from the operations team.",
        "bullets": [
            "Configuring role-based access in SLP CONNECT so sponsors, sites, and SLP staff see appropriate data layers.",
            "Providing site coordinators with kit delivery confirmations and return receipt status through the portal.",
            "Giving sponsor program managers aggregate fulfillment performance, inventory status, and exception summaries.",
            "Enabling SLP operations to manage daily production and shipping from the same SLP CONNECT environment.",
            "Exporting program visibility data in formats compatible with sponsor reporting and regulatory audit packages.",
        ],
    },
    "how-does-slp-connect-support-site-management": {
        "t1": "Managing kit inventory, order submission, and fulfillment status across multiple clinical or collection sites demands a coordination layer that scales with site count without multiplying administrative overhead. SLP CONNECT provides site-level order management, inventory visibility, and delivery tracking through a single portal, giving site coordinators the control they need and giving program managers a consolidated view across every location.",
        "bullets": [
            "Enabling site coordinators to submit kit orders directly through SLP CONNECT within program-defined parameters.",
            "Displaying site-specific inventory levels and pending order status without requiring SLP operations team intervention.",
            "Tracking delivery confirmations to individual site addresses through carrier integration in SLP CONNECT.",
            "Alerting site personnel when kit shipments are in transit or when delivery exceptions occur.",
            "Providing program managers a cross-site inventory and fulfillment dashboard for aggregate oversight.",
        ],
    },
    "how-does-slp-design-a-kitting-program": {
        "t1": "Designing a medical kitting program that is both clinically appropriate and operationally sustainable requires a structured process that aligns clinical requirements, regulatory constraints, supplier qualifications, and production capacity into a scalable, auditable model. Strategic Lab Partners leads clients through a disciplined program design process that produces a validated, SLP CONNECT-governed kit configuration ready for commercial scale.",
        "bullets": [
            "Conducting a clinical requirements review to define kit component specifications based on protocol documentation.",
            "Evaluating supplier qualification status for each component and initiating approval processes where gaps exist.",
            "Designing kit packaging formats that meet shipping durability, labeling, and regulatory requirements.",
            "Developing production SOPs and QC inspection criteria aligned with the program's compliance framework.",
            "Configuring SLP CONNECT with the program's kit SKUs, ordering rules, and reporting parameters before launch.",
        ],
    },
    "how-does-slp-ensure-quality-and-compliance": {
        "t1": "Quality and compliance in medical kitting are not achieved through inspection alone — they are built into every process, from component sourcing through kit assembly to outbound shipment. Strategic Lab Partners operates a documented quality management system that integrates with SLP CONNECT to enforce lot control, expiration management, and assembly verification at every production step, creating a chain of custody that withstands regulatory scrutiny.",
        "bullets": [
            "Verifying component lot numbers and expiration dates against program specifications before kit assembly begins.",
            "Applying documented assembly checklists and in-process QC checks at defined production milestones.",
            "Quarantining non-conforming components and kits and initiating CAPA processes through SLP CONNECT.",
            "Maintaining complete batch records linking every finished kit to its component lots and assembly personnel.",
            "Providing clients with on-demand QC documentation and audit support through SLP CONNECT reporting.",
        ],
    },
    "how-does-slp-ensure-test-id-accuracy": {
        "t1": "Test ID accuracy is a non-negotiable requirement in diagnostic and clinical programs — a mismatched or duplicate ID renders a specimen scientifically unusable and may invalidate program data. Strategic Lab Partners builds test ID management into kit assembly and SLP CONNECT from the ground up, using barcode verification, sequential ID assignment, and system-level duplicate prevention to eliminate ID errors before kits ever leave the facility.",
        "bullets": [
            "Assigning test IDs sequentially from program-specific ranges with system-enforced uniqueness validation.",
            "Scanning and verifying each barcode label against the assigned ID database at the point of kit labeling.",
            "Blocking kit completion in SLP CONNECT when a barcode scan does not match the expected ID assignment.",
            "Maintaining a complete ID-to-kit-to-shipment linkage in SLP CONNECT from assembly through lab receipt.",
            "Providing ID reconciliation reports that match dispatched kit IDs against received and processed specimen records.",
        ],
    },
    "how-does-slp-handle-kit-manufacturing-and-assembly": {
        "t1": "Medical kit manufacturing and assembly demand a controlled environment, validated processes, and relentless attention to component accuracy — conditions that most clinical organizations cannot replicate internally without substantial investment. Strategic Lab Partners manages the full kit manufacturing lifecycle in a regulated facility, applying documented SOPs and SLP CONNECT-governed lot tracking from raw component receipt through finished kit dispatch.",
        "bullets": [
            "Staging validated components by lot and expiration in climate-controlled pre-assembly areas before production runs.",
            "Following documented, SOP-driven assembly sequences with in-process verification at each build step.",
            "Recording kit build completions, component lots, and assembler identification in SLP CONNECT in real time.",
            "Performing final QC inspection against a program-specific acceptance checklist before kits enter finished goods.",
            "Managing packaging, labeling, and palletization to meet carrier and regulatory specifications for dispatch.",
        ],
    },
    "how-does-slp-handle-multi-item-orders": {
        "t1": "Multi-item medical orders — combining different kit types, ancillary supplies, or documentation packages into a single shipment — introduce picking complexity and labeling requirements that standard 3PL workflows are not designed to handle reliably. Strategic Lab Partners manages multi-item orders through SLP CONNECT-coordinated pick sequences and consolidated packing validation that confirm every item is present and correctly labeled before the shipment is sealed.",
        "bullets": [
            "Generating pick lists in SLP CONNECT that sequence multi-item orders by bin location to minimize fulfillment errors.",
            "Applying consolidated packing checklists that verify all items are present before packaging is sealed.",
            "Printing combined packing slips and regulatory manifests that account for all items in the shipment.",
            "Flagging multi-item orders with incomplete picks as exceptions in SLP CONNECT before they reach the carrier.",
            "Tracking multi-item shipments at the order level through SLP CONNECT with full item-level detail.",
        ],
    },
    "how-does-slp-handle-order-fulfillment": {
        "t1": "Medical order fulfillment is not a commodity pick-pack-ship operation — it involves regulated components, compliance documentation, chain-of-custody requirements, and delivery accuracy standards that generic logistics providers cannot reliably meet. Strategic Lab Partners operates a fulfillment model purpose-built for healthcare programs, using SLP CONNECT to govern every order from release through delivery confirmation with full traceability.",
        "bullets": [
            "Releasing orders through SLP CONNECT after authorization validation against program-defined ordering rules.",
            "Picking and packing kits using barcode-verified workflows that confirm item identity and quantity accuracy.",
            "Applying program-specific carrier selection, service level, and labeling requirements to every outbound shipment.",
            "Tendering shipments to carriers and receiving tracking numbers back into SLP CONNECT automatically.",
            "Monitoring delivery confirmation and flagging exceptions for undelivered or delayed shipments within SLA windows.",
        ],
    },
    "how-does-slp-handle-returns-and-reverse-logistics": {
        "t1": "Returns and reverse logistics in medical programs are a compliance requirement in programs that involve specimen collection, expired kit recovery, or regulated material disposal. Strategic Lab Partners manages inbound returns through documented receiving processes, SLP CONNECT lot reconciliation, and disposition workflows that ensure returned materials are handled in accordance with program and regulatory requirements.",
        "bullets": [
            "Receiving returned kits and specimen shipments against expected return records in SLP CONNECT.",
            "Inspecting returned materials to determine disposition — reuse, quarantine, destruction, or lab transfer.",
            "Crediting inventory in SLP CONNECT for returned usable kits after inspection and re-qualification.",
            "Documenting and disposing of non-recoverable or expired returned materials per regulatory requirements.",
            "Providing return reconciliation reports in SLP CONNECT that match dispatched kit IDs against received returns.",
        ],
    },
    "how-does-slp-manage-inventory-for-clients": {
        "t1": "Inventory management in regulated medical programs requires lot-level accountability, expiration date management, and real-time visibility that keeps program managers ahead of stockouts and compliance risks before they become operational crises. Strategic Lab Partners manages client inventory within SLP CONNECT, providing a continuously updated system of record that covers every component and finished kit from receipt through consumption.",
        "bullets": [
            "Maintaining lot-level inventory records in SLP CONNECT that track quantity, expiration, and quarantine status.",
            "Generating automated reorder alerts when kit inventory approaches program-defined safety stock thresholds.",
            "Applying FEFO (first-expired, first-out) logic to outbound fulfillment picks to minimize expiration waste.",
            "Providing clients with on-demand inventory reports covering all SKUs, lots, and storage locations.",
            "Reconciling inventory counts through periodic cycle counts verified against SLP CONNECT records.",
        ],
    },
    "how-does-slp-prevent-duplicate-test-ids": {
        "t1": "Duplicate test IDs are a silent but catastrophic risk in diagnostic programs — they create specimen matching failures, compromise data integrity, and can trigger regulatory findings that invalidate study results. Strategic Lab Partners prevents duplicate test ID assignment through system-enforced sequential allocation, barcode verification at labeling, and real-time SLP CONNECT validation that blocks any kit from completing assembly with a non-unique ID.",
        "bullets": [
            "Assigning test IDs from program-exclusive ranges with database-level uniqueness constraints in SLP CONNECT.",
            "Scanning every barcode label at the assembly station and validating the scan against the authorized ID pool.",
            "Blocking kit completion in SLP CONNECT when a scanned ID is already assigned to another kit record.",
            "Auditing assigned ID ranges against kit production counts to identify and investigate any sequence gaps.",
            "Providing ID assignment logs to program sponsors for cross-reference against lab receipt and processing records.",
        ],
    },
    "how-does-slp-scale-with-customer-growth": {
        "t1": "Program growth is the goal — but it is also the event that exposes every structural weakness in a medical logistics operation. Strategic Lab Partners is built on a scalable infrastructure model that absorbs volume increases without requiring clients to renegotiate contracts, onboard new vendors, or rebuild operational processes, while SLP CONNECT maintains the same governance and visibility regardless of order volume.",
        "bullets": [
            "Increasing kit production capacity by adding assembly shifts within SLP's existing regulated facility footprint.",
            "Expanding outbound fulfillment throughput through carrier network surge agreements pre-negotiated by SLP.",
            "Onboarding new kit SKUs or program variants in SLP CONNECT without disrupting existing program operations.",
            "Adding new sites or geographies to an existing program with configuration changes rather than operational rebuilds.",
            "Maintaining SLP CONNECT performance and data integrity at scale without system re-implementation.",
        ],
    },
    "how-does-slp-support-multi-site-programs": {
        "t1": "Multi-site clinical and diagnostic programs amplify every logistics challenge — each additional site adds ordering complexity, inventory allocation decisions, and delivery tracking requirements that quickly overwhelm programs running manual coordination. Strategic Lab Partners manages multi-site programs through SLP CONNECT's site-level order management and inventory visibility architecture, delivering consistent kit access to every location without proportionally increasing administrative overhead.",
        "bullets": [
            "Configuring site-specific ordering rules, kit allocations, and delivery preferences in SLP CONNECT.",
            "Enabling site coordinators to submit and track orders through SLP CONNECT without SLP staff mediation.",
            "Allocating kit inventory across sites based on program-defined priority rules and current site consumption rates.",
            "Delivering aggregate and site-level fulfillment performance reporting to program managers through SLP CONNECT.",
            "Expanding the program to new sites by adding SLP CONNECT site profiles without operational disruption.",
        ],
    },
    "how-does-slp-work-with-3pl-and-deployment": {
        "t1": "Deploying medical kits at scale through a 3PL network demands a governance layer that maintains quality and compliance accountability as kits move through the extended supply chain. Strategic Lab Partners coordinates 3PL deployment as part of its integrated service model, using SLP CONNECT to maintain chain-of-custody tracking and exception visibility from SLP's kitting facility through the 3PL to final delivery.",
        "bullets": [
            "Transferring finished kit inventory to 3PL nodes with complete lot documentation and SLP CONNECT records.",
            "Maintaining real-time inventory visibility at 3PL storage locations through SLP CONNECT integration.",
            "Coordinating 3PL outbound fulfillment against SLP CONNECT-released orders with carrier tracking feedback.",
            "Escalating 3PL delivery exceptions into SLP CONNECT for program manager notification and resolution.",
            "Auditing 3PL cycle count data against SLP CONNECT inventory records on a scheduled basis.",
        ],
    },
    "how-many-skus-should-a-medical-kitting-program-have": {
        "t1": "Every additional SKU in a medical kitting program adds inventory carrying cost, QC complexity, and reconciliation overhead. Strategic Lab Partners helps clients assess their kit catalog against actual clinical requirements, identifying consolidation opportunities that reduce SKU count without sacrificing program flexibility, and then governs the rationalized catalog through SLP CONNECT.",
        "bullets": [
            "Auditing the existing kit catalog to identify configurations with redundant components or overlapping use cases.",
            "Modeling the cost and complexity impact of each SKU on assembly labor, QC inspection, and inventory management.",
            "Proposing consolidation scenarios that reduce SKU count while maintaining clinical protocol compliance.",
            "Reconfiguring SLP CONNECT after rationalization to reflect the updated catalog with revised ordering rules.",
            "Monitoring consolidated SKU consumption post-launch to confirm the new catalog meets program demand patterns.",
        ],
    },
    "how-medical-fulfillment-improves-accuracy-and-reliability": {
        "t1": "Accuracy and reliability in medical fulfillment are outcomes of systematic process controls applied consistently across every order — not good intentions. Strategic Lab Partners achieves fulfillment accuracy through barcode-verified picking, assembly validation, and SLP CONNECT order confirmation workflows that catch errors before they reach the carrier.",
        "bullets": [
            "Implementing barcode scan-confirm picking that verifies item identity and quantity before packaging.",
            "Applying order completion validation in SLP CONNECT that blocks shipment tender when discrepancies are detected.",
            "Tracking fulfillment accuracy rates by order type and operator to identify and correct performance gaps.",
            "Conducting daily shipment audits against SLP CONNECT records to confirm dispatch accuracy.",
            "Providing clients with fulfillment accuracy reporting through SLP CONNECT on a program-defined frequency.",
        ],
    },
    "how-medical-fulfillment-improves-logistics-for-healthcare-programs": {
        "t1": "Healthcare programs that rely on improvised or general-purpose logistics solutions routinely encounter delayed shipments, inaccurate orders, compliance gaps, and the inability to recover quickly when exceptions occur. Strategic Lab Partners replaces that fragility with purpose-built medical fulfillment governed by SLP CONNECT, giving program operators a logistics foundation designed specifically for the accuracy, compliance, and audit requirements of healthcare operations.",
        "bullets": [
            "Replacing multi-vendor logistics arrangements with a single SLP-managed fulfillment operation.",
            "Applying healthcare-specific labeling, documentation, and carrier selection standards to every shipment.",
            "Providing real-time fulfillment status through SLP CONNECT rather than requiring manual status inquiry.",
            "Building exception escalation workflows that surface logistics problems to program managers within minutes.",
            "Generating compliance-ready fulfillment documentation for regulatory submissions and sponsor audits.",
        ],
    },
    "how-medical-fulfillment-reduces-operational-burden-for-healthcare-organizations": {
        "t1": "When healthcare organizations manage fulfillment internally, logistics overhead competes directly with clinical priorities for staff time, budget, and management attention. Strategic Lab Partners transfers that operational burden to a dedicated fulfillment infrastructure governed by SLP CONNECT — allowing healthcare teams to redirect internal resources to the clinical work that generates outcomes rather than the logistics work that enables delivery.",
        "bullets": [
            "Absorbing kit assembly, QC, warehousing, and outbound shipping so clinical staff can focus on program delivery.",
            "Providing SLP CONNECT visibility that eliminates the need for internal status tracking and vendor follow-up.",
            "Managing carrier relationships, exception resolution, and compliance documentation on behalf of the client.",
            "Scaling fulfillment volume in response to program demand without client staffing or infrastructure changes.",
            "Delivering consolidated billing and performance reporting that reduces internal administrative reconciliation work.",
        ],
    },
    "how-medical-fulfillment-supports-distributed-healthcare-networks": {
        "t1": "Distributed healthcare networks — spanning multiple clinics, collection sites, or participant homes — create a logistics challenge that scales geometrically with geographic spread. Strategic Lab Partners addresses distributed network complexity through SLP CONNECT-coordinated fulfillment that routes the right kit to the right location on the right schedule, maintaining consistent delivery performance regardless of network size or geographic diversity.",
        "bullets": [
            "Mapping kit delivery requirements across distributed network nodes and aligning carrier service levels accordingly.",
            "Maintaining site-specific inventory allocations in SLP CONNECT to prevent imbalances across the network.",
            "Routing participant-direct shipments with address validation and carrier selection optimized for last-mile delivery.",
            "Providing network-wide fulfillment performance dashboards in SLP CONNECT for program manager oversight.",
            "Coordinating return logistics from distributed sites back to SLP facilities through pre-configured return workflows.",
        ],
    },
    "how-medical-fulfillment-supports-scalable-healthcare-programs": {
        "t1": "Healthcare programs that grow quickly — whether driven by enrollment acceleration, geographic expansion, or protocol additions — expose the scalability limits of fulfillment operations built for steady-state volume. Strategic Lab Partners designs its fulfillment infrastructure to absorb growth without operational disruption, using SLP CONNECT to maintain program governance as volume scales and new program elements are added.",
        "bullets": [
            "Increasing fulfillment throughput by activating additional shift capacity within SLP's existing facility.",
            "Onboarding new kit SKUs or program geographies in SLP CONNECT without interrupting current operations.",
            "Pre-negotiating carrier volume agreements that accommodate program growth scenarios without surcharge exposure.",
            "Maintaining SLP CONNECT performance and data accuracy as order volume scales across program expansion phases.",
            "Providing clients with scalability roadmaps that align kit supply capacity with enrollment and protocol timelines.",
        ],
    },
    "how-medical-kitting-improves-operational-efficiency": {
        "t1": "Operational efficiency in healthcare logistics is undermined by fragmented kit assembly processes, inconsistent QC application, and the administrative overhead of managing multiple component suppliers. Strategic Lab Partners consolidates those functions into a single regulated kitting operation governed by SLP CONNECT, reducing per-kit processing time, eliminating inter-vendor coordination delays, and giving program managers real-time data to make faster decisions.",
        "bullets": [
            "Standardizing kit assembly workflows to eliminate variable build times and reduce per-unit labor cost.",
            "Consolidating component sourcing under SLP's qualified supplier network to remove individual vendor management.",
            "Applying in-process QC at defined assembly checkpoints rather than end-of-line inspection to catch defects earlier.",
            "Reducing kit changeover time between program variants through SLP CONNECT configuration management.",
            "Providing production throughput and efficiency metrics through SLP CONNECT for program operations review.",
        ],
    },
    "how-medical-kitting-improves-patient-care": {
        "t1": "The connection between kitting logistics and patient care outcomes is direct: when patients or participants receive the right kit at the right time, in working condition, with clear instructions, the clinical value of the program is preserved. Strategic Lab Partners treats kit delivery accuracy and reliability as patient care requirements — not logistics metrics — building every process around the outcome of a successful patient interaction.",
        "bullets": [
            "Delivering participant-ready kits with patient-facing instructions formatted to program and literacy standards.",
            "Ensuring kit components are within expiration, intact, and correctly assembled before dispatch.",
            "Routing kits through carriers with proven residential delivery performance to minimize failed delivery attempts.",
            "Providing return pre-paid shipping with kits to maximize specimen return rates and reduce participant friction.",
            "Tracking delivery confirmations so program coordinators can proactively follow up with non-responsive participants.",
        ],
    },
    "how-medical-kitting-improves-sample-quality-and-consistency": {
        "t1": "Sample quality in diagnostic programs begins before the sample is collected — it begins with the kit. Inconsistent component specifications, incorrect collection tube types, or improperly sealed collection materials compromise sample integrity at the source. Strategic Lab Partners engineers sample quality into every kit through validated component selection, controlled assembly, and SLP CONNECT lot tracking that connects every sample result to a specific kit build.",
        "bullets": [
            "Specifying collection materials to match assay and transport requirements defined in the program protocol.",
            "Validating collection tube types, anticoagulants, and storage conditions against the laboratory's acceptance criteria.",
            "Assembling kits in a controlled environment with documented temperature and humidity monitoring records.",
            "Applying lot-control tracking to every collection component so anomalous results can be traced to a specific batch.",
            "Providing SLP CONNECT reports linking kit lot data to laboratory receipt records for quality investigation support.",
        ],
    },
}


def slugify(path: Path) -> str:
    return path.stem  # filename without .html


def build_t1(t1_text: str) -> str:
    return (
        '<p class="faq-intro-lead" style="font-size: 1.125rem; line-height: 1.75; '
        'margin-top: 1rem; margin-bottom: 1.5rem; color: #374151;">'
        + t1_text
        + "</p>"
    )


def build_t2(bullets: list) -> str:
    li_items = "".join(
        f'<li style="margin-bottom: 0.5rem;">{b}</li>' for b in bullets
    )
    return (
        '<div class="faq-practical-apps" style="margin-top: 2rem; margin-bottom: 2rem; '
        'padding: 1.25rem; background-color: #f9fafb; border-left: 4px solid #0284c7; '
        'border-radius: 0.375rem;">'
        '<p style="font-weight: 700; margin-bottom: 0.75rem; color: #111827; font-size: 1rem;">'
        "Practical applications:</p>"
        '<ul style="list-style-type: disc; margin-left: 1.5rem; color: #4b5563;">'
        + li_items
        + "</ul></div>"
    )


def generate_fallback(slug: str, h1_text: str) -> dict:
    """Generate plausible T1 + bullets for any slug not in CONTENT."""
    topic = h1_text.strip().rstrip("?")
    t1 = (
        f"{topic} is a critical operational challenge for healthcare programs managing "
        "regulated kitting and fulfillment at scale. Strategic Lab Partners addresses "
        "this directly through standardized kitting processes, governed fulfillment "
        "workflows, and continuous SLP CONNECT oversight — delivering the operational "
        "stability and compliance readiness your program requires."
    )
    bullets = [
        f"Applying SLP's regulated kitting and fulfillment model to {topic.lower()} scenarios.",
        "Maintaining complete lot-level traceability through SLP CONNECT from component receipt to delivery.",
        "Surfacing real-time exceptions and inventory status through the SLP CONNECT dashboard.",
        "Scaling program capacity without rebuilding logistics infrastructure or renegotiating vendor contracts.",
        "Generating compliance-ready documentation and audit trails for regulatory review.",
    ]
    return {"t1": t1, "bullets": bullets}


def process_file(html_path: Path) -> bool:
    raw = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")

    # ── Idempotency check ──────────────────────────────────────────────────────
    article = soup.find("article")
    if not article:
        # Fallback: use body or first block element
        article = soup.find("body") or soup

    if not FORCE and article.get("data-slp-updated") == MARKER:
        print(f"  SKIP (already updated): {html_path.name}")
        return False

    # ── Resolve content ────────────────────────────────────────────────────────
    slug    = slugify(html_path)
    h1_tag  = soup.find("h1")
    h1_text = h1_tag.get_text(strip=True) if h1_tag else slug.replace("-", " ").title()
    data    = CONTENT.get(slug) or generate_fallback(slug, h1_text)

    t1_html = build_t1(data["t1"])
    t2_html = build_t2(data["bullets"])

    # ── Remove any previous T1-T4 blocks if --force ────────────────────────────
    for cls in ("faq-intro-lead", "faq-practical-apps", "faq-prevention-statement", "faq-closing-cta"):
        for el in article.find_all(class_=cls):
            el.decompose()

    # ── Collect direct-child block elements of article ─────────────────────────
    def is_block(tag):
        return isinstance(tag, Tag) and tag.name in (
            "p", "h1", "h2", "h3", "h4", "h5", "h6",
            "ul", "ol", "div", "blockquote", "section",
        )

    blocks = [c for c in article.children if is_block(c)]

    # ── T1: replace first <p> after <h1> ──────────────────────────────────────
    first_p_after_h1 = None
    seen_h1 = False
    for tag in blocks:
        if tag.name == "h1":
            seen_h1 = True
        elif seen_h1 and tag.name == "p" and first_p_after_h1 is None:
            first_p_after_h1 = tag

    t1_soup = BeautifulSoup(t1_html, "html.parser").find()
    if first_p_after_h1:
        first_p_after_h1.replace_with(t1_soup)
    elif h1_tag:
        h1_tag.insert_after(t1_soup)
    else:
        article.insert(0, t1_soup)

    # Re-collect blocks after T1 insertion
    blocks = [c for c in article.children if is_block(c)]

    # ── T2: insert after 2nd paragraph (or after T1 if only one paragraph) ────
    p_tags = [b for b in blocks if b.name == "p"]
    insert_after = p_tags[1] if len(p_tags) >= 2 else (p_tags[0] if p_tags else h1_tag)
    t2_soup = BeautifulSoup(t2_html, "html.parser").find()
    if insert_after:
        insert_after.insert_after(t2_soup)
    else:
        article.append(t2_soup)

    # Re-collect blocks again
    blocks = [c for c in article.children if is_block(c)]

    # ── T3: insert before last block element ──────────────────────────────────
    t3_soup = BeautifulSoup(T3_HTML, "html.parser").find()
    if blocks:
        blocks[-1].insert_before(t3_soup)
    else:
        article.append(t3_soup)

    # ── T4: append as absolute last element ───────────────────────────────────
    t4_soup = BeautifulSoup(T4_HTML, "html.parser").find()
    article.append(t4_soup)

    # ── Mark as updated ───────────────────────────────────────────────────────
    article["data-slp-updated"] = MARKER

    # ── Write back ────────────────────────────────────────────────────────────
    html_path.write_text(str(soup), encoding="utf-8")
    print(f"  UPDATED: {html_path.name}")
    return True


def main():
    if not FAQ_DIR.exists():
        print(f"ERROR: FAQ directory not found: {FAQ_DIR}")
        sys.exit(1)

    html_files = sorted(
        f for f in FAQ_DIR.glob("*.html") if f.name != "index.html"
    )
    print(f"Found {len(html_files)} FAQ files in {FAQ_DIR}")
    print(f"Mode: {'FORCE (reprocess all)' if FORCE else 'INCREMENTAL (skip updated)'}\n")

    updated = skipped = 0
    for f in html_files:
        if process_file(f):
            updated += 1
        else:
            skipped += 1

    print(f"\nDone — {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
