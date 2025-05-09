from typing import Dict, List


class SchoolData:
    """Utility class to manage school information"""
    
    @staticmethod
    def get_schools_list() -> List[Dict]:
        """Returns the predefined list of schools"""
        return [
            {
                "name": "International School Manila",
                "link": "https://www.ismanila.org",
                "school_fee": "https://www.ismanila.org/admissions/school-fees",
                "program": [
                    "https://www.ismanila.org/elementary-school/academic-program",
                    "https://www.ismanila.org/middle-school/academic-program",
                    "https://www.ismanila.org/high-school/academic-program"
                ],
                "Enrollment Process and Requirements": [
                    "https://www.ismanila.org/admissions/admissions-process",
                    "https://www.ismanila.org/admissions/application-file-forms-requirements"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [
                    "https://www.ismanila.org/admissions/scholarships",
                ],
                "Contact Information ": [
                    "https://www.ismanila.org/contact-us"
                ]
            },
            {
                "name": "Brent International School",
                "link": "https://www.brent.edu.ph",
                "school_fee": [
                    "https://brent.edu.ph/wp-content/uploads/2024/02/school-fees-2024-2025.pdf",
                    "http://brent.edu.ph/wp-content/uploads/2025/02/school-fees-SY2025-2026-feb-19.pdf",
                ],
                "program": [
                    "https://brent.edu.ph/academics/early-learning-center/",
                    "https://brent.edu.ph/academics/lower-school/",
                    "https://brent.edu.ph/academics/middle-school/",
                    "https://brent.edu.ph/academics/high-school/",
                    "https://brent.edu.ph/academics/upper-school/",
                    "https://brent.edu.ph/academics/international-baccalaureate/",
                    "https://brent.edu.ph/academics/esl/",
                ],
                "Enrollment Process and Requirements": [
                    "https://brent.edu.ph/admissions/application-process/",
                    "https://brent.edu.ph/admissions/enrollment-process/",
                    "https://brent.edu.ph/admissions/admissions-criteria/"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": [
                    "https://brent.edu.ph/about/contact-us/"
                ]
            },
            {
                "name": "British School Manila",
                "link": "https://www.britishschoolmanila.org",
                "school_fee": "",
                "program": [
                    "https://www.britishschoolmanila.org/academics/the-key-stages"

                ],
                "Enrollment Process and Requirements": [
                    "https://www.britishschoolmanila.org/admissions/how-to-apply",

                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [
                    "https://www.britishschoolmanila.org/community/bsm-taguig-scholarship-programme"
                ],
                "Contact Information ": [
                    "https://www.britishschoolmanila.org/contact"
                ]
            },
            {
                "name": "German European School Manila (GESM)",
                "link": "https://gesm.org",
                "school_fee": "https://www.gesm.org/school-fees",
                "program": [
                    "https://www.gesm.org/curriculum",
                    "https://www.gesm.org/german-section",
                    "https://www.gesm.org/senior-years-programmes"
                ],
                "Enrollment Process and Requirements": [
                    "https://www.gesm.org/admission-process"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": [
                    "https://www.gesm.org/contact-us"
                ]
            },
            {
                "name": "Chinese International School Manila",
                "link": "https://www.cismanila.org",
                "school_fee": "https://cismanila.org/admissions/fee-structure",
                "program": [
                    "https://cismanila.org/learning/curriculum/"
                ],
                "Enrollment Process and Requirements": [
                    "https://cismanila.org/admissions/admissions-policy"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [
                    "https://cismanila.org/scholarships"
                ],
                "Contact Information ": [
                    "https://cismanila.org/contact-us"
                ]
            },
            {
                "name": "Reedley International School",
                "link": "https://reedleyschool.edu.ph",
                "school_fee": "",
                "program": [
                    "https://reedleyschool.edu.ph/acad-programs/",
                ],
                "Enrollment Process and Requirements": [
                    "https://reedleyschool.edu.ph/apply/#procedureId"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [
                    "https://reedleyschool.edu.ph/faq/"
                ],
                "Contact Information ": [
                    "https://reedleyschool.edu.ph/contact/"
                ]
            },
            {
                "name": "Southville International School and Colleges",
                "link": "https://www.southville.edu.ph",
                "school_fee": "",
                "program": [
                    "https://www.southville.edu.ph/preschool/",
                    "https://www.southville.edu.ph/elementary-school-programs/",
                    "https://www.southville.edu.ph/elementary-school-programs/",
                    "https://www.southville.edu.ph/international-baccalaureate-philippines/",
                    "https://www.southville.edu.ph/college-degree-programs-philippines/",
                    "https://www.southville.edu.ph/graduate-programs/",
                    "https://www.southville.edu.ph/online-programs/",
                    "https://www.southville.edu.ph/virtual-online-school/"
                ],
                "Enrollment Process and Requirements": [
                    "https://www.southville.edu.ph/admissions-basic-ed-requirements/",
                    "https://www.southville.edu.ph/college-admissions-requirements/",
                    "https://www.southville.edu.ph/online-summer-enrollment/",
                    "https://www.southville.edu.ph/online-enrollment-for-k-12-ib-new-students/",
                    "https://www.southville.edu.ph/online-enrollment-for-k-12-ib-continuing-students/",
                    "https://www.southville.edu.ph/online-enrollment-for-college-higher-education-new-students/",
                    "https://www.southville.edu.ph/online-enrollment-for-college-higher-education-continuing-students/",

                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [
                    "https://www.southville.edu.ph/college-scholarship/"
                ],
                "Contact Information ": [
                    "https://www.southville.edu.ph/contact-us/#contact-details"
                ]
            },
            {
                "name": "Singapore School Manila",
                "link": "https://www.singaporeschoolmanila.com",
                "school_fee": "https://singaporeschools.ph/admission/",
                "program": ["https://e9m.2af.myftpupload.com/admission/"],
                "Enrollment Process and Requirements": [
                    "https://singaporeschools.ph/admission/"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": [
                    "https://singaporeschools.ph/contact-us/"
                ]
            },
            {
                "name": "Faith Academy",
                "link": "https://faith.edu.ph",
                "school_fee": "https://faith.edu.ph/admissions/finances/",
                "program": [
                    "https://faith.edu.ph/school-life/"
                ],
                "Enrollment Process and Requirements": [
                    "https://faith.edu.ph/admissions/apply/"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": ["https://faith.edu.ph/contact/"]
            },
            {
                "name": "Victory Christian International School",
                "link": "https://www.victoryschool.edu.ph",
                "school_fee": "",
                "program": [
                    "https://vcis.edu.ph/index.php/our-programs/"
                ],
                "Enrollment Process and Requirements": [],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": [
                    "https://vcis.edu.ph/index.php/contact-us/"
                ]
            },
            {
                "name": "The Master's Academy",
                "link": "https://tmahomeschool.org",
                "school_fee": "",
                "program": [],
                "Enrollment Process and Requirements": [],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": []
            },
            {
                "name": "Jubilee Christian Academy",
                "link": "https://www.jca.edu.ph",
                "school_fee": "https://www.jca.edu.ph/admissions",
                "program": [],
                "Enrollment Process and Requirements": [
                    "https://www.jca.edu.ph/be-a-jubilean/admission/",
                    "https://www.jca.edu.ph/wp-content/uploads/2024/09/P-Admissions-Information.pdf",
                    "https://www.jca.edu.ph/wp-content/uploads/2024/09/E-ADMISSIONS-INFORMATION.pdf",
                    "https://www.jca.edu.ph/wp-content/uploads/2024/09/Junior-HS-ADMISSIONS-INFORMATION.pdf",
                    "https://www.jca.edu.ph/wp-content/uploads/2024/09/S-HS-ADMISSIONS-INFORMATION.pdf"
                ],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": [
                    "https://www.jca.edu.ph/contact-us/"
                ]
            },
            {
                "name": "The Learning Place International School",
                "link": "https://www.thelearningplace.edu.ph",
                "school_fee": "",
                "program": [],
                "Enrollment Process and Requirements": [],
                "Upcoming Events": [],
                "Discounts and Scholarship": [],
                "Contact Information ": []
            }
        ]