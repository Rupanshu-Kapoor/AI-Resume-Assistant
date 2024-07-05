# python file to parse different section from resume
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal
from collections import defaultdict
from flask import jsonify
import re, fitz, requests, logging  
from config import data_science_skills, keyword_variations, essential_skills, quality_mapping, Extract_sections
from config import required_sections, linkedin_domain, github_domain, basic_informations, section_headers
from spacy.matcher import Matcher
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')



class ResumeParser:
    def __init__(self):
        pass

    # def extract_text_from_pdf(self, pdf_path):
    #     return extract_text(pdf_path)
    
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
    


    def extract_hyperlinks(self, pdf_path):
        doc = fitz.open(pdf_path)
        links = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            link_list = page.get_links()
            for link in link_list:
                uri = link.get('uri', None)
                if uri:
                    links.append(uri)

        return links

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    
    def extract_email_from_text(self, text):
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            return match.group()
        return None

    def extract_email_from_resume(self, pdf_path):
        text = self.extract_text_from_pdf(pdf_path)
        email = self.extract_email_from_text(text)
        suggestion = ""

        # If no email found in text, check hyperlinks
        if not email:
            links = self.extract_hyperlinks(pdf_path)
            for link in links:
                if link.startswith('mailto:'):
                    email_candidate = link.split('mailto:')[1]
                    if self.is_valid_email(email_candidate):
                        email = email_candidate
                        break

        # Additional validation for email found in text or links
        if email and not self.is_valid_email(email):
            suggestion += "Your email address doesn't seem to be valid. Please check and correct."

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
        
        # Standard email format check
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match(pattern, email) is not None
    
    
    def extract_sections_from_resume(self, text):
        missing_sections = []
        sections_not_capitalized = []

        for section in required_sections:
            pattern = r"\b{}\b".format(re.escape(section))

            match_obj = re.search(pattern, text, re.IGNORECASE)
            if not match_obj:
                missing_sections.append(section)
            else:
                if match_obj.group() not in map(str.upper, required_sections):
                    sections_not_capitalized.append(section)

        return missing_sections, sections_not_capitalized
    
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
                if variation.lower() in text.lower(): 
                    found_keywords.append(variation)
                    break  

        return found_keywords
    
    def extract_keyword_variations_from_formatted_text(self, formatted_text):
        found_keyword_section = []
        for keyword, variations in keyword_variations.items():
            for variation in variations:
                if variation.lower() in formatted_text.lower(): 
                    found_keyword_section.append(variation)
                    break  

        return found_keyword_section
    
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
                    path = re.sub(github_domain, '', url)
                    parts = path.split('/')
                    if len(parts) == 1: 
                        github_urls = url
        pdf_document.close()
        return github_urls 
    
    def is_valid_url(self , github_urls ):
        suggest = ""
        for _ in [github_urls]:  
            if not github_urls:
                break
                                    
            try:
                response = requests.head(github_urls)
                if response.status_code != 200:
                    suggest = "GitHub URL is not valid, please check and correct. "
            except requests.RequestException:
                    suggest = "GitHub URL is not valid, please check and correct. "
                       
            return suggest
        return suggest        
        

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
        name_lines = [line for line in lines if re.match(r'^[A-Za-z]*\s[A-Za-z]*', line.strip())]

        names = []
        for i in range(len(name_lines)):
            if self.is_valid_name(name_lines[i].strip()):
                names.append(name_lines[i].strip())
                
        if len(names) >= 1:
            name = names[0]
            suggestion = ""
            # Check if the name parts contain only alphabetic characters
            name_parts = name.split()
            if any(part[0].islower() for part in name_parts):
                suggestion += " name should start with a capital letter. "
            return name, suggestion

        return None, "No valid name found"
 
    
    def check_missing_sections(self, resume_data):
        missing_information = []
        for section in basic_informations:
            if not resume_data.get(section):
                missing_information.append(section)
        return missing_information
        
    def segregate_sections(self,text__):
        sections_text = {}
        current_section = None
        lines = text__.splitlines()
        for line in lines:
            clean_line = line.strip().upper()
            if clean_line in section_headers:
                current_section = clean_line
                sections_text[current_section] = []
            elif current_section:
                if clean_line not in section_headers:
                    sections_text[current_section].append(line.strip())
        return sections_text
        
    def extract_and_format_sections(self, sections_text, Extract_sections):
        formatted_text = ""
        for section in Extract_sections:
            if section in sections_text:
                section_content = " ".join(sections_text[section]).replace('\n', ' ')
                formatted_text += f"{section}:\n{section_content}\n\n"
        return formatted_text
    
    def replace_keywords_with_placeholders(self, formatted_text, found_keyword_section):
        placeholder_text = formatted_text
        keyword_placeholders = {}
        
        for i, keyword in enumerate(found_keyword_section):
            placeholder = f"{{KEYWORD_{i}}}"
            keyword_placeholders[placeholder] = keyword
            placeholder_text = re.sub(r'\b' + re.escape(keyword) + r'\b', placeholder, placeholder_text)
            
        return placeholder_text, keyword_placeholders
    
    def replace_placeholders_with_keywords(self, placeholder_text, keyword_placeholders):
        for placeholder, keyword in keyword_placeholders.items():
            placeholder_text = placeholder_text.replace(placeholder, keyword)
        return placeholder_text

    def grammar_check(self, placeholder_text):
        matches = tool.check(placeholder_text)
        grammar_issues = []
        for match in matches:
            issue = {
                "context": match.context, 
                "error": match.message,
                "rule_id": match.ruleId,
                "suggested_correction": match.replacements
            }
            grammar_issues.append(issue)
        return grammar_issues
    
    def process_resume(self, text, found_keyword_section, Extract_sections):
        sections_text = self.segregate_sections(text)
        formatted_text = self.extract_and_format_sections(sections_text, Extract_sections)
        placeholder_text, keyword_placeholders = self.replace_keywords_with_placeholders(formatted_text, found_keyword_section)
        placeholder_text = self.replace_placeholders_with_keywords(placeholder_text, keyword_placeholders)
        grammar_issues = self.grammar_check(placeholder_text)
        return grammar_issues
    
    def grammar_issue_check(self, text, found_keyword_section, Extract_sections):
        issues = {}
        for section in Extract_sections:
            grammar_issues = self.process_resume(text, found_keyword_section, [section])
            if not grammar_issues:
                grammar_issues = "no error found"
            issues[section] = grammar_issues
        return issues
    
    def parse_text(self, path):
        logger = logging.getLogger(__name__)
        resume_data = {}
        logger.debug('parsing text')
        text = self.extract_text_from_pdf(path)
        text1 = " ".join(text.split("\n"))
        skills_found = self.extract_skills_from_resume(text)
        found_keywords = self.extract_keyword_variations_from_resume(text)
        sections_text = self.segregate_sections(text)
        formatted_text = self.extract_and_format_sections(sections_text, Extract_sections)
        found_keyword_section = self.extract_keyword_variations_from_formatted_text(formatted_text)
        
        name, name_suggestion = self.extract_name(text)
        contact_number, contact_suggestion = self.extract_contact_number_from_resume(text)
        email, email_suggestion = self.extract_email_from_resume(path)
        github_urls =  self.extract_github_urls_from_pdf(path)     
        github_urls_suggestions = self.is_valid_url(github_urls)
        linkedin_urls =  self.extract_linkedIn_urls_from_pdf(path)
        section_by_grammer_issues = self.grammar_issue_check(text, found_keyword_section, Extract_sections)

        suggestions = name_suggestion + contact_suggestion + email_suggestion + github_urls_suggestions

        # Adding suggestion if name, contact number, and email are not found
        if not name:
            suggestions += "Please add  name to the resume. "
        if not contact_number:
            suggestions += "Please add the contact number to the resume. "
        if not email:
            suggestions += "Please add the email address to the resume. "
        if not github_urls:
            suggestions += " add the github_urls to the resume. "        
        if not linkedin_urls:
            suggestions += " add the linkedin_urls to the resume. "                 


        resume_data = {
            "name": name,
            "info_suggestion":suggestions,
            "contact_number": contact_number,
            "email": email,
            "linkedin_urls": linkedin_urls,
            "grammer_issues_by_section": section_by_grammer_issues,
            "github_urls": github_urls,            
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

        missing_sections, sections_not_capitalized = self.extract_sections_from_resume(text)

        resume_data["missing_sections"] = missing_sections
        logger.debug("Section Not Capitalized",sections_not_capitalized)

        if sections_not_capitalized:
            resume_data["sections_not_capitalized"] = sections_not_capitalized

        return jsonify(resume_data)
    