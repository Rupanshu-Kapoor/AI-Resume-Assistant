import language_tool_python, json, re, logging
from flask import jsonify
tool = language_tool_python.LanguageTool('en-US')
# from pdfminer.high_level import extract_text


class ResumeReviewer:
    def __init__(self):
        pass

    def review(self):
        pass

    def grammar_check(self, parsed_resume):
        text = parsed_resume["text"]
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

        return jsonify(grammar_result)
            




            
