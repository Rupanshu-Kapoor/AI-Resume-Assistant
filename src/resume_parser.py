# python file to parse different section from resume
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal
from collections import defaultdict
from flask import jsonify
import re, fitz, requests, logging, datetime
from config import data_science_skills, keyword_variations, essential_skills, quality_mapping, Extract_sections, suggested_projects
from config import required_sections, linkedin_domain, github_domain, basic_informations, section_headers, common_projects
from spacy.matcher import Matcher
import language_tool_python
tool = language_tool_python.LanguageTool('en-US')



class ResumeParser:
    
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
        
    def segregate_sections(self, text__):
        header_pattern = re.compile(rf'^\s*({"|".join(re.escape(header) for header in section_headers)}):?\s*$', re.IGNORECASE)
        sections_text = {}
        current_section = None
        lines = text__.splitlines()
        for line in lines:
            clean_line = line.strip()
            match = header_pattern.match(clean_line)
            if match:
                current_section = match.group(1).upper()
                sections_text[current_section] = []
            elif current_section:
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
    
    def normalize_font_name(self,font_name):
        if '-' in font_name:
            font_name = font_name.split('-')[0]
        if '+' in font_name:
            font_name = font_name.split('+')[1]
        return font_name

    
    def extract_text_properties(self, pdf_path, predefined_terms):
        text_properties = []
        current_phrase = ""
        current_font_size = None
        current_font_name = None
        current_page_num = None

        special_characters = set("●▪•!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

        def add_current_phrase():
            nonlocal current_phrase
            if current_phrase.strip():
                flag = any(current_phrase in term for term in predefined_terms)
                if not flag:
                    text_properties.append({
                        "text": current_phrase,
                        "font_size": current_font_size,
                        "font_name": current_font_name,
                        "page_num": current_page_num
                    })
                current_phrase = ""

        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLineHorizontal):
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    text = character.get_text()
                                    font_size = round(character.size, 2)
                                    font_name = self.normalize_font_name(character.fontname)
                                    page_num = page_layout.pageid

                                    if text.isspace() or text in special_characters:
                                        add_current_phrase()
                                        continue

                                    if (font_size != current_font_size or font_name != current_font_name or
                                        page_num != current_page_num):
                                        add_current_phrase()
                                        current_font_size = font_size
                                        current_font_name = font_name
                                        current_page_num = page_num

                                    current_phrase += text

                            add_current_phrase()

        return text_properties
    
    def group_similar_fonts(self,text_properties, tolerance=0.5):
        grouped_properties = defaultdict(list)
        
        for prop in text_properties:
            rounded_size = round(prop["font_size"] / tolerance) * tolerance
            key = (prop["font_name"], rounded_size)
            grouped_properties[key].append(prop)

        return grouped_properties
    



    def identify_different_fonts_and_sizes(self, grouped_properties):
        most_common_group = max(grouped_properties.values(), key=len)
        most_common_key = None
        for key, group in grouped_properties.items():
            if group == most_common_group:
                most_common_key = key
                break

        different_texts = []

        for key, group in grouped_properties.items():
            if group != most_common_group:
                for prop in group:
                    reason = []
                    if key[1] != most_common_key[1]:
                        reason.append(f"size not {most_common_key[1]}")
                    if key[0] != most_common_key[0]:
                        reason.append(f"font not {most_common_key[0]}")
                    different_texts.append({
                        "page_num": prop['page_num'],
                        "text": prop['text'],
                        "found_size": prop['font_size'],
                        "found_font_name": prop['font_name'],
                        "reason": ", ".join(reason)
                    })

        return different_texts
    
    def parse_education_dates(self, sections_text):
        # Check if the 'ACADEMIC PROFILE' section is in the text
        if 'ACADEMIC PROFILE' not in sections_text:
            return "ACADEMIC PROFILE section is not here."
        
        # Define the date patterns to match various date formats
        date_pattern = (
            r'\b\d{1,2}/\d{4}\b|'  # MM/YYYY
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4}\b|'  # Month YYYY
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2},?\s*\d{4}\b|'  # Month DD, YYYY
            r'\b\d{4}\b|'  # YYYY
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[a-z]*/?\d{4}\b|'  # Month/YYYY
            r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[a-z]*\d{4}\s*-\s*(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[a-z]*\d{4}\b'  # Month/YYYY - Month/YYYY
        )

        all_dates = []

        # Iterate over the entries in the EDUCATION section
        for entry in sections_text['ACADEMIC PROFILE']:
            entry = entry.lower()
            matches = re.findall(date_pattern, entry)
            if matches:
                if len(matches) == 2:
                    all_dates.append(f"{matches[0]} {matches[1]}")
                else:
                    all_dates.extend(matches)

        return all_dates


    def convert_to_date(self, date_str):
        # Mapping of month names and abbreviations to their numeric equivalents
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
            'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
            'may': 5, 'jun': 6, 'june': 6, 'jul': 7,
            'july': 7, 'aug': 8, 'august': 8, 'sep': 9,
            'september': 9, 'oct': 10, 'october': 10,
            'nov': 11, 'november': 11, 'dec': 12, 'december': 12,
            '01': 1, '02': 2, '03': 3, '04': 4,
            '05': 5, '06': 6, '07': 7, '08': 8,
            '09': 9, '10': 10, '11': 11, '12': 12
        }

        # Regex patterns to match different date formats
        pattern_mm_yyyy = re.compile(r'(\d{1,2})/(\d{4})')
        pattern_mm_yyyy_space = re.compile(r'(\d{1,2})\s(\d{4})')
        pattern_month_yyyy = re.compile(r'([a-zA-Z]+)\s?(\d{4})')
        pattern_yyyy = re.compile(r'(\d{4})')

        def extract_date(date_str):
            match_mm_yyyy = pattern_mm_yyyy.match(date_str)
            match_mm_yyyy_space = pattern_mm_yyyy_space.match(date_str)
            match_month_yyyy = pattern_month_yyyy.match(date_str)
            match_yyyy = pattern_yyyy.match(date_str)

            if match_mm_yyyy:
                month = int(match_mm_yyyy.group(1))
                year = int(match_mm_yyyy.group(2))
            elif match_mm_yyyy_space:
                month = int(match_mm_yyyy_space.group(1))
                year = int(match_mm_yyyy_space.group(2))
            elif match_month_yyyy:
                month = month_map.get(match_month_yyyy.group(1).lower())
                year = int(match_month_yyyy.group(2))
            elif match_yyyy:
                month = 1
                year = int(match_yyyy.group(1))
            else:
                print("Invalid date format")

            return datetime.date(year, month, 1)

        date_parts = re.findall(r'[a-zA-Z]+\s?\d{4}|\d{1,2}/\d{4}|\d{1,2}\s?\d{4}|\d{4}', date_str)
        
        if len(date_parts) == 1:
            # Standalone year or single date
            start_date = extract_date(date_parts[0])
            end_date = datetime.date(start_date.year, 12, 31)
        elif len(date_parts) == 2:
            # Date range
            start_date = extract_date(date_parts[0])
            end_date = extract_date(date_parts[1])
        else:
            print("Invalid date format")

        return start_date, end_date


    def date_time(self, date_parts):
        converted_dates = []
        for date_part in date_parts:
                start_date, end_date = self.convert_to_date(date_part)
                converted_dates.append((start_date, end_date))
        return converted_dates  
    

    def check_chronological_order(self, converted_dates):
        suggestion = ""
        sorted_dates = sorted(converted_dates, key=lambda x: (x[1], x[0]), reverse=True)
        if converted_dates == sorted_dates:
            suggestion = "ACADEMIC PROFILE section is in chronological order."
        else:
            suggestion = "ACADEMIC PROFILE section is not in chronological order."

        return suggestion
    
    def check_common_projects(self, projects_text):
        found_projects = []
        for project in common_projects:
            if project.lower() in projects_text.lower():
                found_projects.append(project)
        return found_projects
    
    def check_imarticus_certifications(self, certifications_text):
        if "imarticus" in certifications_text.lower():
            return True
        return False




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
        
        

        parsed_sections = self.segregate_sections(text)
        projects = parsed_sections.get("PROJECTS", [])
        certifications = parsed_sections.get("CERTIFICATIONS & ACADEMIC ENDEAVOURS", [])
        projects_text = "\n".join(projects)
        certifications_text = "\n".join(certifications)
        found_imarticus_certification = self.check_imarticus_certifications(certifications_text)
        found_projects = self.check_common_projects(projects_text)

        
        name, name_suggestion = self.extract_name(text)
        contact_number, contact_suggestion = self.extract_contact_number_from_resume(text)
        email, email_suggestion = self.extract_email_from_resume(path)
        github_urls =  self.extract_github_urls_from_pdf(path)     
        github_urls_suggestions = self.is_valid_url(github_urls)
        linkedin_urls =  self.extract_linkedIn_urls_from_pdf(path)
        section_by_grammer_issues = self.grammar_issue_check(text, found_keyword_section, Extract_sections)

        suggestions = name_suggestion + contact_suggestion + email_suggestion + github_urls_suggestions

        predefined_terms = [name, email]
        predefined_terms.extend(required_sections)
        text_properties = self.extract_text_properties(path, predefined_terms)
        grouped_properties = self.group_similar_fonts(text_properties)
        different_texts = self.identify_different_fonts_and_sizes(grouped_properties)
        
        
        date_parts = self.parse_education_dates(sections_text)
        converted_dates = self.date_time(date_parts) 
        education_order_suggestion = self.check_chronological_order(converted_dates) 

        font_suggestions = []
        for item in different_texts:
            suggeestion = f"""Formatting issue at Page: {item['page_num']}, Text: {item['text']}, Reason: {item['reason']},
                Found font size: {item['found_size']}, Found font name: {item['found_font_name']}"""
            font_suggestions.append(suggeestion)

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
            # "date_parts": date_parts,
            # "converted_dates" : converted_dates,
            "education_order_suggestion": education_order_suggestion,
            "grammer_issues_by_section": section_by_grammer_issues,
            "github_urls": github_urls,            
            "skills": skills_found,
            "found_keywords": found_keywords,
            "text": text,
            "new_text": text1,
            "font_suggestions": font_suggestions
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
            
        if found_projects:
            common_project = "Common projects found in Projects section: "
            for project in found_projects:
                common_project += project 
        resume_data["common_projects"] = common_project 
            
        if found_imarticus_certification:
            found_certification =  "Imarticus certification found in Certifications section."
        else:
            found_certification = "No Imarticus certification found in Certifications section."

        resume_data["found_certification"] = found_certification       

        return jsonify(resume_data)
    