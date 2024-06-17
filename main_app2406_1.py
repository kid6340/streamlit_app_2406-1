import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

#key設定
import os
GOOGLE_API_KEY = st.secrets['GOOGLE_API_KEY']['key']

#モデル設定
chat=ChatGoogleGenerativeAI(temperature=0,model="gemini-1.5-flash-latest")


#文書抽出_明細書
def googlepat_extract(paturl):
    if not paturl=="":
        r=requests.get(paturl)
        soup=BeautifulSoup(r.content,"html.parser")
        tags=soup.find_all('section',itemprop="description")
        document=tags[0].text
    else:document=""
    return document

#プロンプト設定
system="あなたは誠実で優秀な日本の技術者です。質問には必ず日本語で回答します。"
human="{text}"
prompt= ChatPromptTemplate.from_messages([("system",system),("human",human)])

def custom_prompt(context:str,input:str):
    augument_prompt=f"""
    {input}
    context:
    {context}
    """
    return augument_prompt

#chain設定
chain=prompt | chat

#サイドバー
with st.sidebar:
    with st.form(key='sub_form'):
        paturl=st.text_input(":blue[GooglePatentのリンクを入力]")
        st.markdown("https://patents.google.com/patent/WO2020170704A1")
        st.session_state["pat"]=googlepat_extract(paturl)
        st.form_submit_button(label='送信')
        
    if "pat" in st.session_state:
        document=st.session_state['pat']
        st.write('冒頭文:  \n', document[:200])
        # tokens=tokenizer.tokenize(document)
        # st.text(f'文献のトークン数:{len(tokens)}')
    else: st.write('冒頭文',[])

#メイン
st.title("情報抽出")
st.info('特許文献から情報を抽出')

with st.form("main_form"):
    input=st.text_area("LLMの入力文",height=200)
    submit_btn=st.form_submit_button("生成")
if submit_btn:
    with st.spinner("処理中..."):
        chunk=chain.invoke({"text":custom_prompt(context=document,input=input)})
    st.write(chunk.content)