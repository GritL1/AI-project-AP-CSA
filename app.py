import streamlit as st
import json
from analyzer import analyze_document

st.set_page_config(
    page_title="AI Document Analyzer",
    page_icon="📄",
    layout="centered"
)

st.title("📄 AI Document Analyzer")
st.markdown("""
Upload a **.txt file**, and the AI (DeepSeek) will analyze it to provide:
- Summary
- Sentiment analysis
- Key topics
- Action items

""")

uploaded_file = st.file_uploader("Choose a text file", type=["txt"])

if uploaded_file is not None:
    document_text = uploaded_file.read().decode("utf-8")
    
    with st.expander("📄 Document Preview"):
        st.write(document_text[:500] + ("..." if len(document_text) > 500 else ""))
    
    if st.button("🔍 Analyze with AI", type="primary"):
        with st.spinner("AI is analyzing the document... (DeepSeek API)"):
            analysis_result = analyze_document(document_text)
        
        try:
            if "```json" in analysis_result:
                json_str = analysis_result.split("```json")[1].split("```")[0]
            else:
                json_str = analysis_result
            
            data = json.loads(json_str)
            st.success("✅ Analysis complete!")
            
            st.subheader("📝 Summary")
            st.write(data.get("summary", "No summary available."))
            
            st.subheader("😊 Sentiment")
            sentiment = data.get("sentiment", "Unknown")
            if "positive" in sentiment.lower():
                st.success(sentiment)
            elif "negative" in sentiment.lower():
                st.error(sentiment)
            else:
                st.info(sentiment)
            
            st.subheader("🏷️ Key Topics")
            topics = data.get("key_topics", [])
            if topics:
                st.write(", ".join([f"`{topic}`" for topic in topics]))
            else:
                st.write("No key topics extracted.")
            
            st.subheader("✅ Action Items")
            actions = data.get("action_items", [])
            if actions and isinstance(actions, list):
                for action in actions:
                    st.markdown(f"- {action}")
            else:
                st.write(actions if actions else "No action items identified.")
        
        except json.JSONDecodeError:
            st.warning("Could not parse AI response as JSON. Showing raw output:")
            st.code(analysis_result)
        
        st.download_button(
            label="📥 Download Analysis as JSON",
            data=analysis_result,
            file_name="analysis_result.json",
            mime="application/json"
        )
else:
    st.info("📂 Please upload a .txt file to begin.")