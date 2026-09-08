#!/usr/bin/env python
"""Seed curated authoritative FinTech regulatory knowledge documents."""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.models.source import Source, Category
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.index_manager import IndexManager
from app.core.config import settings

DOCUMENTS_SEED = [
    {
        "filename": "rbi_neft_rtgs_imps_faq.md",
        "title": "RBI FAQs on Electronic Fund Transfers: NEFT, RTGS, IMPS",
        "source_name": "Reserve Bank of India",
        "category_slug": "banking",
        "source_url": "https://www.rbi.org.in/Scripts/FAQView.aspx?Id=60",
        "publication_date": date(2025, 1, 15),
        "last_updated": date(2026, 1, 10),
        "content": """# Reserve Bank of India - Electronic Fund Transfers FAQ

## What is NEFT?
National Electronic Funds Transfer (NEFT) is a nationwide centralised payment system owned and operated by the Reserve Bank of India. NEFT operates on a round-the-clock basis (24x7x365) in batches processed every half hour. There is no minimum or maximum limit on the amount of funds that could be transferred using NEFT for individual retail customers.

## What is RTGS?
Real Time Gross Settlement (RTGS) is a continuous, real-time funds settlement system where fund transfer instructions are processed individually and immediately across participating bank accounts. RTGS is primarily meant for large-value transactions. The minimum amount to be remitted through RTGS is ₹2,00,000 (Rupees Two Lakh), with no upper ceiling. RTGS is available 24x7x365 across India.

## What is IMPS?
Immediate Payment Service (IMPS) is an instant, round-the-clock interbank electronic fund transfer service provided by the National Payments Corporation of India (NPCI). IMPS allows customers to instantly transfer funds through mobile banking, internet banking, and ATMs using bank account numbers and IFSC codes or Mobile Number and MMID. The daily limit for IMPS transfers is typically up to ₹5,00,000.

## Difference between NEFT and RTGS
The key difference between NEFT and RTGS is in the settlement mechanism and transaction limits. NEFT settles fund transfers in half-hourly batches, whereas RTGS settles individual transactions continuously in real-time. Furthermore, RTGS requires a minimum transaction amount of ₹2 lakh, whereas NEFT has no mandatory minimum amount requirement.
"""
    },
    {
        "filename": "rbi_kyc_and_bank_accounts.md",
        "title": "RBI Master Direction on KYC Norms and Bank Account Operations",
        "source_name": "Reserve Bank of India",
        "category_slug": "banking",
        "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566",
        "publication_date": date(2025, 4, 1),
        "last_updated": date(2026, 1, 1),
        "content": """# RBI KYC Guidelines and Customer Identification

## What is KYC?
KYC means Know Your Customer. It is a regulatory process established by the Reserve Bank of India to verify the identity and address of customers opening bank accounts, taking loans, or engaging in financial transactions. KYC is mandatory under the Prevention of Money Laundering Act (PMLA) to prevent financial fraud, identity theft, and money laundering.

## How to complete KYC?
To complete KYC verification with a regulated financial institution, a customer must provide an Officially Valid Document (OVD) for identity and proof of address. Approved documents include Passport, Driving Licence, Proof of possession of Aadhaar number, Voter's Identity Card, and NREGA Job Card. Customers can complete KYC in-person at a bank branch or digitally using Video-based Customer Identification Process (V-CIP).

## What are Savings Accounts and Deposit Protection?
A savings bank account is an interest-bearing deposit facility maintained by commercial banks allowing individuals to deposit surplus funds and make electronic withdrawals. Under the Deposit Insurance and Credit Guarantee Corporation (DICGC), an RBI subsidiary, each depositor in an insured bank is insured up to a maximum of ₹5,00,000 for both principal and interest amounts across all deposit accounts in the same bank.
"""
    },
    {
        "filename": "rbi_loans_emi_and_borrower_rights.md",
        "title": "RBI Borrower Education Guide on Loans, Interest Rates, and EMI",
        "source_name": "Reserve Bank of India",
        "category_slug": "loans",
        "source_url": "https://www.rbi.org.in/FinancialEducation/loans.html",
        "publication_date": date(2025, 2, 10),
        "last_updated": date(2026, 1, 5),
        "content": """# Borrower Education Guide: Loans and Interest

## What is an EMI?
EMI means Equated Monthly Instalment. It is a fixed monetary payment made by a borrower to a lender at a specified calendar date each month. Equated Monthly Instalments are calculated from the loan principal, periodic interest rate, and total number of monthly installments. Each EMI payment pays down both the principal loan balance and accrued interest.

## How is EMI calculated?
EMI is calculated using the formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1), where P is principal loan amount, r is the monthly interest rate (annual interest rate divided by 1200), and n is the loan tenure in months. In the early tenure of a loan, a larger portion of each EMI comprises interest, while in later stages, a higher proportion amortizes the principal.

## What is Loan Prepayment and Foreclosure?
Prepayment is the process where a borrower repays a portion or the entire outstanding loan balance before the agreed tenure ends. According to RBI regulatory guidelines, banks and NBFCs are prohibited from levying foreclosure charges or prepayment penalties on floating-rate term loans sanctioned to individual borrowers for purposes other than business.

## Difference between Secured and Unsecured Loans
A secured loan is backed by collateral or an asset provided by the borrower, such as real estate property for a home loan or a vehicle for a car loan. An unsecured loan (such as a personal loan or credit card debt) requires no collateral asset and is approved based on the borrower's creditworthiness, income stability, and credit score.
"""
    },
    {
        "filename": "rbi_credit_cards_and_cibil.md",
        "title": "RBI Guidelines on Credit Card Operations, Billing, and Credit Scores",
        "source_name": "Reserve Bank of India",
        "category_slug": "credit_cards",
        "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12300",
        "publication_date": date(2025, 3, 1),
        "last_updated": date(2026, 1, 20),
        "content": """# Credit Card Consumer Guidance

## What is a Credit Card and Billing Cycle?
A credit card is a revolving payment instrument issued by authorized financial institutions that allows cardholders to borrow funds up to a pre-approved credit limit to pay for goods and services. The billing cycle is the monthly recurring period between two consecutive statement generation dates, typically ranging from 28 to 31 days.

## What is Minimum Due on a Credit Card?
Minimum due is the minimum amount specified on a credit-card statement (usually 5% of total outstanding balance) that must be paid on or before the payment due date to avoid late payment charges. Paying only the minimum due avoids late penalties but leaves the unpaid balance subject to compounding finance charges and interest rates (often 36% to 42% annualized).

## What is a Credit Score and CIBIL?
A credit score is a three-digit numeric summary (ranging from 300 to 900) of an individual's credit history and repayment reliability, calculated by registered credit bureaus such as TransUnion CIBIL, Experian, CRIF High Mark, and Equifax. A higher score (typically 750 and above) improves loan eligibility, enables lower interest rates, and speeds up credit approval.
"""
    },
    {
        "filename": "sebi_amfi_mutual_funds_and_sip.md",
        "title": "SEBI and AMFI Investor Education: Mutual Funds, SIP, and Wealth Concepts",
        "source_name": "Securities and Exchange Board of India",
        "category_slug": "investments",
        "source_url": "https://investor.sebi.gov.in/mutualfunds.html",
        "publication_date": date(2025, 5, 20),
        "last_updated": date(2026, 2, 1),
        "content": """# Mutual Funds and Systematic Investment Planning

## What is a Mutual Fund?
A mutual fund is an investment vehicle managed by an Asset Management Company (AMC) that pools money from multiple investors to purchase a diversified portfolio of securities such as equities, government bonds, corporate debentures, and money market instruments. Each investor owns units representing a proportional share of the fund's net asset value (NAV).

## What is a SIP?
SIP means Systematic Investment Plan. It is an investment facility offered by mutual funds allowing individuals to invest a fixed sum of money periodically (monthly or quarterly) into a chosen mutual fund scheme. SIP instills financial discipline and benefits from rupee cost averaging and the power of compounding.

## What is CAGR?
CAGR stands for Compound Annual Growth Rate. It represents the mean annual growth rate of an investment over a specified time period longer than one year. It smooths out volatility by calculating the constant rate at which an initial capital would have grown to its ending balance: CAGR = (Ending Value / Beginning Value)^(1/years) - 1.

## Fixed Deposit vs Mutual Fund
A Fixed Deposit (FD) offers guaranteed capital safety and fixed interest returns up to the maturity date, protected up to ₹5 lakh by DICGC insurance. A Mutual Fund invests in market-linked instruments (equities or debt) where returns fluctuate with market conditions and are not guaranteed, but offer potential for inflation-beating long-term capital growth.

## What is a Fixed Deposit and Recurring Deposit?
A Fixed Deposit (FD) is a financial deposit where a lump-sum amount is deposited in a bank for a predetermined tenure at a fixed interest rate. A Recurring Deposit (RD) is an investment product where a depositor contributes a fixed equal amount every month for a specific tenure, earning interest comparable to fixed deposits.
"""
    },
    {
        "filename": "irdai_insurance_fundamentals.md",
        "title": "IRDAI Consumer Guide on Health and Life Insurance",
        "source_name": "Insurance Regulatory and Development Authority of India",
        "category_slug": "insurance",
        "source_url": "https://policyholder.gov.in/web/guest/life-insurance",
        "publication_date": date(2025, 6, 1),
        "last_updated": date(2026, 1, 15),
        "content": """# IRDAI Insurance Consumer Education

## What is Insurance and Premium?
Insurance is a risk management contract in which an individual pays a designated amount called a premium to an insurance company in exchange for financial protection or reimbursement against covered losses, medical expenses, or death.

## What is a Deductible in Health Insurance?
A deductible in health insurance is a predetermined out-of-pocket amount that the policyholder must pay toward covered medical expenses before the insurance provider begins paying its share of the claim. A higher deductible typically results in a lower annual premium.

## Term Insurance vs Health Insurance
Term insurance is a pure life insurance policy that pays a guaranteed lump-sum death benefit to designated beneficiaries if the insured passes away during the active policy term. Health insurance covers medical, hospitalization, and surgical expenses incurred due to illness or accidental injuries of the insured.

## How to file an insurance claim?
The process for filing a health insurance claim requires notifying the insurer or Third Party Administrator (TPA) within designated timelines (e.g. 24 hours in emergency hospitalization). For cashless claims, submit the pre-authorization form at a network hospital. For reimbursement claims, submit original hospital discharge summaries, itemized bills, pharmacy receipts, and diagnostic reports along with the completed claim form.
"""
    },
    {
        "filename": "incometax_tds_and_deductions.md",
        "title": "Income Tax Department Guide on TDS, Deductions, and Tax Terms",
        "source_name": "Income Tax Department of India",
        "category_slug": "taxation",
        "source_url": "https://www.incometax.gov.in/iec/foportal/help/individual/basics",
        "publication_date": date(2025, 4, 15),
        "last_updated": date(2026, 1, 1),
        "content": """# Income Tax Basics and TDS Provisions

## What is TDS?
TDS stands for Tax Deducted at Source. It is a direct taxation mechanism under the Indian Income Tax Act where the person or entity responsible for making specified payments (such as salary, interest on deposits, rent, professional fees) deducts tax at prescribed rates before remitting the balance to the recipient. The deducted tax is deposited directly with the Central Government under the payee's PAN.

## What is Financial Year vs Assessment Year?
The Financial Year (FY) is the 12-month period starting from 1st April to 31st March in which an individual or business earns income. The Assessment Year (AY) is the immediately following financial year in which the earned income is evaluated, tax liability is computed, and Income Tax Returns (ITR) are filed. For example, income earned in FY 2025-26 is assessed in AY 2026-27.

## What are Tax Deductions?
Tax deductions are statutory provisions under chapter VI-A of the Income Tax Act (such as Section 80C, 80D) that reduce the total gross taxable income of an eligible taxpayer under the Old Tax Regime. Deductions incentivize investments in instruments like PPF, ELSS mutual funds, and health insurance premiums.
"""
    }
]


def seed_corpus():
    settings.RAW_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()

    try:
        pipeline = IngestionPipeline(db)

        for doc_info in DOCUMENTS_SEED:
            filepath = settings.RAW_DIR / doc_info["filename"]
            filepath.write_text(doc_info["content"], encoding="utf-8")

            # Look up source
            source = db.query(Source).filter_by(name=doc_info["source_name"]).first()
            if not source:
                print(f"Warning: Source '{doc_info['source_name']}' not found, skipping...")
                continue

            doc = pipeline.ingest_file(
                filepath=filepath,
                source_id=str(source.id),
                category_slug=doc_info["category_slug"],
                title=doc_info["title"],
                source_url=doc_info["source_url"],
                publication_date=doc_info["publication_date"],
                last_updated=doc_info["last_updated"],
            )
            print(f"Ingested: {doc.title} -> {len(doc.chunks)} chunks")

        # Rebuild retrieval index
        idx_mgr = IndexManager.get_instance()
        idx_res = idx_mgr.rebuild_indexes(db)
        print(f"\nRetrieval index built successfully! Active chunks: {idx_res['chunk_count']}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_corpus()
