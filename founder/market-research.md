# Market research notes (web search, 17 Nov 2026)

Quick scan, not the full /founder-competitors run. Prices from vendor pages and blogs are indicative; get quotes before relying on them.

## Who already does this

| Player | What it is | Who pays | Price (indicative) | Integrations |
|---|---|---|---|---|
| Ex Libris campusM | White-label campus app + web portal; homepage "live tiles" | University | Quote-based | Outlook 365 via Microsoft Graph, Canvas, Moodle, Blackboard, Brightspace, Banner, Gmail, library systems |
| Ellucian Experience | Student/staff dashboard on top of Ellucian ERP (Banner/Colleague) | University (Ellucian customers) | Foundation tier free to Ellucian customers; Premium quote-based | Ellucian ERP, SDK for custom cards |
| Modern Campus, Ready Education | US campus app / engagement platforms | University | Quote-based (not found) | SIS, LMS, events |
| Canvas Student / Moodle app / Teams | LMS apps: courses, assignments, grades, materials | University | Canvas ~$5-30 per student per year (estimates); Moodle free + hosting; Teams included with Microsoft Education | Own LMS only |
| Indian college ERPs (MasterSoft, Academia/Serosoft, Camu, Linways, Fedena, Tazk...) | Admin + student portal/app: attendance, marks, fees, timetable | College | ₹300-1,200 per student per year (university guide); ₹10-100 per student per month range quoted; Tazk flat ₹69,990/yr up to 2,500 students; MasterSoft from ₹5 lakh | Own ERP |
| Samarth eGov (Ministry of Education) | Government ERP with student portal (results, admit cards, date sheets, fees) | Government | Free to at least some institutions (Panjab University); 2,800 to 5,400+ institutions reported | Own suite (40+ modules) |
| Praksha (India) | Free student app: attendance, timetable, internships, campus events | Free to students | Free | Manual / own data |
| Consumer planners (Power Planner, MyStudyLife etc.) | Student self-entered planners: assignments, GPA, schedule | Student (freemium) | Free / small subscription | Mostly manual entry, calendar sync |

## Hard facts that shape the business

- **Microsoft access needs the university.** Reading a student's university Outlook through Microsoft Graph often needs tenant admin consent, and tenants can block user consent entirely. campusM itself requires the institution to configure Graph permissions. So the B2C "student signs up alone" route breaks at many universities.
- **Marks and CGPA live in the college ERP or Samarth**, which generally has no public API for third parties. Getting that data means a partnership with the college or the ERP vendor.
- **DPDP Act 2023 / Rules 2025:** the university is the data fiduciary; vendors need DPDP-aligned contracts; under-18 students need verifiable parental consent (first-years can be 17); full enforcement around May 2027.
- **Government colleges** increasingly run Samarth, which is free; they buy through tenders and GeM, slowly.

## Sources
- campusM Outlook 365 integration: https://knowledge.exlibrisgroup.com/campusM/Product_Documentation/Product_Integrations/Email/Outlook_365
- campusM LMS integrations: https://campusm.exlibrisgroup.com/academic-services/
- campusM at Univ. of Southern Mississippi: https://exlibrisgroup.com/press-release/ex-libris-campusm-mobile-app-and-web-portal-now-live-at-the-university-of-southern-mississippi/
- Ellucian Experience tier sheet: https://www.ellucian.com/assets/en/ellucian-experience-tier-sheet.pdf
- Canvas pricing estimates: https://www.wooclap.com/en/blog/canvas-lms-pricing/
- Indian university ERP cost: https://www.optatechinnovation.com/blog/university-erp-software-cost-india
- College management software India: https://tazk.in/college-management-software
- Samarth: https://samarth.edu.in/about/ , https://samarth.edu.in/panjab-university-adopts-samarth-portal-for-data-management/
- Praksha: https://www.praksha.app/
- Microsoft admin consent: https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/app-integration/troubleshoot-consent-issues
- DPDP and higher education: https://campx.in/xpress/articles/dpdp-privacy-reset-higher-education , https://ssrana.in/articles/schools-coaching-centres-platforms-processing-childrens-data-are-you-compliant/
