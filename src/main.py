import os
from flask import Flask, jsonify, request, flash, redirect, url_for
from submitter import ResumeSubmitter
from reviewer import ResumeReviewer
from resume_parser import ResumeParser
from logging_config import setup_logging

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
app.secret_key = 'supersecretkey'
setup_logging()

@app.route('/v1/resumes/', methods=['POST', 'GET'])
def submit_resume():
    if request.method == 'POST':
        result = ResumeSubmitter().upload_file()
        if result:
            resume_path = result  # Get the path of the uploaded resume
            try:
                # Redirect to the /v1/reviews/ endpoint with the resume path as a parameter
                return redirect(url_for('get_reviews', path=resume_path))
            except Exception as e:
                app.logger.error("Failed to redirect to /v1/reviews/: %s", str(e))
                return jsonify(message="failed to redirect to reviews page"), 500
        else:
            return jsonify(message="failed to submit resume"), 400
    else:
        return ResumeSubmitter().upload_form()

@app.route("/v1/reviews/<path:path>", methods=['POST', 'GET'])
def get_reviews(path):
    app.logger.debug("Inside get_reviews")
    resume_parser = ResumeParser()
    resume_reviewer = ResumeReviewer()
    parsed_resume = resume_parser.parse_text(path)
    if parsed_resume:
        reviews = resume_reviewer.grammar_check(parsed_resume)
    return jsonify(message="reviews retrieved successfully for resume at path: {}".format(parsed_resume))


@app.route("/v1/users/<int:id>", methods=['GET'])
def get_user(id):
    return jsonify(message="user retrieved successfully! for given id {}".format(id))

@app.route('/', methods=['GET'])
def greet():
    return jsonify(message="Home Page!")

if __name__ == '__main__':
    app.run(debug=True)
