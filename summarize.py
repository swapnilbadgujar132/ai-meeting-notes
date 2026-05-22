"""
SUMMARIZE.PY
Multi-language text summarization
Supports: English, Hindi, Marathi, and 45+ languages
"""

from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class MeetingSummarizer:
    def __init__(self):
        """Initialize multi-language summarization models"""
        print("🤖 Loading summarization models...")
        print("   This may take a minute on first run...")
        
        # English summarizer (best quality)
        try:
            self.en_summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # Use CPU
            )
            print("   ✅ English model loaded")
        except Exception as e:
            print(f"   ⚠️  English model error: {e}")
            self.en_summarizer = None
        
        # Multilingual summarizer (Hindi, Marathi, 45+ languages)
        try:
            self.multilingual_summarizer = pipeline(
                "summarization",
                model="csebuetnlp/mT5_multilingual_XLSum",
                device=-1  # Use CPU
            )
            print("   ✅ Multilingual model loaded")
        except Exception as e:
            print(f"   ⚠️  Multilingual model error: {e}")
            self.multilingual_summarizer = None
        
        print("✅ Summarization ready!")
    
    def summarize_text(self, text, language="en", max_length=150, min_length=50):
        """
        Summarize text in multiple languages
        
        Parameters:
            text (str): Input text to summarize
            language (str): Language code ("en", "hi", "mr", etc.)
            max_length (int): Maximum summary length
            min_length (int): Minimum summary length
            
        Returns:
            str: Summarized text
        """
        
        # If text is too short, return as is
        word_count = len(text.split())
        if word_count < 50:
            print("   ⚠️  Text too short to summarize, returning original")
            return text
        
        print(f"📊 Generating summary...")
        print(f"   Language: {language}")
        print(f"   Input length: {word_count} words")
        
        # Choose appropriate model
        if language == "en" and self.en_summarizer:
            summarizer = self.en_summarizer
            print("   Using: English model")
        elif self.multilingual_summarizer:
            summarizer = self.multilingual_summarizer
            print("   Using: Multilingual model")
        else:
            print("   ⚠️  No model available, returning first 200 chars")
            return text[:200] + "..."
        
        # Split text into chunks if too long
        chunks = self._split_text(text, chunk_size=1000)
        print(f"   Processing {len(chunks)} chunk(s)...")
        
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}/{len(chunks)}...", end=" ")
            
            try:
                summary = summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])
                print("✅")
            except Exception as e:
                print(f"⚠️  Error: {str(e)[:50]}")
                # Fallback: use first 200 characters
                summaries.append(chunk[:200] + "...")
        
        final_summary = " ".join(summaries)
        print(f"✅ Summary generated! ({len(final_summary.split())} words)")
        
        return final_summary
    
    def _split_text(self, text, chunk_size=1000):
        """Split long text into manageable chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("SUMMARIZE MODULE TEST")
    print("="*60 + "\n")
    
    summarizer = MeetingSummarizer()
    
    # Test text (English)
    sample_text = """
    In today's quarterly team meeting, we discussed several critical items 
    for the upcoming product launch. Sarah presented the new dashboard design, 
    which received positive feedback from the team. The development team, 
    led by John, committed to completing the API integration by the end of 
    this week. We identified some performance issues that need immediate 
    attention, particularly around database query optimization. The marketing 
    team will begin the campaign rollout next Monday, pending final approval 
    from management. Budget allocation for the next quarter was also discussed, 
    with a focus on hiring two additional developers. Action items were 
    assigned to respective team members with clear deadlines.
    """
    
    print("\n📝 Original Text:")
    print("-" * 60)
    print(sample_text.strip())
    print("-" * 60)
    
    summary = summarizer.summarize_text(sample_text, language="en")
    
    print("\n📄 Summary:")
    print("-" * 60)
    print(summary)
    print("-" * 60)