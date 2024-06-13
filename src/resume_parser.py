# python file to parse different section from resume
from pdfminer.high_level import extract_text
import re
from config import data_science_skills , keyword_variations, essential_skills, quality_mapping 
import spacy
from spacy.matcher import Matcher
import logging


class ResumeParser:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path):
        return extract_text(pdf_path)
    
    def extract_contact_number_from_resume(self, text):
        contact_number = None

        # Use regex pattern to find a potential contact number
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()

        return contact_number
    
    def extract_email_from_resume(self, text):
        email = None

        # Use regex pattern to find a potential email address
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            email = match.group()

        return email
    
    def extract_skills_from_resume(self, text):
        skills = []

        for skill in data_science_skills:
            pattern = r"\b{}\b".format(re.escape(skill))
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills.append(skill) 

        found_keywords = []
        for keyword, variations in keyword_variations.items():
            for variation in variations:
                if variation.lower() in map(str.lower, skills):  # Convert both variation and skills to lowercase
                    found_keywords.append(keyword)
                    break  # Once a keyword is found, no need to check its other variations

        return skills, found_keywords


            
    def extract_name(self, resume_text):
        nlp = spacy.load('en_core_web_sm')
        matcher = Matcher(nlp.vocab)

        # Define name patterns
        patterns = [
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First name, Middle name, Middle name, and Last name
            # Add more patterns as needed
        ]

        for pattern in patterns:
            matcher.add('NAME', patterns=[pattern])

        doc = nlp(resume_text)
        matches = matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]
            return span.text

        return None
    
    
    def parse_text(self, path):
        logger = logging.getLogger(__name__)
        resume_data = {}
        logger.debug('parsing text')
        text = self.extract_text_from_pdf(path)
        logger.debug("extracting contact number")
        resume_data["contact_number"] = self.extract_contact_number_from_resume(text)
        logger.debug("extracting email")
        resume_data["email"] = self.extract_email_from_resume(text)
        skills , found_keywords = self.extract_skills_from_resume(text)  
        resume_data["skills"] = skills    
        resume_data["found_keywords"] = found_keywords  
        resume_data["text"] = text
        
        found_keywords = len(resume_data["found_keywords"])  
        num_keywords = len(keyword_variations)
        
        for quality, threshold in quality_mapping.items():
            if found_keywords < num_keywords * threshold:
                resume_data["quality"] = quality
                break

        return resume_data