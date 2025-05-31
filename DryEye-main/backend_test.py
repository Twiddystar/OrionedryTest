
import requests
import sys
import json
from datetime import datetime

class DryEyeQuestionnaireAPITester:
    def __init__(self, base_url="https://d4915dc0-7d26-49e0-887b-6260af997345.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json() if response.text else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            print(f"Health check response: {response}")
        return success

    def test_get_questionnaire_info(self):
        """Test getting questionnaire info"""
        success, response = self.run_test(
            "Get Questionnaire Info",
            "GET",
            "api/questionnaire/info",
            200
        )
        if success:
            print(f"Questionnaire info: {json.dumps(response, indent=2)}")
        return success

    def test_get_questions(self):
        """Test getting questionnaire questions"""
        success, response = self.run_test(
            "Get Questionnaire Questions",
            "GET",
            "api/questionnaire/questions",
            200
        )
        if success:
            print(f"Number of sections: {len(response.get('sections', []))}")
            total_questions = sum(len(section.get('questions', [])) for section in response.get('sections', []))
            print(f"Total questions: {total_questions}")
        return success

    def test_submit_evaporative_type(self):
        """Test submitting answers for evaporative dry eye type"""
        # Prepare answers for evaporative type (high scores on Q2,3,5,7,14,19)
        answers = {str(i): "0" for i in range(1, 21)}  # Initialize all with 0
        
        # Set high scores for evaporative questions
        answers["2"] = "4"  # bruciore
        answers["3"] = "4"  # sabbia
        answers["5"] = "4"  # vista offuscata
        answers["7"] = "4"  # sera/computer
        answers["14"] = "si"  # impacchi caldi
        answers["19"] = "si"  # ghiandole Meibomio
        
        # Set other yes/no questions to "no"
        for i in range(8, 21):
            if str(i) not in ["14", "19"]:
                answers[str(i)] = "no"
        
        data = {
            "answers": answers,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Submit Evaporative Type",
            "POST",
            "api/questionnaire/submit",
            200,
            data=data
        )
        
        if success:
            print(f"Classification result: {response.get('type')}")
            print(f"Scores: {json.dumps(response.get('scores'), indent=2)}")
            if "Evaporativo" in response.get('type', ''):
                print("✅ Correctly classified as Evaporative type")
                return True
            else:
                print("❌ Failed to classify as Evaporative type")
                return False
        return False

    def test_submit_aqueous_deficit_type(self):
        """Test submitting answers for aqueous deficit dry eye type"""
        # Prepare answers for aqueous deficit type (high scores on Q1,6,15,16,11,18)
        answers = {str(i): "0" for i in range(1, 21)}  # Initialize all with 0
        
        # Set high scores for aqueous deficit questions
        answers["1"] = "4"  # secchezza
        answers["6"] = "4"  # lacrimazione
        answers["11"] = "si"  # autoimmuni
        answers["15"] = "si"  # risveglio
        answers["16"] = "si"  # gel viscosi
        answers["18"] = "si"  # Schirmer
        
        # Set other yes/no questions to "no"
        for i in range(8, 21):
            if str(i) not in ["11", "15", "16", "18"]:
                answers[str(i)] = "no"
        
        data = {
            "answers": answers,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Submit Aqueous Deficit Type",
            "POST",
            "api/questionnaire/submit",
            200,
            data=data
        )
        
        if success:
            print(f"Classification result: {response.get('type')}")
            print(f"Scores: {json.dumps(response.get('scores'), indent=2)}")
            if "Deficit Acquoso" in response.get('type', ''):
                print("✅ Correctly classified as Aqueous Deficit type")
                return True
            else:
                print("❌ Failed to classify as Aqueous Deficit type")
                return False
        return False

    def test_submit_neuropathic_type(self):
        """Test submitting answers for neuropathic dry eye type"""
        # Prepare answers for neuropathic type (Q20='si' + high total symptoms (≥15))
        answers = {str(i): "0" for i in range(1, 21)}  # Initialize all with 0
        
        # Set high scores for symptoms (Q1-7)
        for i in range(1, 8):
            answers[str(i)] = "3"  # Set all symptoms to high (total = 21)
        
        # Set Q20 to "si" (neuropathic indicator)
        answers["20"] = "si"
        
        # Set other yes/no questions to "no"
        for i in range(8, 20):
            answers[str(i)] = "no"
        
        data = {
            "answers": answers,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Submit Neuropathic Type",
            "POST",
            "api/questionnaire/submit",
            200,
            data=data
        )
        
        if success:
            print(f"Classification result: {response.get('type')}")
            print(f"Scores: {json.dumps(response.get('scores'), indent=2)}")
            if "Neuropatico" in response.get('type', ''):
                print("✅ Correctly classified as Neuropathic type")
                return True
            else:
                print("❌ Failed to classify as Neuropathic type")
                return False
        return False

    def test_submit_mixed_type(self):
        """Test submitting answers for mixed dry eye type"""
        # Prepare answers for mixed type (high scores in both evaporative and aqueous categories)
        answers = {str(i): "0" for i in range(1, 21)}  # Initialize all with 0
        
        # Set high scores for evaporative questions
        answers["2"] = "4"  # bruciore
        answers["3"] = "4"  # sabbia
        answers["5"] = "4"  # vista offuscata
        answers["7"] = "4"  # sera/computer
        answers["14"] = "si"  # impacchi caldi
        answers["19"] = "si"  # ghiandole Meibomio
        
        # Set high scores for aqueous deficit questions
        answers["1"] = "4"  # secchezza
        answers["6"] = "4"  # lacrimazione
        answers["11"] = "si"  # autoimmuni
        answers["15"] = "si"  # risveglio
        answers["16"] = "si"  # gel viscosi
        answers["18"] = "si"  # Schirmer
        
        # Set other yes/no questions to "no"
        for i in range(8, 21):
            if str(i) not in ["11", "14", "15", "16", "18", "19"]:
                answers[str(i)] = "no"
        
        data = {
            "answers": answers,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Submit Mixed Type",
            "POST",
            "api/questionnaire/submit",
            200,
            data=data
        )
        
        if success:
            print(f"Classification result: {response.get('type')}")
            print(f"Scores: {json.dumps(response.get('scores'), indent=2)}")
            if "Misto" in response.get('type', ''):
                print("✅ Correctly classified as Mixed type")
                return True
            else:
                print("❌ Failed to classify as Mixed type")
                return False
        return False

    def test_incomplete_submission(self):
        """Test submitting incomplete answers"""
        # Prepare incomplete answers (only 10 questions)
        answers = {str(i): "0" for i in range(1, 11)}
        
        data = {
            "answers": answers,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Submit Incomplete Questionnaire",
            "POST",
            "api/questionnaire/submit",
            400,  # Expecting 400 Bad Request
            data=data
        )
        
        return success

def main():
    # Setup
    tester = DryEyeQuestionnaireAPITester()
    
    # Run tests
    print("\n===== TESTING DRY EYE QUESTIONNAIRE API =====\n")
    
    # Test basic endpoints
    tester.test_health_check()
    tester.test_get_questionnaire_info()
    tester.test_get_questions()
    
    # Test classification algorithm with different answer patterns
    tester.test_submit_evaporative_type()
    tester.test_submit_aqueous_deficit_type()
    tester.test_submit_neuropathic_type()
    tester.test_submit_mixed_type()
    
    # Test validation
    tester.test_incomplete_submission()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
      