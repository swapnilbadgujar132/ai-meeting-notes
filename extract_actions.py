"""
EXTRACT_ACTIONS.PY
Multi-language action item and decision extraction
Supports: English, Hindi, Marathi, and code-mixing
"""

import spacy
import re
from langdetect import detect, DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0

class ActionExtractor:
    def __init__(self):
        """Initialize multi-language NLP models and keywords"""
        print("🔍 Loading NLP models...")
        
        # Load spaCy English model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("   ✅ spaCy model loaded")
        except:
            print("   ⚠️  Installing spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Multi-language action keywords
        self.action_keywords = {
            'en': [
                'complete', 'finish', 'implement', 'create', 'build',
                'design', 'develop', 'review', 'send', 'schedule',
                'prepare', 'update', 'fix', 'resolve', 'contact',
                'follow up', 'call', 'email', 'submit', 'approve',
                'check', 'verify', 'test', 'deploy', 'release',
                'analyze', 'investigate', 'coordinate', 'arrange'
            ],
            'hi': [
                'पूरा करना', 'खत्म करना', 'बनाना', 'तैयार करना',
                'भेजना', 'संपर्क करना', 'जांच करना', 'सुधारना',
                'देखना', 'करना', 'होना', 'लगाना', 'निकालना'
            ],
            'mr': [
                'पूर्ण करणे', 'संपवणे', 'तयार करणे', 'बनवणे',
                'पाठवणे', 'संपर्क करणे', 'तपासणे', 'सुधारणे',
                'पहाणे', 'करणे', 'होणे', 'देणे', 'घेणे', 'लावणे'
            ],
            'code_mix': [
                # Hinglish
                'complete karna', 'finish karna', 'banana', 'bhejana',
                'check karna', 'fix karna', 'update karna', 'call karna',
                'review karna', 'submit karna',
                # Marathi-English mix
                'complete karणे', 'finish karणे', 'send karणे',
                'fix karणे', 'update karणे', 'check karणे',
                'prepare karणे', 'review karणे'
            ]
        }
        
        # Decision keywords
        self.decision_keywords = {
            'en': [
                'decided', 'agreed', 'approved', 'confirmed',
                'concluded', 'resolved', 'finalized', 'accepted',
                'determined', 'settled'
            ],
            'hi': [
                'तय किया', 'सहमत हुए', 'स्वीकृत', 'पुष्टि की',
                'निर्णय लिया', 'मान लिया', 'फैसला किया'
            ],
            'mr': [
                'ठरवले', 'मान्य केले', 'स्वीकारले', 'निर्णय घेतला',
                'सहमत झालो', 'मंजूर केले', 'पुष्टी केली', 'ठरले'
            ],
            'code_mix': [
                'decide kiya', 'agree kiya', 'approve kiya',
                'decide केले', 'agree झालो', 'approve केले',
                'finalize kiya', 'confirm kiya'
            ]
        }
        
        # Priority keywords
        self.priority_keywords = {
            'urgent': {
                'en': ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'now'],
                'hi': ['तुरंत', 'जरूरी', 'अति आवश्यक', 'फौरन', 'अभी'],
                'mr': ['तात्काळ', 'त्वरित', 'आवश्यक', 'लगेच', 'आत्ताच']
            },
            'important': {
                'en': ['soon', 'important', 'priority', 'necessary', 'key'],
                'hi': ['जल्दी', 'महत्वपूर्ण', 'प्राथमिकता', 'जरूरी'],
                'mr': ['लवकर', 'महत्त्वाचे', 'प्राधान्य', 'आवश्यक']
            }
        }
        
        print("✅ Action extraction ready!")
        print("   Supported: English, Hindi, Marathi, Code-mixing")
    
    def extract_action_items(self, text, language="auto"):
        """
        Extract action items from text
        
        Parameters:
            text (str): Input text
            language (str): Language code or "auto"
            
        Returns:
            list: [{task, assignee, priority}, ...]
        """
        print(f"🎯 Extracting action items...")
        
        # Detect language if auto
        if language == "auto":
            try:
                language = detect(text[:500])  # Use first 500 chars for detection
            except:
                language = "en"
        
        print(f"   Language: {language}")
        
        # Combine relevant keywords
        action_verbs = self._get_action_keywords(language)
        
        # Process text with spaCy
        doc = self.nlp(text)
        actions = []
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_lower = sent_text.lower()
            
            # Check for action verbs
            for verb in action_verbs:
                if verb.lower() in sent_lower:
                    person = self._extract_person(sent)
                    priority = self._get_priority(sent_text, language)
                    
                    actions.append({
                        'task': sent_text,
                        'assignee': person,
                        'priority': priority
                    })
                    break  # One action per sentence
        
        print(f"✅ Found {len(actions)} action item(s)")
        return actions
    
    def extract_decisions(self, text, language="auto"):
        """
        Extract key decisions from text
        
        Parameters:
            text (str): Input text
            language (str): Language code or "auto"
            
        Returns:
            list: [decision1, decision2, ...]
        """
        print(f"💡 Extracting key decisions...")
        
        # Detect language
        if language == "auto":
            try:
                language = detect(text[:500])
            except:
                language = "en"
        
        # Get decision keywords
        decision_verbs = self._get_decision_keywords(language)
        
        # Process text
        doc = self.nlp(text)
        decisions = []
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_lower = sent_text.lower()
            
            # Check for decision keywords
            for keyword in decision_verbs:
                if keyword.lower() in sent_lower:
                    decisions.append(sent_text)
                    break
        
        print(f"✅ Found {len(decisions)} decision(s)")
        return decisions
    
    def _get_action_keywords(self, language):
        """Get action keywords based on language"""
        if language == "mr":
            return (
                self.action_keywords['mr'] +
                self.action_keywords['code_mix'] +
                self.action_keywords['en']
            )
        elif language == "hi":
            return (
                self.action_keywords['hi'] +
                self.action_keywords['code_mix'] +
                self.action_keywords['en']
            )
        else:
            return (
                self.action_keywords['en'] +
                self.action_keywords['code_mix']
            )
    
    def _get_decision_keywords(self, language):
        """Get decision keywords based on language"""
        if language == "mr":
            return (
                self.decision_keywords['mr'] +
                self.decision_keywords['code_mix'] +
                self.decision_keywords['en']
            )
        elif language == "hi":
            return (
                self.decision_keywords['hi'] +
                self.decision_keywords['code_mix'] +
                self.decision_keywords['en']
            )
        else:
            return (
                self.decision_keywords['en'] +
                self.decision_keywords['code_mix']
            )
    
    def _extract_person(self, sentence):
        """Extract person name from sentence"""
        # Try spaCy's named entity recognition
        for ent in sentence.ents:
            if ent.label_ == "PERSON":
                return ent.text
        
        # Fallback: Look for name patterns
        text = sentence.text
        
        # Pattern: Name + will/should/needs to/को/ला
        patterns = [
            r'\b([A-Z][a-z]+)\s+(will|should|needs to|must)\b',
            r'\b([A-Z][a-z]+)\s+(को|ला|ने)\b',
            r'\b([A-Z][a-z]+)\s+please\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "Team"
    
    def _get_priority(self, text, language):
        """Determine task priority"""
        text_lower = text.lower()
        
        # Collect all urgent keywords
        urgent_words = (
            self.priority_keywords['urgent']['en'] +
            self.priority_keywords['urgent']['hi'] +
            self.priority_keywords['urgent']['mr']
        )
        
        # Collect all important keywords
        important_words = (
            self.priority_keywords['important']['en'] +
            self.priority_keywords['important']['hi'] +
            self.priority_keywords['important']['mr']
        )
        
        # Check priority
        if any(word in text_lower for word in urgent_words):
            return "High"
        elif any(word in text_lower for word in important_words):
            return "Medium"
        else:
            return "Normal"


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ACTION EXTRACTION MODULE TEST")
    print("="*60 + "\n")
    
    extractor = ActionExtractor()
    
    # Test cases
    test_texts = [
        ("English", "Sarah will complete the dashboard redesign by Friday urgently."),
        ("Hindi", "राहुल को API issues तुरंत fix करने हैं।"),
        ("Marathi", "प्रशांत ला dashboard तात्काळ तयार करणे आहे।"),
        ("Code-mix", "Team ने decide kiya budget approve करना है next week."),
    ]
    
    for lang_name, text in test_texts:
        print(f"\n{'─'*60}")
        print(f"Testing: {lang_name}")
        print(f"Text: {text}")
        print(f"{'─'*60}")
        
        actions = extractor.extract_action_items(text)
        decisions = extractor.extract_decisions(text)
        
        if actions:
            for action in actions:
                print(f"   🎯 Action: {action['task'][:50]}...")
                print(f"      Assignee: {action['assignee']}")
                print(f"      Priority: {action['priority']}")
        
        if decisions:
            for decision in decisions:
                print(f"   💡 Decision: {decision[:50]}...")