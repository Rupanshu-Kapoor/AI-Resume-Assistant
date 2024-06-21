# python file to parse different section from resume
from pdfminer.high_level import extract_text
from flask import jsonify
import re, fitz, requests, logging  
from config import data_science_skills, keyword_variations, essential_skills, quality_mapping
from config import required_sections, linkedin_domain, github_domain, basic_informations
from spacy.matcher import Matcher
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')


class ResumeParser:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path):
        return extract_text(pdf_path)
    
    def extract_contact_number_from_resume(self, text):
        contact_number = None
        suggestion = ""

        # Use regex pattern to find a potential contact number
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()
            # Check if the contact number is of the correct length
            digits_only = re.sub(r'\D', '', contact_number)
            if len(digits_only) == 10:
                suggestion = ""
            elif len(digits_only) > 10 and digits_only.startswith('91') and len(digits_only[2:]) == 10:
                suggestion = ""
            else:
                suggestion = "Contact number should have exactly 10 digits."
        
        return contact_number, suggestion
    
    def extract_email_from_resume(self, text):
        email = None
        suggestion = ""

        # Use regex pattern to find a potential email address
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            email = match.group()
            # Additional validation
            if not self.is_valid_email(email):
                suggestion += "your email address doesn't seem to be valid. Please check and correct."
        return email, suggestion
    
    def is_valid_email(self, email):
        # Length check
        if len(email) > 254:
            return False
        
        # Consecutive special characters check
        if re.search(r"[._%+-]{2,}", email):
            return False
        
        # Domain part validation
        domain_part = email.split('@')[1]
        if not re.match(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", domain_part):
            return False
        return True
    
    def extract_sections_from_resume(self, text):
        sections = []

        for section in required_sections:
            pattern = r"\b{}\b".format(re.escape(section))
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                sections.append(section)
        return sections
    
    def extract_skills_from_resume(self, text):
        skills = []

        for skill in essential_skills:
            pattern = r"\b{}\b".format(re.escape(skill))
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills.append(skill) 
        return skills
    
    def extract_keyword_variations_from_resume(self, text):
        found_keywords = []
        for keyword, variations in keyword_variations.items():
            for variation in variations:
                if variation.lower() in (text.lower()):  # Convert both variation and text to lowercase
                    found_keywords.append(keyword)
                    break  # Once a keyword is found, no need to check its other variations

        return found_keywords
    
    def extract_linkedIn_urls_from_pdf(self, pdf_path):
        linkedin_urls = None
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            links = page.get_links()
            for link in links:
                url = link.get('uri', '')
                if re.search(linkedin_domain, url):
                    linkedin_urls = url
        pdf_document.close()
        return linkedin_urls

    def extract_github_urls_from_pdf(self, pdf_path):
        github_urls = None
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            links = page.get_links()
            for link in links:
                url = link.get('uri', '')
                if re.search(github_domain, url):
                    github_urls = url
        pdf_document.close()
        
        return github_urls   
    
    def is_valid_name(self, name):
        if any(char.isdigit() for char in name):
            return False
        if len(name.split()) > 3: 
            return False
        common_non_names = {"Email", "Github", "LinkedIn", "Portfolio", "Data Analyst"}
        if name in common_non_names:
            return False
        return True
          
    def extract_name(self, resume_text):
        
        lines = resume_text.split('\n')
                
        # Use regex to find lines that likely contain names
        name_lines = [line for line in lines if re.match(r'^[A-Za-z]*\s[A-Za-z]*$', line.strip())]

        names = []
        for i in range(len(name_lines)):
            if self.is_valid_name(name_lines[i].strip()):
                names.append(name_lines[i].strip())
                
        if len(names) >= 1:
            name = names[0]
            suggestion = ""
            # Check if the name parts contain only alphabetic characters
            name_parts = name.split()
            if not all(part.replace("-", "").replace("'", "").isalpha() for part in name_parts):
                suggestion += "Name should contain only English alphabets. "
            elif any(part[0].islower() for part in name_parts) or any(part[1:].isupper() for part in name_parts):
                suggestion += "Each name part should start with a capital letter. "
            return name, suggestion

        return None, "No valid name found"
 
    
    def check_missing_sections(self, resume_data):
        missing_information = []
        for section in basic_informations:
            if not resume_data.get(section):
                missing_information.append(section)
        return missing_information
    
    def grammar_check(self, parsed_resume):
        text = parsed_resume["new_text"]
        matches = tool.check(text)
        corrected_text = tool.correct(text)
        grammar_issues = []
        for match in matches:
            issue = {
                "error": match.message,
                "suggested_correction": match.replacements,
                "context": match.context,
                "rule_id": match.ruleId
            }
            grammar_issues.append(issue)
            grammar_result = {
            "original_text": text,
            "grammar_issues": grammar_issues,
            "corrected_text": corrected_text
            }

        return grammar_result
            
    def parse_text(self, path):
        logger = logging.getLogger(__name__)
        resume_data = {}
        logger.debug('parsing text')
        text = self.extract_text_from_pdf(path)
        text1 = " ".join(text.split("\n"))
        skills_found = self.extract_skills_from_resume(text)
        found_keywords = self.extract_keyword_variations_from_resume(text)
        
        name, name_suggestion = self.extract_name(text)
        contact_number, contact_suggestion = self.extract_contact_number_from_resume(text)

        email, email_suggestion = self.extract_email_from_resume(text)

        suggestions = name_suggestion + contact_suggestion + email_suggestion 
        # Adding suggestion if name, contact number, and email are not found
        if not name:
            suggestions += "Please add  name to the resume. "
        if not contact_number:
            suggestions += "Please add the contact number to the resume. "
        if not email:
            suggestions += "Please add the email address to the resume. "

        resume_data = {
            "name": name,
            "info_suggestion":suggestions,
            "contact_number": contact_number,
            "email": email,
            "linkedin_urls": self.extract_linkedIn_urls_from_pdf(path),
            "github_urls": self.extract_github_urls_from_pdf(path),            
            "skills": skills_found,
            "found_keywords": found_keywords,
            "text": text,
            "new_text": text1
        }
        resume_data["text"] = [text]
        
        missing_important_sections = self.check_missing_sections(resume_data)
        resume_data["basic_information_section"] = missing_important_sections

        if not resume_data["basic_information_section"]:
            resume_data["basic_information_section"] = "Basic information is Found"
        else:
            resume_data["basic_information_section"] = "Basic information is missing: " + ", ".join(list(missing_important_sections))

        # create list of skills that are present in essesnial_skills but not in skills_found
        missing_skills = list(set(essential_skills) - set(skills_found))
        resume_data["missing_skills"] = missing_skills

        found_keywords = len(resume_data["found_keywords"])
        num_keywords = len(keyword_variations)
        
        for quality, threshold in quality_mapping.items():
            if found_keywords < num_keywords * threshold:
                resume_data["quality"] = quality
                break

        resume_data["missing_sections"] = self.extract_sections_from_resume(text)

        grammar_check_result = self.grammar_check(resume_data)
        resume_data["grammar_check_result"] = grammar_check_result
        return jsonify(resume_data)
    
