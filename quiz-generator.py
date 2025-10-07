import streamlit as st
import re
import random

def extract_key_concepts(text):
    """Extract key sentences and concepts from the text"""
    # Clean and split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Extract words (potential key terms)
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b|\b\w{5,}\b', text)
    key_terms = list(set([w for w in words if len(w) > 4]))[:10]
    
    return sentences, key_terms

def generate_assignments(sentences, key_terms, topic):
    """Generate 2 assignment questions"""
    assignments = []
    
    if sentences:
        # Assignment 1: Analysis/Explanation
        assignments.append(
            f"Explain the main concepts presented in the text about {topic}. "
            f"Support your answer with specific examples and reasoning. (300-500 words)"
        )
        
        # Assignment 2: Critical thinking
        if key_terms:
            term = random.choice(key_terms[:3]) if len(key_terms) >= 3 else (key_terms[0] if key_terms else topic)
            assignments.append(
                f"Discuss the significance of '{term}' in the context of {topic}. "
                f"How does this concept relate to real-world applications? (250-400 words)"
            )
        else:
            assignments.append(
                f"Compare and contrast different perspectives or approaches discussed regarding {topic}. "
                f"Provide your own critical analysis. (300-500 words)"
            )
    else:
        # Fallback assignments
        assignments = [
            f"Write an essay exploring the key aspects of {topic}. Include examples and analysis. (300-500 words)",
            f"Critically evaluate the importance of {topic} in modern context. (250-400 words)"
        ]
    
    return assignments

def generate_quiz_questions(sentences, key_terms, topic):
    """Generate 3 multiple-choice quiz questions"""
    questions = []
    
    # Question 1: Definition/Concept-based
    if key_terms and len(key_terms) >= 4:
        correct = key_terms[0]
        options = [correct] + random.sample(key_terms[1:], min(3, len(key_terms)-1))
        if len(options) < 4:
            options += ["None of the above", "All of the above"][:4-len(options)]
        random.shuffle(options)
        
        questions.append({
            "question": f"Which of the following is a key concept related to {topic}?",
            "options": options,
            "answer": correct
        })
    else:
        questions.append({
            "question": f"What is the primary focus when studying {topic}?",
            "options": [
                f"Understanding core principles of {topic}",
                "Memorizing dates only",
                "Ignoring practical applications",
                "Avoiding critical analysis"
            ],
            "answer": f"Understanding core principles of {topic}"
        })
    
    # Question 2: Comprehension-based
    if sentences and len(sentences) >= 2:
        questions.append({
            "question": f"Based on the provided content, which statement best describes {topic}?",
            "options": [
                f"{sentences[0][:80]}..." if len(sentences[0]) > 80 else sentences[0],
                "This topic has no practical relevance",
                "It contradicts all established theories",
                "It requires no further study"
            ],
            "answer": f"{sentences[0][:80]}..." if len(sentences[0]) > 80 else sentences[0]
        })
    else:
        questions.append({
            "question": f"What is an important aspect of {topic}?",
            "options": [
                f"Analyzing and understanding {topic} concepts",
                "Ignoring foundational principles",
                "Only memorizing terminology",
                "Dismissing real-world applications"
            ],
            "answer": f"Analyzing and understanding {topic} concepts"
        })
    
    # Question 3: Application/Analysis
    if key_terms:
        term = key_terms[0] if len(key_terms) > 0 else topic
        questions.append({
            "question": f"How might understanding '{term}' be applied practically?",
            "options": [
                f"By applying {term} principles to solve real problems",
                "By ignoring its relevance completely",
                "By memorizing it without context",
                "By avoiding its implementation"
            ],
            "answer": f"By applying {term} principles to solve real problems"
        })
    else:
        questions.append({
            "question": f"Why is {topic} considered important?",
            "options": [
                f"It provides insights and practical knowledge about {topic}",
                "It has no significance",
                "It contradicts common sense",
                "It should be ignored"
            ],
            "answer": f"It provides insights and practical knowledge about {topic}"
        })
    
    return questions

# Streamlit UI
st.title("📚 Assignment & Quiz Generator")
st.write("Generate assignments and quizzes from any document or topic!")

# Input section
st.subheader("Input Your Content")
topic = st.text_input("Topic/Title:", placeholder="e.g., Photosynthesis, Machine Learning, World War II")
document_text = st.text_area(
    "Paste your document text here (optional):",
    height=200,
    placeholder="Paste educational content here to generate more specific questions..."
)

if st.button("🎯 Generate Questions", type="primary"):
    if not topic:
        st.error("Please enter a topic!")
    else:
        with st.spinner("Generating assignments and quizzes..."):
            # Process input
            sentences, key_terms = extract_key_concepts(document_text) if document_text else ([], [])
            
            # Generate content
            assignments = generate_assignments(sentences, key_terms, topic)
            quiz_questions = generate_quiz_questions(sentences, key_terms, topic)
            
            # Display Assignments
            st.success("✅ Generated Successfully!")
            st.header("📝 Assignment Questions")
            for i, assignment in enumerate(assignments, 1):
                st.subheader(f"Assignment {i}")
                st.write(assignment)
                st.divider()
            
            # Display Quiz
            st.header("❓ Multiple Choice Quiz")
            for i, q in enumerate(quiz_questions, 1):
                st.subheader(f"Question {i}")
                st.write(q["question"])
                
                for j, option in enumerate(q["options"], 1):
                    st.write(f"{chr(64+j)}. {option}")
                
                with st.expander("Show Answer"):
                    st.success(f"✓ Correct Answer: {q['answer']}")
                
                st.divider()

# Footer
st.markdown("---")
st.caption("💡 Tip: Provide more detailed text for better, more specific questions!")