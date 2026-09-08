"""Controlled, deterministic response templates."""

DEFINITION_TEMPLATE = """**{term_display}** means:

{definition_sentence}

*Educational information based on verified regulatory guidelines.*"""

EXPLANATION_TEMPLATE = """**{topic_title}**

{body_sentences}

*Educational information based on verified regulatory guidelines.*"""

PROCEDURE_TEMPLATE = """According to the verified official source, the procedure for **{procedure_title}** involves the following steps:

{steps_list}

*Requirements may differ across financial institutions. Refer to the cited guidelines for details.*"""

COMPARISON_TEMPLATE = """### Comparison: {topic_a} vs {topic_b}

| Aspect | {topic_a} | {topic_b} |
|---|---|---|
| **Overview** | {summary_a} | {summary_b} |
| **Key Details** | {details_a} | {details_b} |

*This comparison is educational. Consult the respective official terms for full conditions.*"""

CALCULATION_TEXT_TEMPLATE = """**Calculation: {calc_name}**

**Inputs:**
{inputs_list}

**Result:**
{result_list}

**Formula:**
`{formula}`

**Assumptions:**
{assumptions_list}"""

CLARIFICATION_TEMPLATE = """I need a bit more detail to answer your question accurately: **{missing_field}**.

{example_prompt}"""

INSUFFICIENT_EVIDENCE_TEMPLATE = """I could not locate an exact regulatory clause for that specific phrase in the active knowledge base.

**You can ask me anything across these financial domains:**
- **Banking & UPI**: *Savings vs Current Accounts*, *DICGC ₹5 Lakh Insurance*, *UPI Lite*, *NEFT vs RTGS*
- **Loans & Credit**: *Loan EMI calculations*, *Fixed vs Floating Rates*, *CIBIL Score dynamics*, *Foreclosure rules*
- **Taxation & 80C**: *Old vs New Tax Regime*, *Section 80C & 80D deductions*, *Capital Gains (LTCG / STCG)*
- **Mutual Funds & Wealth**: *SIP wealth compounding*, *Equity vs Debt Funds*, *Direct vs Regular plans*, *CAGR*
- **Consumer Protection**: *RBI Integrated Ombudsman Scheme*, *Credit Card Zero-Liability protection*
- **Calculations**: *'Calculate EMI for 10 lakh at 9% for 5 years'*, *'10% of 50000 salary'*, *'SIP for 5000 at 12% for 10 years'*"""

