import streamlit as st
from main import NewsDataUnstructured

def main():
    st.title("Financial News Sentiment Analyzer")
    ticker = st.text_input("Enter the ticker Symbol to get the sentiment score for it:")
    
    if ticker:
        data = NewsDataUnstructured(ticker)
        df = data.get_sentiment()

        st.subheader("Sentiment Analysis Results:")
        st.dataframe(df)

if __name__ == "__main__":
    main()
