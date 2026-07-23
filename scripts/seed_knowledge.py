"""
Seed script to populate the insurance_knowledge_base table with
comprehensive health insurance domain knowledge for the AI cold calling agent.

Usage: python scripts/seed_knowledge.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.rag_service import RAGService
from app.database import async_session

try:
    from app.models import KnowledgeBase
except ImportError:
    KnowledgeBase = None

KNOWLEDGE_DOCUMENTS = [
    {
        "title": "Introduction to Health Insurance in Pakistan",
        "content": """Salam! Health insurance ek aisi protection hai jo aap ko medical emergencies mein financial burden se bachati hai. Pakistan mein health insurance plans basic hospitalization se lekar comprehensive family floater plans tak available hain. Ye plans aap ke hospital ke kharche, doctor fees, medicines aur diagnostic tests ko cover karte hain. Aam taur par, insurance companies cashless treatment ki suwulat deti hain jin mein aap ko paise upfront nahi dene padte. Premiums aap ki umar, plan ki type aur coverage ke hisaab se muqarrar kiye jate hain. NCAI Insurance aap ki zarooraton ke mutabiq behtareen plans provide karta hai taake aap aur aap ka khandan medical emergencies mein suroo se mehfooz rahe.""",
        "metadata": {"category": "introduction", "topic": "overview"}
    },
    {
        "title": "Basic Hospitalization Plans (PKR 2,000/month)",
        "content": """Agar aap ek affordable plan dhundh rahe hain to basic hospitalization plans aap ke liye hain. Ye plans sirf PKR 2,000 per month ya us se bhi kam mein shuru hote hain. In plans mein room rent (general ward), doctor ke fees, nursing charges aur basic diagnostic tests ka coverage hota hai. Hospitalization ki hadd takreeban PKR 200,000 se 500,000 tak hoti hai. Ye un logon ke liye behtareen hain jo pehli dafa health insurance le rahe hain ya limited budget mein reh kar bhi apne aap ko medical emergencies se bachana chahte hain. Zyada tar companies 1 saal ke contract par ye plans provide karti hain jo har saal renew kiye ja sakte hain.""",
        "metadata": {"category": "plans", "topic": "basic_hospitalization", "price_range": "low"}
    },
    {
        "title": "Comprehensive Family Plans (PKR 15,000/month)",
        "content": """Comprehensive family plans un logo ke liye hain jo apne pure khandan ko ek hi plan mein cover karwana chahte hain. Ye plans PKR 15,000/month se shuru hote hain aur in mein shohar, biwi aur 2-4 bache shamil ho sakte hain. Coverage mein private room rent, surgery, ICU, diagnostics, outpatient consultation aur kuch plans mein maternity bhi included hoti hai. Sum insured usually PKR 500,000 se 2,000,000 tak hoti hai. Cashless facility 500+ network hospitals par available hai. Family floater plans ka ye faida hai ke poori family ek hi sum insured share karti hai, jis se ek patient ko zyada coverage mil sakta hai agar zaroorat ho.""",
        "metadata": {"category": "plans", "topic": "family_plans", "price_range": "medium"}
    },
    {
        "title": "Coverage Details: Hospitalization, Day-Care, Maternity",
        "content": """NCAI Insurance ke plans teen major cheezon ko cover karte hain. Pehla: Hospitalization — jab patient ko 24 ghante ya zyada hospital mein rehna ho, to room rent, nursing, surgeon fees, anesthesia, medicines aur lab tests sab kuch cover hota hai. Doosra: Day-care procedures — aaj kal kafi medical procedures mein patient ko zyada der hospital mein nahi rehna padta. Chemotherapy, dialysis, cataract surgery aur angiography jaisi day-care procedures bhi cover hoti hain. Teesra: Maternity — pregnancy se related expenses, delivery charges (normal aur C-section dono) aur newborn ki basic care bhi shamil hai. Maternity coverage ke liye usually 9-12 months ki waiting period hoti hai.""",
        "metadata": {"category": "coverage", "topic": "details", "subtopics": "hospitalization,daycare,maternity"}
    },
    {
        "title": "Pre-Existing Conditions Coverage (Waiting Period 1 Year)",
        "content": """Pre-existing conditions ka matlab hai koi bhi bimari jo insurance policy lene se pehle mojood ho. Diabetes, blood pressure, asthma, heart disease aur thyroid disorders aam pre-existing conditions hain. Pakistan mein SECP ke regulations ke mutabiq, health insurance companies pre-existing conditions ko cover kar sakti hain lekin is ke liye 1 saal ki waiting period hoti hai. Matlab aap ko policy lene ke 1 saal baad tak intezar karna hoga is se pehle ke ye conditions cover hona shuru ho. Kuch companies 4 saal ki waiting period bhi rakhti hain. Waiting period ke dauran agar in conditions ki wajah se admission hota hai to claim reject ho sakta hai, is liye policy lene se pehle waiting period ki sharton ko samajh lena zaroori hai.""",
        "metadata": {"category": "coverage", "topic": "pre_existing", "waiting_period": "1_year"}
    },
    {
        "title": "Cashless Claim Process at 500+ Hospitals",
        "content": """Cashless claim process NCAI Insurance ki sab se ahem suwulat hai. Jab aap ko hospital admission ki zaroorat hoti hai, to aap network hospital mein apna insurance card dikha kar admission le sakte hain bina koi payment kiye. Hospital direct insurance company se billing karti hai. Process aasan hai: pehle hospital ke insurance desk par apna card aur CNIC submit karein, phir insurance company authorization ke liye call karti hai, authorization milne ke baad admission proceed hota hai. 500+ hospitals Karachi, Lahore, Islamabad, Peshawar aur Quetta mein is service ka faida utha sakte hain. Emergency admissions mein 24-48 ghanton mein insurance company ko inform karna hota hai. Yeh suwulat aap ko financial tension se bachati hai.""",
        "metadata": {"category": "claims", "topic": "cashless", "network_size": "500+"}
    },
    {
        "title": "Network Hospitals in Major Cities",
        "content": """NCAI Insurance ka network 500+ hospitals par phaila hua hai jo Pakistan ke tamam major cities mein hain. Karachi mein Aga Khan Hospital, Liaquat National Hospital, South City Hospital aur Tabba Heart Institute shamil hain. Lahore mein Mayo Hospital, Services Hospital, Doctors Hospital aur Hameed Latif Hospital network ka hissa hain. Islamabad mein Shifa International, Kulsum International Hospital aur Islamabad Diagnostic Centre include hain. Peshawar mein Rehman Medical Institute aur Hayatabad Medical Complex hain. Quetta mein Bolan Medical Complex aur Fatima Jinnah Hospital bhi network mein hain. In hospitals par cashless treatment ki saholat hai. Naye hospitals regularly add hote hain, is liye nearest network hospital ke baare mein agent se zaroor poochh len.""",
        "metadata": {"category": "network", "topic": "hospitals_by_city", "cities": "karachi,lahore,islamabad,peshawar,quetta"}
    },
    {
        "title": "Maternity Coverage Details",
        "content": """Maternity coverage health insurance ka ek important hissa hai. NCAI Insurance ke family plans mein maternity coverage shamil ho sakta hai jo pregnancy-related expenses cover karta hai. Is mein antenatal check-ups, doctor fees, delivery charges (normal delivery PKR 50,000-80,000 aur C-section PKR 100,000-150,000 tak), aur postnatal care shamil hai. Newborn ki initial vaccination aur 30-90 din tak basic coverage bhi hoti hai. Lekin yaad rakhein: maternity coverage ke liye 9-12 maheeno ki waiting period hoti hai. Is ka matlab agar aap aaj policy lete hain to us ke 9-12 maheene baad hi maternity claims file kar sakte hain. Pehle se existing pregnancy cover nahi hoti. Family planning ke liye ye ek best investment hai.""",
        "metadata": {"category": "coverage", "topic": "maternity", "waiting_period": "9_12_months"}
    },
    {
        "title": "Emergency Ambulance Coverage",
        "content": """Health insurance plans mein emergency ambulance coverage bhi shamil hai jo aap ki jaan bacha sakti hai. Jab bhi koi medical emergency hoti hai — jaise heart attack, accident, ya sudden illness — to ambulance ki zaroorat parti hai. Ambulance coverage mein door se door tak patient ko hospital pohanchane ka kharja shamil hai. Aam taur par, plans ambulance ke kharche ko actual basis par cover karte hain, ya phir fixed limit set hoti hai (jaise PKR 3,000-5,000 per incident). Kuch premium plans mein air ambulance ka bhi coverage hota hai. Zyada tar insurance companies emergency ambulance ke liye 24/7 helpline provide karti hain. Is service ko activate karne ke liye toll-free number par call karna hota hai.""",
        "metadata": {"category": "coverage", "topic": "ambulance", "type": "emergency"}
    },
    {
        "title": "Health Insurance vs Takaful (Islamic Insurance)",
        "content": """Pakistan mein health insurance ke do systems hain: conventional insurance aur takaful (Islamic insurance). Conventional insurance mein aap premium pay karte hain aur company aap ke claims ko cover karti hai. Takaful ek Islamic alternative hai jo shariah principles par kaam karta hai. Is mein participants ek mutual fund mein paisa daalte hain aur claims is fund se pay kiye jate hain. Takaful operators fund ka management karte hain aur surplus (agar koi ho) to participants mein distribute kar dete hain. Takaful mein gharar (uncertainty) aur riba (interest) se bacha jaata hai. Bohat se log Karachi, Lahore aur Islamabad mein takaful ko prefer karte hain kyun ke ye unke religious beliefs ke saath consistent hai. NCAI Insurance dono options provide karta hai.""",
        "metadata": {"category": "comparison", "topic": "insurance_vs_takaful"}
    },
    {
        "title": "Tax Benefits on Health Insurance Premiums in Pakistan",
        "content": """Pakistan mein health insurance premiums par tax benefit milta hai jo aap ki savings barhata hai. Income Tax Ordinance 2001 ke Section 62 ke under, individual taxpayers health insurance premium par tax credit claim kar sakte hain. Aap apne taxable income se health insurance premium ki raqam deduct kar sakte hain, jo aap ki total tax liability ko kam kar deti hai. Maximum deduction PKR 50,000 per annum hai. Ye faida sirf registered insurance companies ke plans par applicable hai. Tax benefit lene ke liye aap ko premium payment ka receipt aur insurance certificate apne employer ya tax consultant ko dena hoga. Salaried individuals aur self-employed dono is benefit ke haqdaar hain. Yeh ek aur reason hai ke log health insurance kyun lete hain.""",
        "metadata": {"category": "benefits", "topic": "tax", "max_deduction": "PKR_50000"}
    },
    {
        "title": "How to File a Claim — Step by Step",
        "content": """Claim file karna aasan hai agar aap process ko samajh lein. Pehla qadam: jab aap hospital admission lein to insurance card aur CNIC sath rakhein. Cashless hospitals mein admission ke waqt insurance desk par card submit karein. Doosra qadam: insurance company admission ke 48 ghanton mein inform karein. Reimbursement claims ke liye (jahan aap ne khud paise diye) discharge ke 7 din mein claim form submit karein. Teesra qadam: saare documents jama karein — claim form, discharge summary, original bills, prescription, lab reports, aur insurance card copy. Choutha qadam: insurance company claim ka verification karti hai jo 7-15 working days mein complete hota hai. Paanchwa qadam: approval ke baad payment aap ke bank account mein transfer ho jati hai ya cashless case mein hospital ko direct pay hoti hai.""",
        "metadata": {"category": "claims", "topic": "process", "steps": "5"}
    },
    {
        "title": "Common Exclusions in Health Insurance",
        "content": """Health insurance mein kuch cheezen cover nahi hotin jinhe exclusions kehte hain. Aam exclusions mein shamil hain: pehle se existing diseases (waiting period ke dauran), cosmetic surgery, dental treatment (accident ke ilawa), weight loss surgery, infertility treatment, matlab: bachay paida karne ke treatment, self-inflicted injuries, aur war ya nuclear incidents se honay wale nuqsan. Kuch plans mein specific diseases ke liye alag se waiting period hoti hai, jaise cataract, hernia ya piles ke liye 1-2 saal. Nashe ki liye jane wali bimariyan (alcoholism, drug abuse) bhi cover nahi hotin. Outpatient prescription drugs (jo kuch plans mein shamil hain lekin zyada tar nahi) aur maternity (waiting period ke dauran) bhi exclusions mein hain. Policy lene se pehle exclusions ki list zaroor parh len.""",
        "metadata": {"category": "coverage", "topic": "exclusions"}
    },
    {
        "title": "Family Floater vs Individual Plans",
        "content": """Health insurance mein do options hain: family floater aur individual plans. Family floater plan mein poore khandan ke liye ek hi sum insured hoti hai, masalan PKR 1,000,000. Agar kisi ek ko bada claim ho to wo poori amount use kar sakta hai. Ye un families ke liye affordable hai jin mein ek saath multiple claims ka chance kam ho. Individual plans mein har member ki apni alag sum insured hoti hai. Is ka faida ye hai ke har person ka coverage separate hai aur koi doosra usay use nahi kar sakta. Lekin individual plans zyada mehngay hote hain. Family floater teeno bachon aur maan-baap ke liye economical option hai. Faisla karte waqt family ke medical history aur budget ko dhyan mein rakhna chahiye.""",
        "metadata": {"category": "comparison", "topic": "family_floater_vs_individual"}
    },
    {
        "title": "Top-Up Plans for Additional Coverage",
        "content": """Agar aap ke paas pehle se health insurance hai lekin aap zyada coverage chahte hain to top-up plans ek acha option hain. Top-up plan ek additional coverage hai jo aap ke existing plan ke upar lete hain. Is ka matlab hai ke jab aap ka pehla plan ki sum insured khatam ho jaye, to top-up plan ka coverage shuru hota hai. Masalan, agar aap ka base plan PKR 500,000 ka hai aur top-up plan PKR 1,000,000 ka hai, to pehle 500,000 base plan se pay hoga, phir agay 1,000,000 top-up se. Super top-up plans mein ye bhi hota hai ke agar ek claim mein pehli policy ka coverage exceed ho jaye to top-up kaam aata hai. Ye plans un logon ke liye hain jo existing coverage ko affordable tareeqay se barhana chahte hain bina naye full plan ki price pay kiye.""",
        "metadata": {"category": "plans", "topic": "top_up"}
    },
    {
        "title": "SECP Regulations for Health Insurance in Pakistan",
        "content": """Pakistan mein health insurance industry ko SECP (Securities and Exchange Commission of Pakistan) regulate karti hai. Insurance Ordinance 2000 ke under SECP tamam insurance companies ke operations ko monitor karti hai. Kuch important regulations hain: har policy mein 14 din ki free-look period hoti hai jismein aap policy cancel kar ke full refund le sakte hain. Pre-existing conditions ke liye maximum waiting period 4 saal hai. Companies ko policy ke terms aur conditions Urdu aur English dono mein provide karne hote hain. Grievance redressal mechanism har company ke paas hona zaroori hai. SECP ne recently health insurance ke liye standardized policy wordings bhi introduce ki hain. Companies ko registered hone ke liye minimum capital requirements poori karni parti hain aur time-to-time filings SECP ke saath submit karne hoti hain.""",
        "metadata": {"category": "regulations", "topic": "secp", "regulator": "SECP"}
    },
    {
        "title": "Comparison of Different Insurance Providers in Pakistan",
        "content": """Pakistan mein kai insurance companies health insurance provide karti hain. State Life Insurance aur EFU Life aam conventional insurance provide karte hain. Jubilee Life, IGI Life aur Adamjee Insurance bhi popular options hain. Takaful operators mein Pak-Qatar Family Takaful, Dawood Family Takaful aur TPL Takaful shamil hain. Har company ke premium rates, coverage options aur network hospitals mein farq hota hai. Masalan, State Life aur EFU Life ke premium zyada affordable hote hain lekin network hospitals limited hain. Jubilee Life ka network barha hai lekin premium thora zyada hai. NCAI Insurance sab se comprehensive coverage aur best customer service provide karta hai. Sahi company choose karne ke liye aap ko apni zarooraton, budget aur preferred hospitals ko dhyan mein rakhna chahiye.""",
        "metadata": {"category": "comparison", "topic": "provider_comparison"}
    },
    {
        "title": "How to Choose the Right Health Insurance Plan",
        "content": """Apne liye sahi health insurance plan select karna aasan hai agar aap kuch factors ko dhyan mein rakhein. Pehle: apni zarooraton ko samjhein — kya aap ko sirf basic hospitalization chahiye ya comprehensive family coverage? Doosre: budget decide karein — plans PKR 2,000/month se lekar PKR 30,000/month tak available hain. Teesre: sum insured ka size — aik aam operation mein PKR 200,000-500,000 lag sakta hai, is liye kam se kam PKR 500,000 ka coverage lein. Chauthe: network hospitals dekhein — check karein ke aap ke qareebi hospital network mein hai ya nahi. Paanchwe: maternity aur pre-existing conditions ke liye waiting periods ko samjhein. Chhatwe: policy ke exclusions aur claim settlement ratio ka pata karein. NCAI Insurance agent aap ki in sab cheezon mein madad kar sakta hai.""",
        "metadata": {"category": "guide", "topic": "choosing_plan"}
    },
]


async def main():
    rag_service = RAGService()
    total_chunks = 0

    print(f"Seeding {len(KNOWLEDGE_DOCUMENTS)} knowledge documents into the knowledge base...")
    print("=" * 60)

    for i, doc in enumerate(KNOWLEDGE_DOCUMENTS, 1):
        content = doc["content"].strip()
        metadata = doc.get("metadata", {})

        num_chunks = await rag_service.index_document(content, metadata)
        total_chunks += num_chunks

        print(f"[{i}/{len(KNOWLEDGE_DOCUMENTS)}] Indexed: {doc['title']} ({num_chunks} chunks)")

    print("=" * 60)
    print(f"Done! Successfully indexed {len(KNOWLEDGE_DOCUMENTS)} documents in {total_chunks} total chunks.")


if __name__ == "__main__":
    asyncio.run(main())
