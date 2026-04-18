def calculate_ats_score(seeker, job_post):
    """
    Calculates ATS score for an applicant out of 100.

    Formula:
    - CGPA component (40 points max): seeker's CGPA / 4.0 * 40
    - Skill match component (60 points max): matched skills / required skills * 60

    Example:
    - Seeker has CGPA 3.5 → CGPA component = 3.5 / 4.0 * 40 = 35
    - Seeker has skills "Python, Django, SQL"
    - Job requires "Python, Django, React, SQL" (4 skills)
    - Matched skills = 3 (Python, Django, SQL)
    - Skill component = 3 / 4 * 60 = 45
    - Total ATS score = 35 + 45 = 80
    """

    # ===== CGPA COMPONENT (max 40 points) =====
    cgpa_score = 0
    if seeker.cgpa:
        # Assume CGPA is out of 4.0
        cgpa_score = (seeker.cgpa / 4.0) * 40

    # ===== SKILL MATCH COMPONENT (max 60 points) =====
    skill_score = 0

    # Get the seeker's skills and job's required skills
    seeker_skills_text = seeker.skills_text or ''
    job_skills_text = job_post.skills_text or ''

    # Split skills by comma, strip whitespace, convert to lowercase
    seeker_skills = [s.strip().lower() for s in seeker_skills_text.split(',') if s.strip()]
    job_skills = [s.strip().lower() for s in job_skills_text.split(',') if s.strip()]

    # If job has required skills, calculate match percentage
    if job_skills:
        # Find how many of the job's required skills the seeker has
        matched = [s for s in job_skills if s in seeker_skills]
        skill_score = (len(matched) / len(job_skills)) * 60
    else:
        # If job has no skills listed, give full skill points
        skill_score = 60

    # ===== TOTAL SCORE =====
    total_score = cgpa_score + skill_score

    # Round to 2 decimal places and cap at 100
    total_score = round(min(total_score, 100), 2)

    return total_score
